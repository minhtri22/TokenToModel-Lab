// TTM P01 L1 S1 / Job Object watchdog V2: SOURCE-ONLY CANDIDATE.
// No Main(), no permit issuance, no compilation or execution in this phase.
// Future one-shot driver must pin all source hashes, receipt and consume marker.
// Design target: Windows 11 x64 / .NET Framework 4.x / C# 5.
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Win32.SafeHandles;

namespace TTMP01S1 {
internal static class IsolatedJobWatchdogV2 {
  const uint CREATE_SUSPENDED = 0x00000004;
  const uint CREATE_NO_WINDOW = 0x08000000;
  const uint EXTENDED_STARTUPINFO_PRESENT = 0x00080000;
  const uint STARTF_USESTDHANDLES = 0x00000100;
  const uint HANDLE_FLAG_INHERIT = 0x00000001;
  const uint JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008;
  const uint JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200;
  const uint JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000;
  const int JobObjectExtendedLimitInformation = 9;
  const int PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002;
  const int PROC_THREAD_ATTRIBUTE_JOB_LIST = 0x0002000D;
  const uint WAIT_OBJECT_0 = 0;
  const uint WAIT_TIMEOUT = 258;
  const uint WAIT_FAILED = 0xffffffff;
  const uint GENERIC_READ = 0x80000000;
  const uint FILE_SHARE_READ = 0x00000001;
  const uint FILE_SHARE_WRITE = 0x00000002;
  const uint OPEN_EXISTING = 3;
  const int TIMEOUT_MS = 15000;
  const int CONFIRM_MS = 3000;
  const int OUTPUT_LIMIT = 8192;
  const int JOB_MEMORY_MAX_BYTES = 256 * 1024 * 1024;

  [StructLayout(LayoutKind.Sequential)]
  struct SECURITY_ATTRIBUTES {
    public int nLength;
    public IntPtr lpSecurityDescriptor;
    [MarshalAs(UnmanagedType.Bool)] public bool bInheritHandle;
  }
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
  struct STARTUPINFO {
    public int cb;
    [MarshalAs(UnmanagedType.LPWStr)] public string lpReserved;
    [MarshalAs(UnmanagedType.LPWStr)] public string lpDesktop;
    [MarshalAs(UnmanagedType.LPWStr)] public string lpTitle;
    public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute;
    public uint dwFlags;
    public short wShowWindow, cbReserved2;
    public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
  }
  [StructLayout(LayoutKind.Sequential)]
  struct STARTUPINFOEX { public STARTUPINFO StartupInfo; public IntPtr lpAttributeList; }
  [StructLayout(LayoutKind.Sequential)]
  struct PROCESS_INFORMATION {
    public IntPtr hProcess, hThread;
    public uint dwProcessId, dwThreadId;
  }
  [StructLayout(LayoutKind.Sequential)]
  struct IO_COUNTERS {
    public ulong ReadOperationCount, WriteOperationCount, OtherOperationCount;
    public ulong ReadTransferCount, WriteTransferCount, OtherTransferCount;
  }
  [StructLayout(LayoutKind.Sequential)]
  struct JOBOBJECT_BASIC_LIMIT_INFORMATION {
    public long PerProcessUserTimeLimit, PerJobUserTimeLimit;
    public uint LimitFlags;
    public UIntPtr MinimumWorkingSetSize, MaximumWorkingSetSize;
    public uint ActiveProcessLimit;
    public IntPtr Affinity;
    public uint PriorityClass, SchedulingClass;
  }
  [StructLayout(LayoutKind.Sequential)]
  struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION {
    public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
    public IO_COUNTERS IoInfo;
    public UIntPtr ProcessMemoryLimit, JobMemoryLimit, PeakProcessMemoryUsed, PeakJobMemoryUsed;
  }
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  static extern IntPtr CreateJobObjectW(IntPtr attributes, string name);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool SetInformationJobObject(IntPtr job, int informationClass,
    ref JOBOBJECT_EXTENDED_LIMIT_INFORMATION info, uint size);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool IsProcessInJob(IntPtr process, IntPtr job,
    [MarshalAs(UnmanagedType.Bool)] out bool inJob);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool TerminateJobObject(IntPtr job, uint exitCode);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool CreatePipe(out IntPtr read, out IntPtr write,
    ref SECURITY_ATTRIBUTES security, uint size);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool SetHandleInformation(IntPtr handle, uint mask, uint flags);
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  static extern IntPtr CreateFileW(string name, uint desiredAccess, uint share,
    ref SECURITY_ATTRIBUTES security, uint disposition, uint flags, IntPtr template);
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool CreateProcessW(string applicationName, StringBuilder commandLine,
    IntPtr processAttributes, IntPtr threadAttributes,
    [MarshalAs(UnmanagedType.Bool)] bool inheritHandles, uint creationFlags,
    IntPtr environment, string directory,
    ref STARTUPINFOEX startupInfo, out PROCESS_INFORMATION processInfo);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern uint ResumeThread(IntPtr thread);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern uint WaitForSingleObject(IntPtr handle, uint timeoutMs);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool GetExitCodeProcess(IntPtr process, out uint code);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool CloseHandle(IntPtr handle);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool InitializeProcThreadAttributeList(IntPtr attributes,
    int attributeCount, int flags, ref IntPtr size);
  [DllImport("kernel32.dll", SetLastError=true)]
  [return: MarshalAs(UnmanagedType.Bool)]
  static extern bool UpdateProcThreadAttribute(IntPtr attributes, uint flags, IntPtr key,
    IntPtr value, IntPtr size, IntPtr previous, IntPtr returnSize);
  [DllImport("kernel32.dll")]
  static extern void DeleteProcThreadAttributeList(IntPtr attributes);

