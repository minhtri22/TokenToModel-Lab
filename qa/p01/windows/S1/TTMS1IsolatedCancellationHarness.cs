// TTM P01 L1 / S1 isolated cancellation harness. SOURCE ONLY; not executed.
// Standalone local process, never TTMP01Broker, no SCM, no worker credentials.
// One-shot future native run requires an independently issued S1 permit.
using System;
using System.IO;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Principal;
using Microsoft.Win32.SafeHandles;

namespace TTMP01S1 {
  internal static class IsolatedCancellationHarness {
    const string UniquePipePrefix = "TTM_P01_S1_ISOLATED_";
    const int ConnectTimeoutMs = 1500;
    const int CompletionTimeoutMs = 4000;
    const int ErrorOperationAborted = 995;
    const int ErrorNotFound = 1168;

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CancelIoEx(SafePipeHandle handle, IntPtr overlapped);

    delegate void Complete(IAsyncResult pending);
    internal sealed class Outcome {
      internal readonly string Name;
      internal readonly string Status;
      internal Outcome(string name, string status) { Name = name; Status = status; }
      internal bool Passed { get { return Status == "PASS_COMPLETED_ABORTED"; } }
    }

    static string NewUniqueName() {
      return UniquePipePrefix + Guid.NewGuid().ToString("N");
    }

    // The current user's SID is the only intended non-SYSTEM participant.
    // Never use the service pipe name or a configurable user-supplied pipe name.
    static NamedPipeServerStream NewServer(string name) {
      WindowsIdentity identity = WindowsIdentity.GetCurrent();
      try {
        if (identity.User == null) throw new InvalidOperationException("S1_NO_USER_SID");
        PipeSecurity security = new PipeSecurity();
        security.SetAccessRuleProtection(true, false);
        security.AddAccessRule(new PipeAccessRule(
          identity.User, PipeAccessRights.FullControl, AccessControlType.Allow));
        return new NamedPipeServerStream(
          name, PipeDirection.InOut, 1, PipeTransmissionMode.Byte,
          PipeOptions.Asynchronous, 512, 512, security);
      } finally { identity.Dispose(); }
    }

    static Outcome CancelAndObserve(string label, NamedPipeServerStream server,
                                    IAsyncResult pending, Complete end) {
      if (pending == null || pending.IsCompleted)
        return new Outcome(label, "BLOCK_NOT_PENDING_BEFORE_CANCEL");

      // CancelIoEx merely requests cancellation; it does NOT wait for completion.
      bool submitted = CancelIoEx(server.SafePipeHandle, IntPtr.Zero);
      int error = submitted ? 0 : Marshal.GetLastWin32Error();
      if (!submitted && error != ErrorNotFound)
        return new Outcome(label, "BLOCK_CANCEL_REQUEST_" + error.ToString());

      // Do not call End* or dispose the pipe while the request is still pending.
      if (!pending.AsyncWaitHandle.WaitOne(CompletionTimeoutMs))
        return new Outcome(label, "BLOCK_CANCEL_COMPLETION_TIMEOUT");

      try {
        // Exactly one End* call after the asynchronous operation completes.
        end(pending);
        return new Outcome(label, "BLOCK_END_COMPLETED_NORMALLY");
      } catch (IOException io) {
        int win32 = io.HResult & 0xffff;
        return new Outcome(label, win32 == ErrorOperationAborted
          ? "PASS_COMPLETED_ABORTED"
          : "BLOCK_END_IO_" + win32.ToString());
      } catch (ObjectDisposedException) {
        return new Outcome(label, "BLOCK_HANDLE_DISPOSED_EARLY");
      } catch (Exception ex) {
        return new Outcome(label, "BLOCK_END_" + ex.GetType().Name);
      }
    }

    static Outcome IdleAccept() {
      string name = NewUniqueName();
      NamedPipeServerStream server = null;
      IAsyncResult pending = null;
      try {
        server = NewServer(name);
        pending = server.BeginWaitForConnection(null, null);
        return CancelAndObserve("IDLE_ACCEPT", server, pending,
          delegate(IAsyncResult ar) { server.EndWaitForConnection(ar); });
      } catch (Exception ex) {
        return new Outcome("IDLE_ACCEPT", "BLOCK_SETUP_" + ex.GetType().Name);
      } finally {
        // If still pending, leave handle to process teardown; never free live OVERLAPPED.
        if (server != null && (pending == null || pending.IsCompleted)) server.Dispose();
      }
    }

    static Outcome SilentClientRead() {
      string name = NewUniqueName();
      NamedPipeServerStream server = null;
      NamedPipeClientStream client = null;
      IAsyncResult accept = null;
      IAsyncResult read = null;
      try {
        server = NewServer(name);
        accept = server.BeginWaitForConnection(null, null);
        client = new NamedPipeClientStream(
          ".", name, PipeDirection.InOut, PipeOptions.Asynchronous);
        client.Connect(ConnectTimeoutMs);
        if (!accept.AsyncWaitHandle.WaitOne(ConnectTimeoutMs))
          return new Outcome("SILENT_READ", "BLOCK_CONNECT_COMPLETION_TIMEOUT");
        server.EndWaitForConnection(accept);
        // Keep client connected and silent while the server waits for bytes.
        byte[] buffer = new byte[16];
        read = server.BeginRead(buffer, 0, buffer.Length, null, null);
        return CancelAndObserve("SILENT_READ", server, read,
          delegate(IAsyncResult ar) { server.EndRead(ar); });
      } catch (Exception ex) {
        return new Outcome("SILENT_READ", "BLOCK_SETUP_" + ex.GetType().Name);
      } finally {
        // No cleanup before a pending async call has completed.
        bool acceptComplete = accept == null || accept.IsCompleted;
        bool readComplete = read == null || read.IsCompleted;
        if (acceptComplete && readComplete) {
          if (client != null) client.Dispose();
          if (server != null) server.Dispose();
        }
      }
    }

    public static int Main(string[] args) {
      if (args.Length != 0) {
        Console.WriteLine("TTM_S1_VERDICT=BLOCK_ARGUMENTS_FORBIDDEN");
        return 3;
      }
      if (Environment.OSVersion.Platform != PlatformID.Win32NT) {
        Console.WriteLine("TTM_S1_VERDICT=BLOCK_WINDOWS_REQUIRED");
        return 3;
      }
      Outcome idle = IdleAccept();
      Console.WriteLine("TTM_S1_" + idle.Name + "=" + idle.Status);
      if (!idle.Passed) {
        Console.WriteLine("TTM_S1_VERDICT=BLOCK_ISOLATED_CANCELLATION");
        return 3;
      }
      Outcome silent = SilentClientRead();
      Console.WriteLine("TTM_S1_" + silent.Name + "=" + silent.Status);
      Console.WriteLine("TTM_S1_VERDICT=" +
        (silent.Passed ? "PASS_ISOLATED_CANCELLATION_ONLY" : "BLOCK_ISOLATED_CANCELLATION"));
      return silent.Passed ? 0 : 3;
    }
  }
}
