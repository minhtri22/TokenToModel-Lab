// TTM P01 L1 Broker V3 -- source-only successor to V2.
// Native Windows / .NET Framework 4.x, security attestation ONLY.
// This service never writes an evidence record; all non-probe requests are denied.
// Original V1/V2 code and frozen P00/F0 remain untouched.
using System;
using System.IO;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Principal;
using System.ServiceProcess;
using System.Text;
using System.Threading;
using Microsoft.Win32.SafeHandles;

namespace TTMP01 {
  public sealed class BrokerAttestationServiceV3 : ServiceBase {
    const string Service = "TTMP01Broker";
    const string PipeName = "TTM_P01_L1_BROKER_V1";
    const int StopJoinMilliseconds = 8000;
    const int ErrorNotFound = 1168; // CancelIoEx: no outstanding matching I/O
    readonly object lifecycleLock = new object();
    ManualResetEvent stopSignal;
    Thread serviceThread;
    volatile bool stopping;
    string workerSid;
    string serviceSid;

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CancelIoEx(SafePipeHandle handle, IntPtr overlapped);

    public BrokerAttestationServiceV3() {
      ServiceName = Service;
      CanStop = true;
      AutoLog = false;
    }

    static bool TokenHasGroup(string expected) {
      using (WindowsIdentity identity = WindowsIdentity.GetCurrent()) {
        foreach (IdentityReference group in identity.Groups) {
          try {
            if (group.Translate(typeof(SecurityIdentifier)).Value == expected)
              return true;
          } catch (IdentityNotMappedException) { }
        }
      }
      return false;
    }

    static PipeSecurity StrictPipeDacl(string service, string worker) {
      PipeSecurity acl = new PipeSecurity();
      acl.SetAccessRuleProtection(true, false);
      acl.AddAccessRule(new PipeAccessRule(
        new SecurityIdentifier("S-1-5-18"),
        PipeAccessRights.FullControl, AccessControlType.Allow));
      acl.AddAccessRule(new PipeAccessRule(
        new SecurityIdentifier(service),
        PipeAccessRights.FullControl, AccessControlType.Allow));
      // Deliberately no CreateNewInstance, ChangePermissions or TakeOwnership.
      acl.AddAccessRule(new PipeAccessRule(
        new SecurityIdentifier(worker),
        PipeAccessRights.ReadWrite, AccessControlType.Allow));
      return acl;
    }

    protected override void OnStart(string[] args) {
      using (WindowsIdentity identity = WindowsIdentity.GetCurrent()) {
        if (identity.User == null || identity.User.Value != "S-1-5-19")
          throw new InvalidOperationException("LOCAL_SERVICE_IDENTITY_REQUIRED");
      }
      string cfg = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "broker_sids.txt");
      string[] lines = File.ReadAllLines(cfg);
      if (lines.Length != 2 || !lines[0].StartsWith("service=") ||
          !lines[1].StartsWith("worker="))
        throw new InvalidOperationException("PINNED_SID_CONFIGURATION_REQUIRED");
      string expectedService = lines[0].Substring(8).Trim();
      string expectedWorker = lines[1].Substring(7).Trim();
      if (!expectedService.StartsWith("S-1-5-80-") ||
          !expectedWorker.StartsWith("S-1-5-21-") ||
          expectedService == expectedWorker || !TokenHasGroup(expectedService))
        throw new InvalidOperationException("SERVICE_WORKER_SID_ATTESTATION_FAILED");

      lock (lifecycleLock) {
        if (serviceThread != null || stopSignal != null)
          throw new InvalidOperationException("SERVICE_LIFECYCLE_RESTART_REFUSED");
        serviceSid = expectedService;
        workerSid = expectedWorker;
        stopping = false;
        stopSignal = new ManualResetEvent(false);
        serviceThread = new Thread(Serve);
        serviceThread.IsBackground = true;
        serviceThread.Start();
      }
    }

    // Called on the service thread only; OnStop never disposes its pipe.
    // Windows OVERLAPPED request is cancelled by the owning service thread.
    bool WaitOrCancel(NamedPipeServerStream pipe, IAsyncResult pending) {
      WaitHandle[] wait = new WaitHandle[] { stopSignal, pending.AsyncWaitHandle };
      int result = WaitHandle.WaitAny(wait);
      if (result == 0) {
        if (!CancelIoEx(pipe.SafePipeHandle, IntPtr.Zero)) {
          int error = Marshal.GetLastWin32Error();
          // ERROR_NOT_FOUND can race with successful async completion.
          if (error != ErrorNotFound)
            throw new IOException("CANCEL_IO_EX_FAILED_" + error.ToString());
        }
        return false;
      }
      if (result != 1)
        throw new InvalidOperationException("UNEXPECTED_PIPE_WAIT_RESULT");
      return !stopping;
    }