  internal sealed class Result {
    internal string Verdict = "BLOCK_NOT_STARTED";
    internal uint ChildPid, ExitCode;
    internal bool JobChecked, ChildExitConfirmed, StdoutBounded, StderrEmpty;
    internal long StdoutLength, StderrLength;
    internal string StdoutSha256 = "", StderrSha256 = "";
  }
  sealed class Capture {
    internal byte[] Bytes = new byte[0];
    internal long SeenBytes;
    internal int OverflowFlag;
    internal bool Overflow;
    internal bool ReadFailed;
  }

  static void Need(bool condition, string reason) {
    if (!condition) throw new InvalidOperationException(reason);
  }
  static bool HandleOK(IntPtr value) {
    return value != IntPtr.Zero && value != new IntPtr(-1);
  }
  static void Close(ref IntPtr h) {
    if (HandleOK(h)) { CloseHandle(h); h = IntPtr.Zero; }
  }
  static byte[] Digest(byte[] bytes) {
    using (SHA256 h = SHA256.Create()) { return h.ComputeHash(bytes); }
  }
  static string Hex(byte[] bytes) {
    return BitConverter.ToString(bytes).Replace("-", "").ToLowerInvariant();
  }
  static void ProjectFile(string path, string projectRoot) {
    string root = Path.GetFullPath(projectRoot).TrimEnd(Path.DirectorySeparatorChar);
    string full = Path.GetFullPath(path);
    Need(String.Equals(root, @"D:\WORK\RESEARCH\TokenToModel-Lab",
      StringComparison.OrdinalIgnoreCase), "BLOCK_PROJECT_ROOT");
    Need(full.StartsWith(root + Path.DirectorySeparatorChar,
      StringComparison.OrdinalIgnoreCase), "BLOCK_EXE_OUTSIDE_PROJECT");
    string current = Path.GetDirectoryName(full);
    while (!String.IsNullOrEmpty(current)) {
      Need(Directory.Exists(current), "BLOCK_MISSING_PARENT");
      Need((File.GetAttributes(current) & FileAttributes.ReparsePoint) == 0,
        "BLOCK_REPARSE_PARENT");
      if (String.Equals(current, root, StringComparison.OrdinalIgnoreCase)) break;
      string parent = Path.GetDirectoryName(current);
      Need(!String.Equals(parent, current, StringComparison.OrdinalIgnoreCase),
        "BLOCK_BAD_ROOT");
      current = parent;
    }
    Need(String.Equals(current, root, StringComparison.OrdinalIgnoreCase),
      "BLOCK_OUTSIDE_PROJECT");
    Need(File.Exists(full), "BLOCK_EXE_MISSING");
    Need((File.GetAttributes(full) & FileAttributes.ReparsePoint) == 0,
      "BLOCK_REPARSE_EXE");
  }
  static FileStream LockBinaryAndCheck(string binaryPath, string sha) {
    Need(sha != null && sha.Length == 64, "BLOCK_NO_EXE_HASH");
    // FileShare.Read denies write AND delete/rename while the handle remains open.
    FileStream handle = new FileStream(binaryPath, FileMode.Open, FileAccess.Read,
      FileShare.Read);
    try {
      string actual;
      using (SHA256 h = SHA256.Create()) { actual = Hex(h.ComputeHash(handle)); }
      Need(String.Equals(actual, sha, StringComparison.OrdinalIgnoreCase),
        "BLOCK_EXE_HASH");
      return handle;  // Caller must keep open through CreateProcess and child exit.
    } catch { handle.Dispose(); throw; }
  }

