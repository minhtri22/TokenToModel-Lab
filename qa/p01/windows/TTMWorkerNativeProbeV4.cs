// TTM P01 L1 Worker native probe V4 -- source-only successor to V3.
// DACL is read from the authenticated worker's already-connected pipe HANDLE,
// not via a second name-based GetFileSecurityW open (which failed ERROR_PIPE_BUSY).
// Windows .NET Framework 4.x; no files written and no scientific workloads.
using System;
using System.IO;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using Microsoft.Win32.SafeHandles;

public static class TTMWorkerNativeProbeV4 {
  [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
  static extern bool LogonUser(string user, string domain, string password,
                                int logonType, int provider, out IntPtr token);
  [DllImport("advapi32.dll", SetLastError = true)]
  static extern bool ImpersonateLoggedOnUser(IntPtr token);
  [DllImport("advapi32.dll", SetLastError = true)]
  static extern bool RevertToSelf();
  [DllImport("kernel32.dll", SetLastError = true)]
  static extern bool CloseHandle(IntPtr token);
  [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
  static extern IntPtr CreateFile(string path, uint access, uint share, IntPtr attributes,
                                 uint disposition, uint flags, IntPtr template);

  // SE_FILE_OBJECT=1 (pipe handles are File objects); DACL_SECURITY_INFORMATION=4.
  // The worker's PipeAccessRights.ReadWrite includes READ_CONTROL but not bit 0x4.
  [DllImport("advapi32.dll", SetLastError = true)]
  static extern uint GetSecurityInfo(SafePipeHandle handle, uint objectType, uint securityInfo,
                                     IntPtr owner, IntPtr group, IntPtr dacl, IntPtr sacl,
                                     out IntPtr descriptor);
  [DllImport("advapi32.dll", SetLastError = true)]
  static extern uint GetSecurityDescriptorLength(IntPtr descriptor);
  [DllImport("advapi32.dll", SetLastError = true)]
  static extern bool GetSecurityDescriptorControl(IntPtr descriptor, out ushort control,
                                                  out uint revision);
  [DllImport("kernel32.dll", SetLastError = true)]
  static extern IntPtr LocalFree(IntPtr pointer);

  const uint FileGenericWrite = 0x40000000u;
  const uint OpenExisting = 3u;
  const uint ShareAll = 7u;
  const uint DirectoryFlags = 0x02000000u | 0x00200000u;
  const int AccessDenied = 5;

  static string Hex(byte[] data) {
    using (SHA256 sha = SHA256.Create()) {
      return BitConverter.ToString(sha.ComputeHash(data)).Replace("-", "").ToLowerInvariant();
    }
  }

  static string AuditConnectedPipe(SafePipeHandle handle, string serviceSid,
                                    string workerSid) {
    if (handle == null || handle.IsClosed || handle.IsInvalid)
      return "BLOCK_INVALID_CONNECTED_PIPE_HANDLE";
    IntPtr descriptor = IntPtr.Zero;
    uint result = GetSecurityInfo(handle, 1u, 4u,
                                  IntPtr.Zero, IntPtr.Zero, IntPtr.Zero,
                                  IntPtr.Zero, out descriptor);
    if (result != 0)
      return "BLOCK_HANDLE_GETSECURITYINFO_" + result.ToString();
    try {
      if (descriptor == IntPtr.Zero) return "BLOCK_NULL_SECURITY_DESCRIPTOR";
      ushort control;
      uint revision;
      if (!GetSecurityDescriptorControl(descriptor, out control, out revision))
        return "BLOCK_DESCRIPTOR_CONTROL_" + Marshal.GetLastWin32Error().ToString();
      // SE_SELF_RELATIVE(0x8000), SE_DACL_PROTECTED(0x1000), SE_DACL_PRESENT(0x0004).
      if ((control & 0x8000) == 0 || (control & 0x1000) == 0 ||
          (control & 0x0004) == 0)
        return "BLOCK_DESCRIPTOR_NOT_SELF_RELATIVE_PROTECTED_PRESENT";
      uint length = GetSecurityDescriptorLength(descriptor);
      if (length < 20u || length > 65536u)
        return "BLOCK_SECURITY_DESCRIPTOR_LENGTH";
      byte[] raw = new byte[(int)length];
      Marshal.Copy(descriptor, raw, 0, raw.Length);
      RawSecurityDescriptor sd = new RawSecurityDescriptor(raw, 0);
      if (sd.DiscretionaryAcl == null)
        return "BLOCK_NULL_PIPE_DACL";
      int allowCount = 0;
      bool systemSeen = false, serviceSeen = false, workerSeen = false;
      foreach (GenericAce item in sd.DiscretionaryAcl) {
        CommonAce ace = item as CommonAce;
        if (ace == null || ace.AceQualifier != AceQualifier.AccessAllowed ||
            (ace.AceFlags & AceFlags.Inherited) != 0)
          return "BLOCK_UNEXPECTED_PIPE_ACE";
        string sid = ace.SecurityIdentifier.Value;
        int mask = ace.AccessMask;
        allowCount++;
        if (sid == "S-1-5-18") {
          if (systemSeen || mask != (int)PipeAccessRights.FullControl)
            return "BLOCK_SYSTEM_ACE_UNEXPECTED";
          systemSeen = true;
        } else if (sid == serviceSid) {
          if (serviceSeen || mask != (int)PipeAccessRights.FullControl)
            return "BLOCK_SERVICE_ACE_UNEXPECTED";
          serviceSeen = true;
        } else if (sid == workerSid) {
          if (workerSeen || mask != (int)PipeAccessRights.ReadWrite)
            return "BLOCK_WORKER_ACE_UNEXPECTED";
          // Defensive explicit bit checks independent of exact mask comparison.
          if ((mask & 0x00000004) != 0 || (mask & 0x00040000) != 0 ||
              (mask & 0x00080000) != 0 || (mask & 0x00020003) != 0x00020003)
            return "BLOCK_WORKER_PIPE_FORBIDDEN_OR_MISSING_RIGHTS";
          workerSeen = true;
        } else {
          return "BLOCK_BROAD_OR_UNKNOWN_PIPE_ALLOW_SID";
        }
      }
      if (allowCount != 3 || !systemSeen || !serviceSeen || !workerSeen)
        return "BLOCK_PIPE_DACL_EXPECTED_3_SIDS";
      // Only the fingerprint is returned. Raw SD, token and credentials stay local.
      return "PASS_HANDLE_PIPE_DACL_EXACT_SHA256_" + Hex(raw);
    } finally {
      if (descriptor != IntPtr.Zero) LocalFree(descriptor);
    }
  }

  static string DeniedEvidenceRights(string evidenceRoot, string ledger) {
    // Each right independently checked; never claim each denied from a combined open.
    uint[] forbidden = new uint[] {
      0x00000002u, // FILE_ADD_FILE on directory
      0x00000004u, // FILE_ADD_SUBDIRECTORY
      0x00000010u, // FILE_WRITE_EA
      0x00000100u, // FILE_WRITE_ATTRIBUTES
      0x00010000u, // DELETE
      0x00040000u, // WRITE_DAC
      0x00080000u  // WRITE_OWNER
    };
    foreach (uint right in forbidden) {
      IntPtr handle = CreateFile(evidenceRoot, right, ShareAll, IntPtr.Zero,
                                OpenExisting, DirectoryFlags, IntPtr.Zero);
      int error = Marshal.GetLastWin32Error();
      if (handle != new IntPtr(-1) && handle != IntPtr.Zero) {
        CloseHandle(handle);
        return "BLOCK_WORKER_ALLOWED_RIGHT_0x" + right.ToString("X");
      }
      if (error != AccessDenied)
        return "BLOCK_DIR_ACCESS_INCONCLUSIVE_0x" + right.ToString("X") +
               "_ERROR_" + error.ToString();
    }
    IntPtr ledgerHandle = CreateFile(ledger, FileGenericWrite, ShareAll, IntPtr.Zero,
                                    OpenExisting, 0u, IntPtr.Zero);
    int ledgerError = Marshal.GetLastWin32Error();
    if (ledgerHandle != new IntPtr(-1) && ledgerHandle != IntPtr.Zero) {
      CloseHandle(ledgerHandle);
      return "BLOCK_WORKER_CAN_WRITE_LEDGER";
    }
    if (ledgerError != AccessDenied)
      return "BLOCK_LEDGER_ACCESS_INCONCLUSIVE_" + ledgerError.ToString();
    return "PASS_DENIED_RIGHTS";
  }

  public static string Run(string user, string domain, string password,
                           string evidenceRoot, string pipeName,
                           string expectedServiceSid, string expectedWorkerSid) {
    if (!Path.IsPathRooted(evidenceRoot) || !Directory.Exists(evidenceRoot))
      return "BLOCK_INVALID_EVIDENCE_ROOT";
    if (pipeName != "TTM_P01_L1_BROKER_V1")
      return "BLOCK_UNPINNED_PIPE";
    if (string.IsNullOrEmpty(expectedServiceSid) ||
        !expectedServiceSid.StartsWith("S-1-5-80-") ||
        string.IsNullOrEmpty(expectedWorkerSid) ||
        !expectedWorkerSid.StartsWith("S-1-5-21-") ||
        expectedWorkerSid == expectedServiceSid)
      return "BLOCK_EXPECTED_SID_PIN";
    string ledger = Path.Combine(evidenceRoot, "broker_ledger.sqlite3");
    if (!File.Exists(ledger))
      return "BLOCK_LEDGER_MISSING";
    // No generic write or CreateNewInstance access is requested for the client.
    if ((((int)PipeAccessRights.ReadWrite) & ((int)PipeAccessRights.CreateNewInstance)) != 0)
      return "BLOCK_CLIENT_RIGHTS_MASK";
    IntPtr token = IntPtr.Zero;
    if (!LogonUser(user, domain, password, 2, 0, out token))
      return "BLOCK_WORKER_LOGON_" + Marshal.GetLastWin32Error().ToString();
    bool impersonated = false;
    try {
      if (!ImpersonateLoggedOnUser(token))
        return "BLOCK_WORKER_IMPERSONATE_" + Marshal.GetLastWin32Error().ToString();
      impersonated = true;
      using (WindowsIdentity identity = WindowsIdentity.GetCurrent()) {
        if (identity.User == null || identity.User.Value != expectedWorkerSid)
          return "BLOCK_WORKER_TOKEN_SID_MISMATCH";
      }
      try {
        using (NamedPipeClientStream client = new NamedPipeClientStream(
                 ".", pipeName, PipeAccessRights.ReadWrite, PipeOptions.None,
                 TokenImpersonationLevel.Impersonation, HandleInheritability.None)) {
          client.Connect(4000);
          string aclResult = AuditConnectedPipe(client.SafePipeHandle,
                                                expectedServiceSid, expectedWorkerSid);
          if (!aclResult.StartsWith("PASS_HANDLE_PIPE_DACL_EXACT_SHA256_"))
            return aclResult;
          string denied = DeniedEvidenceRights(evidenceRoot, ledger);
          if (denied != "PASS_DENIED_RIGHTS") return denied;
          byte[] request = Encoding.ASCII.GetBytes("AUTH_PROBE\n");
          client.Write(request, 0, request.Length);
          client.Flush();
          byte[] reply = new byte[128];
          // Source-only candidate; receive completion must be bounded by the
          // independent Windows harness before any one-shot native execution.
          client.ReadTimeout = 4000;
          int n = client.Read(reply, 0, reply.Length);
          if (Encoding.ASCII.GetString(reply, 0, n) != "AUTH_PEER_OK_NO_WRITE\n")
            return "BLOCK_PIPE_PEER_RESPONSE";
          return "PASS_WORKER_V4_HANDLE_DACL_DENIED_RIGHTS_PEER_AUTH_" +
                 aclResult.Substring("PASS_HANDLE_PIPE_DACL_EXACT_SHA256_".Length);
        }
      } catch (Exception e) {
        return "BLOCK_PIPE_HANDLE_OR_PEER_" + e.GetType().Name;
      }
    } finally {
      if (impersonated && !RevertToSelf())
        throw new InvalidOperationException("WORKER_REVERT_TO_SELF_FAILED");
      if (token != IntPtr.Zero) CloseHandle(token);
    }
  }
}
