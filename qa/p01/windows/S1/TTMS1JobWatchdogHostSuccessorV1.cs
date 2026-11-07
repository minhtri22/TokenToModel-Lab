// TTM P01 L1 S1 / Host V1: source-only candidate, no permit issued.
// Compiled only with exact pinned IsolatedJobWatchdogV2 engine after future authorization.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Json;
using System.Security.Cryptography;
using System.Text;

namespace TTMP01S1 {
 [DataContract] internal sealed class S1NativePermit {
  [DataMember(Name="schema")] public string Schema;
  [DataMember(Name="decision")] public string Decision;
  [DataMember(Name="permit_id")] public string PermitId;
  [DataMember(Name="one_shot_id")] public string OneShotId;
  [DataMember(Name="original_head")] public string OriginalHead;
  [DataMember(Name="harness_sha256")] public string HarnessSha;
  [DataMember(Name="watchdog_sha256")] public string WatchdogSha;
  [DataMember(Name="host_sha256")] public string HostSha;
  [DataMember(Name="runner_sha256")] public string RunnerSha;
  [DataMember(Name="scm_actions")] public string ScmActions;
  [DataMember(Name="allowed_native_runs")] public int AllowedNativeRuns;
  [DataMember(Name="scope")] public string Scope;
 }
 internal static class S1JobWatchdogHostV1 {
  const string Root=@"D:\WORK\RESEARCH\TokenToModel-Lab";
  const string PermitId="TTM_P01_L1_S1_NATIVE_SUCCESSOR_PERMIT_20261107";
  const string OneShotId="TTM_P01_L1_S1_NATIVE_SUCCESSOR_ONCE_20261107";
  const string MarkerName="L1_S1_NATIVE_SUCCESSOR_ONE_SHOT_ATTEMPT_20261107.lock";
  const string FrozenHead="f2e333df2f9ca24a8e483507c3cfc386ad9c76f0";
  const string PermitSchema="ttm.p01.l1.s1.native_successor_permit.v1";
  const string MarkerSchema="ttm.p01.l1.s1.native_successor_marker.v1";
  const string Decision="AUTHORIZED_ONCE_EXACT_SOURCE_S1_NATIVE";
  const string Scope="S1_ISOLATED_SUCCESSOR_COMPILE_SINGLE_NATIVE_SMOKE";
  static void Need(bool yes,string why) {
   if(!yes)throw new InvalidOperationException(why);
  }
  static string Hash(byte[] bytes) {
   using(SHA256 h=SHA256.Create())
    return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();
  }
  static bool HashShape(string s) {
   if(s==null||s.Length!=64)return false;
   foreach(char c in s)
    if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))return false;
   return true;
  }
  static string LocalFile(string path,string basename) {
   Need(Path.IsPathRooted(path),"BLOCK_RELATIVE_PATH");
   string full=Path.GetFullPath(path);
   Need(full.StartsWith(Root+Path.DirectorySeparatorChar,
       StringComparison.OrdinalIgnoreCase),"BLOCK_OUTSIDE_PROJECT");
   Need(String.Equals(Path.GetFileName(full),basename,
       StringComparison.OrdinalIgnoreCase),"BLOCK_FILENAME");
   string current=Path.GetDirectoryName(full);
   while(!String.IsNullOrEmpty(current)) {
    Need(Directory.Exists(current),"BLOCK_PARENT_MISSING");
    Need((File.GetAttributes(current)&FileAttributes.ReparsePoint)==0,"BLOCK_PARENT_REPARSE");
    if(String.Equals(current,Root,StringComparison.OrdinalIgnoreCase))break;
    string parent=Path.GetDirectoryName(current);
    Need(parent!=current,"BLOCK_PARENT_LOOP");
    current=parent;
   }
   Need(String.Equals(current,Root,StringComparison.OrdinalIgnoreCase),"BLOCK_ROOT");
   Need(File.Exists(full) &&
       (File.GetAttributes(full)&FileAttributes.ReparsePoint)==0,"BLOCK_FILE_MISSING_OR_REPARSE");
   return full;
  }
  static byte[] Pinned(string file,string sha) {
   Need(HashShape(sha),"BLOCK_HASH_SHAPE");
   byte[] data=File.ReadAllBytes(file);
   Need(Hash(data)==sha,"BLOCK_PINNED_HASH");
   return data;
  }
  static S1NativePermit ReadPermit(byte[] data) {
   using(MemoryStream m=new MemoryStream(data)) {
    DataContractJsonSerializer s=new DataContractJsonSerializer(typeof(S1NativePermit));
    S1NativePermit p=(S1NativePermit)s.ReadObject(m);
    Need(p!=null,"BLOCK_PERMIT_NULL");
    return p;
   }
  }
  static Dictionary<string,string> ReadMarker(byte[] data) {
   string s=new UTF8Encoding(false,true).GetString(data);
   string[] lines=s.Replace("\r\n","\n").Split('\n');
   Need(lines.Length==6&&lines[5].Length==0,"BLOCK_MARKER_LINES");
   Dictionary<string,string> map=new Dictionary<string,string>(StringComparer.Ordinal);
   for(int i=0;i<5;i++) {
    int pos=lines[i].IndexOf('=');
    Need(pos>0&&pos<lines[i].Length-1,"BLOCK_MARKER_SYNTAX");
    string key=lines[i].Substring(0,pos);
    Need(!map.ContainsKey(key),"BLOCK_MARKER_DUPLICATE");
    map.Add(key,lines[i].Substring(pos+1));
   }
   return map;
  }
  static void Match(Dictionary<string,string> map,string key,string expected) {
   string actual;
   Need(map.TryGetValue(key,out actual)&&actual==expected,"BLOCK_MARKER_"+key);
  }
  static void Print(IsolatedJobWatchdogV2.Result r) {
   Console.WriteLine("TTM_S1_HOST_VERDICT="+r.Verdict);
   Console.WriteLine("TTM_S1_HOST_PID="+r.ChildPid);
   Console.WriteLine("TTM_S1_HOST_EXIT="+r.ExitCode);
   Console.WriteLine("TTM_S1_HOST_JOB_CHECKED="+(r.JobChecked?"TRUE":"FALSE"));
   Console.WriteLine("TTM_S1_HOST_EXIT_CONFIRMED="+(r.ChildExitConfirmed?"TRUE":"FALSE"));
   Console.WriteLine("TTM_S1_HOST_STDOUT_BOUNDED="+(r.StdoutBounded?"TRUE":"FALSE"));
   Console.WriteLine("TTM_S1_HOST_STDERR_EMPTY="+(r.StderrEmpty?"TRUE":"FALSE"));
   Console.WriteLine("TTM_S1_HOST_STDOUT_LENGTH="+r.StdoutLength);
   Console.WriteLine("TTM_S1_HOST_STDERR_LENGTH="+r.StderrLength);
   Console.WriteLine("TTM_S1_HOST_STDOUT_SHA256="+r.StdoutSha256);
   Console.WriteLine("TTM_S1_HOST_STDERR_SHA256="+r.StderrSha256);
  }
  // Eight positional arguments from the future one-shot PowerShell runner:
  // project, S1.exe, SHA256(EXE), permit.json, SHA256(permit),
  // native-marker, SHA256(marker), run_id.
  public static int Main(string[] args) {
   try {
    Need(args!=null&&args.Length==8,"BLOCK_ARGUMENTS");
    Need(Environment.OSVersion.Platform==PlatformID.Win32NT&&
         Environment.Is64BitProcess,"BLOCK_WINDOWS_X64");
    Need(Path.GetFullPath(args[0]).TrimEnd('\\').Equals(Root,
         StringComparison.OrdinalIgnoreCase),"BLOCK_PROJECT_ID");
    string binary=LocalFile(args[1],"TTMS1IsolatedCancellationHarness.exe");
    Need(HashShape(args[2]),"BLOCK_BINARY_HASH");
    string permitFile=LocalFile(args[3],"S1_NATIVE_SUCCESSOR_PERMIT.json");
    string markerFile=LocalFile(args[5],MarkerName);
    Need(HashShape(args[4])&&HashShape(args[6]),"BLOCK_META_HASH");
    string runId=args[7];
    Need(runId.StartsWith("S1_NATIVE_SUCCESSOR_",StringComparison.Ordinal)&&
         runId.Length>=22&&runId.Length<=90,"BLOCK_RUN_ID");
    foreach(char c in runId)
     Need((c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_',"BLOCK_RUN_ID_CHAR");
    S1NativePermit p=ReadPermit(Pinned(permitFile,args[4]));
    Need(p.Schema==PermitSchema&&p.Decision==Decision&&p.PermitId==PermitId&&
         p.OneShotId==OneShotId&&p.OriginalHead==FrozenHead&&p.Scope==Scope&&
         p.ScmActions=="FORBIDDEN"&&p.AllowedNativeRuns==1&&
         HashShape(p.HarnessSha)&&HashShape(p.WatchdogSha)&&
         HashShape(p.HostSha)&&HashShape(p.RunnerSha),"BLOCK_PERMIT_CONTENT");
    Dictionary<string,string> m=ReadMarker(Pinned(markerFile,args[6]));
    Match(m,"schema",MarkerSchema);
    Match(m,"permit_id",PermitId);
    Match(m,"permit_sha256",args[4]);
    Match(m,"one_shot_id",OneShotId);
    Match(m,"run_id",runId);
    // Only the pinned engine can spawn the child; this host has no Win32 process API.
    IsolatedJobWatchdogV2.Result result=
      IsolatedJobWatchdogV2.RunAfterExternalPermit(Root,binary,args[2]);
    Print(result);
    return result.Verdict=="PASS_ISOLATED_S1_ONLY"?0:3;
   } catch(Exception ex) {
    Console.WriteLine("TTM_S1_HOST_VERDICT=BLOCK_HOST_"+ex.GetType().Name);
    return 3;
   }
  }
 }
}