  // Reader runs on a separate managed task. Child cannot write to a disk log.
  // Memory never stores more than 8192 bytes; overflow is signaled and drained.
  static Capture ReadCapped(IntPtr inheritedReadHandle, Capture capture) {
    try {
      using (SafeFileHandle safe = new SafeFileHandle(inheritedReadHandle, true))
      using (FileStream pipe = new FileStream(safe, FileAccess.Read, 4096, false))
      using (MemoryStream mem = new MemoryStream()) {
        byte[] block = new byte[512];
        for (;;) {
          int read = pipe.Read(block, 0, block.Length);
          if (read == 0) break;
          capture.SeenBytes += read;
          if (capture.SeenBytes > OUTPUT_LIMIT) {
            capture.Overflow = true;
            Interlocked.Exchange(ref capture.OverflowFlag, 1);
            // Discard remaining data and continue draining to release pipe backpressure.
          } else {
            mem.Write(block, 0, read);
          }
        }
        capture.Bytes = mem.ToArray();
      }
    } catch { capture.ReadFailed = true; }
    return capture;
  }
  static bool CheckStdout(byte[] data) {
    string decoded;
    try { decoded = new UTF8Encoding(false, true).GetString(data); }
    catch { return false; }
    // No arbitrary text or extra blank lines allowed.
    string[] lines = decoded.Replace("\r\n", "\n").TrimEnd('\n').Split('\n');
    return lines.Length == 3 &&
      lines[0] == "TTM_S1_IDLE_ACCEPT=PASS_COMPLETED_ABORTED" &&
      lines[1] == "TTM_S1_SILENT_READ=PASS_COMPLETED_ABORTED" &&
      lines[2] == "TTM_S1_VERDICT=PASS_ISOLATED_CANCELLATION_ONLY";
  }

