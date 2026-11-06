// TTM P01 L1 Broker transport attestation service.
// WINDOWS-NATIVE SECURITY QA ONLY. It refuses every WRITE command.
// No F0, GPT training, broker evidence writes, or L1 grouped QA.
using System;
using System.IO;
using System.IO.Pipes;
using System.Security.AccessControl;
using System.Security.Principal;
using System.ServiceProcess;
using System.Text;
using System.Threading;

namespace TTMP01 {
  public sealed class BrokerAttestationService : ServiceBase {
    const string Service = "TTMP01Broker";
    const string PipeName = "TTM_P01_L1_BROKER_V1";
    const string ServiceSidPrefix = "S-1-5-80-";
    volatile bool stopping;
    Thread serverThread;
    NamedPipeServerStream active;
    string workerSid;
    string serviceSid;

    public BrokerAttestationService() {
      ServiceName = Service;
      CanStop = true;
      AutoLog = false;
    }

    static bool InTokenGroups(string expected) {
      using (var token = WindowsIdentity.GetCurrent()) {
        foreach (IdentityReference s in token.Groups) {
          try {
            if (s.Translate(typeof(SecurityIdentifier)).Value == expected)
              return true;
          } catch (IdentityNotMappedException) {}
        }
      }
      return false;
    }

    protected override void OnStart(string[] args) {
      try {
        // LocalService user SID; service SID must also appear in token groups.
        using (var token = WindowsIdentity.GetCurrent()) {
          if (token.User.Value != "S-1-5-19")
            throw new InvalidOperationException("LOCAL_SERVICE_IDENTITY_REQUIRED");
        }
        string cfg = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "broker_sids.txt");
        string[] lines = File.ReadAllLines(cfg);
        if (lines.Length != 2 || !lines[0].StartsWith("service=") ||
            !lines[1].StartsWith("worker="))
          throw new InvalidOperationException("PINNED_SID_CONFIGURATION_REQUIRED");
        serviceSid = lines[0].Substring(8).Trim();
        workerSid = lines[1].Substring(7).Trim();
        if (!serviceSid.StartsWith(ServiceSidPrefix) || serviceSid == workerSid ||
            !workerSid.StartsWith("S-1-5-21-") || !InTokenGroups(serviceSid))
          throw new InvalidOperationException("SERVICE_WORKER_SID_ATTESTATION_FAILED");
        stopping = false;
        serverThread = new Thread(Serve);
        serverThread.IsBackground = true;
        serverThread.Start();
      } catch {
        // SCM receives a service-start error; never run with default DACL.
        throw;
      }
    }

    static PipeSecurity ExplicitDacl(string service, string worker) {
      var sec = new PipeSecurity();
      sec.SetAccessRuleProtection(true, false);
      sec.AddAccessRule(new PipeAccessRule(
        new SecurityIdentifier("S-1-5-18"), PipeAccessRights.FullControl, AccessControlType.Allow));
      sec.AddAccessRule(new PipeAccessRule(
        new SecurityIdentifier(service), PipeAccessRights.FullControl, AccessControlType.Allow));
      // No WRITE_DAC, WRITE_OWNER, CreateNewInstance for clients.
      sec.AddAccessRule(new PipeAccessRule(
        new SecurityIdentifier(worker), PipeAccessRights.ReadWrite, AccessControlType.Allow));
      return sec;
    }

    void Serve() {
      while (!stopping) {
        try {
          var sec = ExplicitDacl(serviceSid, workerSid);
          using (var pipe = new NamedPipeServerStream(PipeName, PipeDirection.InOut,
                   1, PipeTransmissionMode.Byte, PipeOptions.None, 4096, 4096, sec)) {
            active = pipe;
            pipe.WaitForConnection();
            if (stopping) break;
            string peer = null;
            pipe.RunAsClient(() => {
              using (var identity = WindowsIdentity.GetCurrent()) {
                peer = identity.User.Value;
              }
            });
            byte[] reply;
            if (peer != workerSid) {
              reply = Encoding.ASCII.GetBytes("DENY_PEER_SID\n");
            } else {
              var incoming = new byte[64];
              int n = pipe.Read(incoming, 0, incoming.Length);
              string request = Encoding.ASCII.GetString(incoming, 0, n);
              // Transport attestation only: no request can write to a file.
              reply = Encoding.ASCII.GetBytes(
                request == "AUTH_PROBE\n" ? "AUTH_PEER_OK_NO_WRITE\n" : "DENY_UNSUPPORTED_OPERATION\n");
            }
            pipe.Write(reply, 0, reply.Length);
            pipe.Flush();
          }
        } catch (IOException) { if (stopping) break; }
          catch (ObjectDisposedException) { if (stopping) break; }
          catch (Exception) {
            // Fail closed: never degrade to listener with default security.
            stopping = true;
            break;
          }
        finally { active = null; }
      }
    }

    protected override void OnStop() {
      stopping = true;
      try { if (active != null) active.Dispose(); } catch {}
      if (serverThread != null && !serverThread.Join(5000))
        throw new InvalidOperationException("SERVER_THREAD_STOP_UNVERIFIED");
    }
    public static void Main() {
      ServiceBase.Run(new BrokerAttestationService());
    }
  }
}
