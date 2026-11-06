// Native Windows probe V2 for pinned TTM P01 worker account.
// No files are created. Tests denied OPEN_EXISTING write access and authenticated
// Named Pipe peer SID. Not a substitute for independent W01-W12.
using System;
using System.IO;
using System.IO.Pipes;
using System.Runtime.InteropServices;
using System.Text;

public static class TTMWorkerNativeProbe {
 [DllImport("advapi32.dll",SetLastError=true,CharSet=CharSet.Unicode)]
 static extern bool LogonUser(string username,string domain,string password,int logonType,int provider,out IntPtr token);
 [DllImport("advapi32.dll",SetLastError=true)]
 static extern bool ImpersonateLoggedOnUser(IntPtr token);
 [DllImport("advapi32.dll",SetLastError=true)]
 static extern bool RevertToSelf();
 [DllImport("kernel32.dll",SetLastError=true)]
 static extern bool CloseHandle(IntPtr handle);
 [DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]
 static extern IntPtr CreateFile(string path,uint access,uint share,IntPtr attributes,
                                uint disposition,uint flags,IntPtr template);
 public static string Run(string user,string domain,string password,string evidenceRoot,string pipeName){
  if(!Path.IsPathRooted(evidenceRoot) || !Directory.Exists(evidenceRoot))
   return "BLOCK_INVALID_ROOT";
  if(pipeName!="TTM_P01_L1_BROKER_V1")return "BLOCK_UNPINNED_PIPE";
  IntPtr token=IntPtr.Zero;
  if(!LogonUser(user,domain,password,2,0,out token))
   return "BLOCK_LOGON_"+Marshal.GetLastWin32Error().ToString();
  bool impersonated=false;
  try {
   if(!ImpersonateLoggedOnUser(token))
    return "BLOCK_IMPERSONATE_"+Marshal.GetLastWin32Error().ToString();
   impersonated=true;
   // Check each requested right separately. An ACCESS_DENIED for a
   // combined request does NOT prove that every individual right is denied.
   uint[] forbiddenRights=new uint[]{
      0x00000002u,  // directory FILE_ADD_FILE
      0x00000004u,  // directory FILE_ADD_SUBDIRECTORY
      0x00000010u,  // FILE_WRITE_EA
      0x00000100u,  // FILE_WRITE_ATTRIBUTES
      0x00010000u,  // DELETE
      0x00040000u,  // WRITE_DAC
      0x00080000u   // WRITE_OWNER
   };
   foreach(uint right in forbiddenRights){
    IntPtr handle=CreateFile(evidenceRoot,right,0x7u,IntPtr.Zero,3u,
                            0x02000000u|0x00200000u,IntPtr.Zero);
    int error=Marshal.GetLastWin32Error();
    if(handle!=new IntPtr(-1) && handle!=IntPtr.Zero){
     CloseHandle(handle);
     return "BLOCK_WORKER_ALLOWED_RIGHT_0x"+right.ToString("X");
    }
    if(error!=5) return "BLOCK_DIR_ACCESS_INCONCLUSIVE_0x"+right.ToString("X")+"_ERROR_"+error.ToString();
   }
   string ledger=Path.Combine(evidenceRoot,"broker_ledger.sqlite3");
   if(!File.Exists(ledger)) return "BLOCK_LEDGER_MISSING";
   // Existing ledger must not be opened under the worker token for WRITE.
   IntPtr ledgerHandle=CreateFile(ledger,0x40000000u,0x7u,
                                IntPtr.Zero,3u,0u,IntPtr.Zero);
   int ledgerError=Marshal.GetLastWin32Error();
   if(ledgerHandle!=new IntPtr(-1) && ledgerHandle!=IntPtr.Zero){
    CloseHandle(ledgerHandle);
    return "BLOCK_WORKER_CAN_WRITE_LEDGER";
   }
   if(ledgerError!=5)return "BLOCK_LEDGER_ACCESS_INCONCLUSIVE_"+ledgerError.ToString();
   try {
    using(var c=new NamedPipeClientStream(".",pipeName,PipeDirection.InOut,PipeOptions.None,System.Security.Principal.TokenImpersonationLevel.Impersonation)){
     c.Connect(4000);
     c.ReadTimeout=4000;
     byte[] request=Encoding.ASCII.GetBytes("AUTH_PROBE\n");
     c.Write(request,0,request.Length);
     c.Flush();
     byte[] result=new byte[128];
     int n=c.Read(result,0,result.Length);
     string response=Encoding.ASCII.GetString(result,0,n);
     if(response!="AUTH_PEER_OK_NO_WRITE\n")
      return "BLOCK_UNEXPECTED_PEER_RESPONSE";
     return "PASS_WORKER_SEPARATE_RIGHTS_LEDGER_DENIED_AND_PEER_AUTH_NO_WRITE";
    }
   } catch (Exception e){
    return "BLOCK_PIPE_PEER_PROBE_"+e.GetType().Name;
   }
  } finally {
   if(impersonated && !RevertToSelf())
    throw new InvalidOperationException("REVERT_TO_SELF_FAILED");
   CloseHandle(token);
  }
 }
}