  // Future entrypoint with a *separately* verified one-shot permit; this source
  // deliberately contains no Main() and no permit-granting implementation.
  internal static Result RunAfterExternalPermit(string projectRoot, string binaryPath,
    string exactBinarySha256) {
    Result result = new Result();
    IntPtr job = IntPtr.Zero, stdin = IntPtr.Zero, outRead = IntPtr.Zero,
      outWrite = IntPtr.Zero, errRead = IntPtr.Zero, errWrite = IntPtr.Zero;
    IntPtr attributeList = IntPtr.Zero, attrJobValue = IntPtr.Zero, attrHandlesValue = IntPtr.Zero;
    bool attrInitialized = false, created = false, childFinished = false;
    PROCESS_INFORMATION child = new PROCESS_INFORMATION();
    Task<Capture> readOut = null, readErr = null;
    FileStream lockedBinary = null;
    try {
      Need(Environment.OSVersion.Platform == PlatformID.Win32NT && Environment.Is64BitProcess,
        "BLOCK_WINDOWS_X64_REQUIRED");
      Need(Path.IsPathRooted(binaryPath) &&
        String.Equals(Path.GetFileName(binaryPath),
          "TTMS1IsolatedCancellationHarness.exe", StringComparison.OrdinalIgnoreCase),
        "BLOCK_WRONG_S1_EXE");
      ProjectFile(binaryPath, projectRoot);
      lockedBinary = LockBinaryAndCheck(binaryPath, exactBinarySha256);

      job = CreateJobObjectW(IntPtr.Zero, null);
      Need(HandleOK(job), "BLOCK_CREATE_JOB");
      JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits =
        new JOBOBJECT_EXTENDED_LIMIT_INFORMATION();
      limits.BasicLimitInformation.LimitFlags =
        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_ACTIVE_PROCESS |
        JOB_OBJECT_LIMIT_JOB_MEMORY;
      limits.BasicLimitInformation.ActiveProcessLimit = 1;
      limits.JobMemoryLimit = new UIntPtr((uint)JOB_MEMORY_MAX_BYTES);
      Need(SetInformationJobObject(job, JobObjectExtendedLimitInformation,
        ref limits, (uint)Marshal.SizeOf(typeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION))),
        "BLOCK_SET_JOB_LIMITS");

      SECURITY_ATTRIBUTES security = new SECURITY_ATTRIBUTES();
      security.nLength = Marshal.SizeOf(typeof(SECURITY_ATTRIBUTES));
      security.bInheritHandle = true;
      Need(CreatePipe(out outRead, out outWrite, ref security, 4096),
        "BLOCK_STDOUT_PIPE");
      Need(CreatePipe(out errRead, out errWrite, ref security, 4096),
        "BLOCK_STDERR_PIPE");
      Need(SetHandleInformation(outRead, HANDLE_FLAG_INHERIT, 0) &&
           SetHandleInformation(errRead, HANDLE_FLAG_INHERIT, 0),
        "BLOCK_READ_HANDLE_INHERIT");
      stdin = CreateFileW("NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE,
        ref security, OPEN_EXISTING, 0, IntPtr.Zero);
      Need(HandleOK(stdin), "BLOCK_STDIN");

      // TWO creation-time attributes: only three inheritable std handles,
      // and association with *this* job in CreateProcessW itself.
      IntPtr needed = IntPtr.Zero;
      InitializeProcThreadAttributeList(IntPtr.Zero, 2, 0, ref needed);
      Need(needed.ToInt64() > 0, "BLOCK_ATTR_SIZE");
      attributeList = Marshal.AllocHGlobal(needed);
      Need(InitializeProcThreadAttributeList(attributeList, 2, 0, ref needed),
        "BLOCK_ATTR_INIT");
      attrInitialized = true;
      attrJobValue = Marshal.AllocHGlobal(IntPtr.Size);
      Marshal.WriteIntPtr(attrJobValue, job);
      attrHandlesValue = Marshal.AllocHGlobal(IntPtr.Size * 3);
      Marshal.WriteIntPtr(attrHandlesValue, IntPtr.Size * 0, stdin);
      Marshal.WriteIntPtr(attrHandlesValue, IntPtr.Size * 1, outWrite);
      Marshal.WriteIntPtr(attrHandlesValue, IntPtr.Size * 2, errWrite);
      Need(UpdateProcThreadAttribute(attributeList, 0,
        new IntPtr(PROC_THREAD_ATTRIBUTE_HANDLE_LIST), attrHandlesValue,
        new IntPtr(IntPtr.Size * 3), IntPtr.Zero, IntPtr.Zero), "BLOCK_HANDLE_LIST");
      Need(UpdateProcThreadAttribute(attributeList, 0,
        new IntPtr(PROC_THREAD_ATTRIBUTE_JOB_LIST), attrJobValue,
        new IntPtr(IntPtr.Size), IntPtr.Zero, IntPtr.Zero), "BLOCK_CREATION_JOB_LIST");

      STARTUPINFOEX startup = new STARTUPINFOEX();
      startup.StartupInfo.cb = Marshal.SizeOf(typeof(STARTUPINFOEX));
      startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
      startup.StartupInfo.hStdInput = stdin;
      startup.StartupInfo.hStdOutput = outWrite;
      startup.StartupInfo.hStdError = errWrite;
      startup.lpAttributeList = attributeList;
      StringBuilder cmd = new StringBuilder("\"" + binaryPath + "\"");
      Need(CreateProcessW(binaryPath, cmd, IntPtr.Zero, IntPtr.Zero, true,
        CREATE_SUSPENDED | CREATE_NO_WINDOW | EXTENDED_STARTUPINFO_PRESENT,
        IntPtr.Zero, Path.GetDirectoryName(binaryPath), ref startup, out child),
        "BLOCK_CREATE_WITH_JOB");
      created = true;
      result.ChildPid = child.dwProcessId;
      bool insideJob = false;
      Need(IsProcessInJob(child.hProcess, job, out insideJob) && insideJob,
        "BLOCK_JOB_MEMBERSHIP");
      result.JobChecked = true;
      // Parent must not retain write ends, otherwise pipe reader would never get EOF.
      Close(ref outWrite); Close(ref errWrite); Close(ref stdin);
      // Transfer native read-handle ownership to dedicated tasks.
      Capture stdoutState = new Capture(), stderrState = new Capture();
      IntPtr readOutHandle = outRead, readErrHandle = errRead;
      readOut = Task.Run(() => ReadCapped(readOutHandle, stdoutState));
      outRead = IntPtr.Zero; // Task now owns native read handle.
      readErr = Task.Run(() => ReadCapped(readErrHandle, stderrState));
      errRead = IntPtr.Zero; // Task now owns native read handle.
      Need(ResumeThread(child.hThread) != WAIT_FAILED, "BLOCK_RESUME");
      Stopwatch clock = Stopwatch.StartNew();
      bool timeoutOrOverflow = false;
      for (;;) {
        long elapsed = clock.ElapsedMilliseconds;
        if (elapsed >= TIMEOUT_MS) {
          result.Verdict = "BLOCK_WATCHDOG_TIMEOUT";
          timeoutOrOverflow = true;
          break;
        }
        uint waited = WaitForSingleObject(child.hProcess, (uint)Math.Min(50L, TIMEOUT_MS - elapsed));
        if (waited == WAIT_OBJECT_0) {
          childFinished = true;
          result.ChildExitConfirmed = true;
          break;
        }
        if (waited != WAIT_TIMEOUT) {
          result.Verdict = "BLOCK_WAIT_FAILED";
          timeoutOrOverflow = true;
          break;
        }
        // Actual in-memory cap is enforced by the readers. Parent kills the
        // owned job if either reader reports overflow; no child writes disk logs.
        if (Interlocked.CompareExchange(ref stdoutState.OverflowFlag, 0, 0) != 0 ||
            Interlocked.CompareExchange(ref stderrState.OverflowFlag, 0, 0) != 0) {
          result.Verdict = "BLOCK_CAPTURE_LIMIT";
          timeoutOrOverflow = true;
          break;
        }
      }
      if (timeoutOrOverflow) {
        Need(TerminateJobObject(job, 3), "BLOCK_TERMINATE_JOB");
        uint end = WaitForSingleObject(child.hProcess, CONFIRM_MS);
        childFinished = end == WAIT_OBJECT_0;
        result.ChildExitConfirmed = childFinished;
      }
      if (childFinished) {
        uint code;
        Need(GetExitCodeProcess(child.hProcess, out code), "BLOCK_EXIT_CODE");
        result.ExitCode = code;
      }
      if (childFinished && !timeoutOrOverflow) {
        Need(Task.WaitAll(new Task[] {readOut, readErr}, CONFIRM_MS),
          "BLOCK_READERS_TIMEOUT");
        Capture stdout = readOut.Result, stderr = readErr.Result;
        result.StdoutLength = stdout.SeenBytes;
        result.StderrLength = stderr.SeenBytes;
        result.StdoutSha256 = Hex(Digest(stdout.Bytes));
        result.StderrSha256 = Hex(Digest(stderr.Bytes));
        result.StdoutBounded = !stdout.ReadFailed && !stdout.Overflow;
        result.StderrEmpty = !stderr.ReadFailed && !stderr.Overflow && stderr.SeenBytes == 0;
        Need(result.StdoutBounded && result.StderrEmpty && codeIsZero(result.ExitCode) &&
          CheckStdout(stdout.Bytes), "BLOCK_OUTPUT_OR_EXIT");
        result.Verdict = "PASS_ISOLATED_S1_ONLY";
      }
    } catch (Exception ex) {
      // FAIL-CLOSED; never claim an unconfirmed child or a broker/SCM result.
      result.Verdict = "BLOCK_WATCHDOG_" + ex.GetType().Name;
    } finally {
      // Creation-time JOB_LIST guarantees child was in our job if created.
      // Kill-on-close covers launcher crash after CreateProcessW. Never kill
      // by name or by searching external PIDs.
      if (created && !childFinished && HandleOK(job)) {
        TerminateJobObject(job, 3);
        if (HandleOK(child.hProcess)) {
          uint end = WaitForSingleObject(child.hProcess, CONFIRM_MS);
          if (end == WAIT_OBJECT_0) result.ChildExitConfirmed = true;
          else result.Verdict = "BLOCK_TERMINATION_UNCONFIRMED";
        }
      }
      Close(ref outWrite); Close(ref errWrite); Close(ref stdin);
      if (attrInitialized) DeleteProcThreadAttributeList(attributeList);
      if (attrHandlesValue != IntPtr.Zero) Marshal.FreeHGlobal(attrHandlesValue);
      if (attrJobValue != IntPtr.Zero) Marshal.FreeHGlobal(attrJobValue);
      if (attributeList != IntPtr.Zero) Marshal.FreeHGlobal(attributeList);
      Close(ref child.hThread); Close(ref child.hProcess);
      Close(ref job);
      if (lockedBinary != null) lockedBinary.Dispose();
      // Pump tasks retain read-handle ownership until they finish.
      // If they did not finish by now, this result is not qualified.
      if ((readOut != null && !readOut.IsCompleted) ||
          (readErr != null && !readErr.IsCompleted)) {
        result.Verdict = "BLOCK_READERS_UNCONFIRMED";
      }
      Close(ref outRead);
      Close(ref errRead);
    }
    if (!result.ChildExitConfirmed || !result.JobChecked ||
        !result.StdoutBounded || !result.StderrEmpty) {
      if (result.Verdict == "PASS_ISOLATED_S1_ONLY")
        result.Verdict = "BLOCK_FINAL_INVARIANT";
    }
    return result;
  }
  static bool codeIsZero(uint code) { return code == 0; }
}
}