    bool Accept(NamedPipeServerStream pipe) {
      IAsyncResult pending = pipe.BeginWaitForConnection(null, null);
      bool ready = false;
      try {
        ready = WaitOrCancel(pipe, pending);
      } finally {
        // Required exactly once for every successful BeginWaitForConnection.
        try { pipe.EndWaitForConnection(pending); }
        catch (IOException) { if (!stopping) throw; }
        catch (ObjectDisposedException) { if (!stopping) throw; }
      }
      return ready && !stopping && pipe.IsConnected;
    }

    int ReadRequest(NamedPipeServerStream pipe, byte[] buffer) {
      IAsyncResult pending = pipe.BeginRead(buffer, 0, buffer.Length, null, null);
      bool ready = false;
      int bytes = 0;
      try {
        ready = WaitOrCancel(pipe, pending);
      } finally {
        // Required exactly once for a BeginRead request, including cancellation.
        try { bytes = pipe.EndRead(pending); }
        catch (IOException) { if (!stopping) throw; }
        catch (ObjectDisposedException) { if (!stopping) throw; }
      }
      return ready && !stopping ? bytes : 0;
    }

    bool WriteReply(NamedPipeServerStream pipe, byte[] response) {
      IAsyncResult pending = pipe.BeginWrite(response, 0, response.Length, null, null);
      bool ready = false;
      try {
        ready = WaitOrCancel(pipe, pending);
      } finally {
        // Required exactly once for a BeginWrite request, including cancellation.
        try { pipe.EndWrite(pending); }
        catch (IOException) { if (!stopping) throw; }
        catch (ObjectDisposedException) { if (!stopping) throw; }
      }
      return ready && !stopping;
    }

    void Serve() {
      // Only this thread creates and closes pipe instances. No unsynchronized
      // "active" reference is shared with the SCM service-control thread.
      while (!stopping) {
        try {
          PipeSecurity acl = StrictPipeDacl(serviceSid, workerSid);
          using (NamedPipeServerStream pipe = new NamedPipeServerStream(
                   PipeName, PipeDirection.InOut, 1,
                   PipeTransmissionMode.Byte, PipeOptions.Asynchronous,
                   4096, 4096, acl)) {
            if (!Accept(pipe)) continue;
            byte[] input = new byte[64];
            int n = ReadRequest(pipe, input);
            if (n <= 0 || stopping) continue;
            string request = Encoding.ASCII.GetString(input, 0, n);
            string peer = null;
            // The incoming read is complete before client impersonation.
            pipe.RunAsClient(delegate {
              using (WindowsIdentity identity = WindowsIdentity.GetCurrent()) {
                peer = identity.User == null ? null : identity.User.Value;
              }
            });
            byte[] reply;
            if (peer != workerSid) {
              reply = Encoding.ASCII.GetBytes("DENY_PEER_SID\n");
            } else {
              reply = Encoding.ASCII.GetBytes(
                request == "AUTH_PROBE\n" ?
                  "AUTH_PEER_OK_NO_WRITE\n" : "DENY_UNSUPPORTED_OPERATION\n");
            }
            WriteReply(pipe, reply);
          }
        } catch (IOException) {
          if (stopping) break;
          SignalFatalFailure();
        } catch (ObjectDisposedException) {
          if (stopping) break;
          SignalFatalFailure();
        } catch (Exception) {
          // Security failure must never downgrade to default-DACL listener.
          SignalFatalFailure();
        }
      }
    }

    void SignalFatalFailure() {
      stopping = true;
      if (stopSignal != null) stopSignal.Set();
    }

    protected override void OnStop() {
      Thread thread;
      ManualResetEvent signal;
      lock (lifecycleLock) {
        stopping = true;
        signal = stopSignal;
        thread = serviceThread;
        if (signal != null) signal.Set();
      }
      if (thread != null && !thread.Join(StopJoinMilliseconds))
        throw new InvalidOperationException("BROKER_V3_SERVER_THREAD_STOP_TIMEOUT");
      lock (lifecycleLock) {
        serviceThread = null;
        stopSignal = null;
      }
      if (signal != null) signal.Dispose();
    }

    public static void Main() {
      ServiceBase.Run(new BrokerAttestationServiceV3());
    }
  }
}
