// TTM P01 L1 S1: isolated Win32 Job Object engine (SOURCE ONLY).
// No Main(), no compile/launch/SCM actions are authorized by this source commit.
// Called only by a future separately authorized, exact-pinned one-shot launcher.
// Target: Windows x64 / .NET Framework 4.x / C# 5.
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;

namespace TTMP01S1 {
  internal static class IsolatedJobWatchdog {
    const uint CREATE_SUSPENDED = 0x00000004;
    const uint CREATE_NO_WINDOW = 0x08000000;
    const uint EXTENDED_STARTUPINFO_PRESENT = 0x00080000;
    const uint STARTF_USESTDHANDLES = 0x00000100;
    const uint HANDLE_FLAG_INHERIT = 0x00000001;
    const uint JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008;
    const uint JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000;
    const uint WAIT_OBJECT_0 = 0;
    const uint WAIT_TIMEOUT = 258;
    const uint WAIT_FAILED = 0xffffffff;
    const uint STDOUT_MAX_BYTES = 8192;
    const uint STDERR_MAX_BYTES = 8192;
    const uint TIMEOUT_MS = 15000;
    const uint TERMINATION_CONFIRM_MS = 3000;
    const uint GENERIC_READ = 0x80000000;
    const uint FILE_SHARE_READ = 0x00000001;
    const uint FILE_SHARE_WRITE = 0x00000002;
    const uint OPEN_EXISTING = 3;
    const uint FILE_ATTRIBUTE_NORMAL = 0x00000080;
    const int JobObjectExtendedLimitInformation = 9;
    const int ProcThreadAttributeHandleList = 0x00020002;

    [StructLayout(LayoutKind.Sequential)]
    struct SECURITY_ATTRIBUTES {
      public int nLength;
      public IntPtr lpSecurityDescriptor;
      [MarshalAs(UnmanagedType.Bool)] public bool bInheritHandle;
    }
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    struct STARTUPINFO {
      public int cb;
      public string lpReserved;
      public string lpDesktop;
      public string lpTitle;
      public int dwX;
      public int dwY;
      public int dwXSize;
      public int dwYSize;
      public int dwXCountChars;
      public int dwYCountChars;
      public int dwFillAttribute;
      public uint dwFlags;
      public short wShowWindow;
      public short cbReserved2;
      public IntPtr lpReserved2;
      public IntPtr hStdInput;
      public IntPtr hStdOutput;
      public IntPtr hStdError;
    }
    [StructLayout(LayoutKind.Sequential)]
    struct STARTUPINFOEX {
      public STARTUPINFO StartupInfo;
      public IntPtr lpAttributeList;
    }
    [StructLayout(LayoutKind.Sequential)]
    struct PROCESS_INFORMATION {
      public IntPtr hProcess;
      public IntPtr hThread;
      public uint dwProcessId;
      public uint dwThreadId;
    }
    [StructLayout(LayoutKind.Sequential)]
    struct IO_COUNTERS {
      public ulong ReadOperationCount;
      public ulong WriteOperationCount;
      public ulong OtherOperationCount;
      public ulong ReadTransferCount;
      public ulong WriteTransferCount;
      public ulong OtherTransferCount;
    }
    [StructLayout(LayoutKind.Sequential)]
    struct JOBOBJECT_BASIC_LIMIT_INFORMATION {
      public long PerProcessUserTimeLimit;
      public long PerJobUserTimeLimit;
      public uint LimitFlags;
      public UIntPtr MinimumWorkingSetSize;
      public UIntPtr MaximumWorkingSetSize;
      public uint ActiveProcessLimit;
      public IntPtr Affinity;
      public uint PriorityClass;
      public uint SchedulingClass;
    }
    [StructLayout(LayoutKind.Sequential)]
    struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION {
      public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
      public IO_COUNTERS IoInfo;
      public UIntPtr ProcessMemoryLimit;
      public UIntPtr JobMemoryLimit;
      public UIntPtr PeakProcessMemoryUsed;
      public UIntPtr PeakJobMemoryUsed;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern IntPtr CreateJobObjectW(IntPtr attributes, string name);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool SetInformationJobObject(IntPtr job, int infoClass,
      ref JOBOBJECT_EXTENDED_LIMIT_INFORMATION info, uint infoLength);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool TerminateJobObject(IntPtr job, uint exitCode);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CreateProcessW(string app, StringBuilder command,
      IntPtr procSecurity, IntPtr threadSecurity,
      [MarshalAs(UnmanagedType.Bool)] bool inheritHandles, uint flags,
      IntPtr environment, string currentDirectory,
      ref STARTUPINFOEX startup, out PROCESS_INFORMATION information);
    [DllImport("kernel32.dll", SetLastError = true)]
    static extern uint ResumeThread(IntPtr thread);
    [DllImport("kernel32.dll", SetLastError = true)]
    static extern uint WaitForSingleObject(IntPtr handle, uint millis);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool GetExitCodeProcess(IntPtr process, out uint code);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool TerminateProcess(IntPtr process, uint exitCode);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CloseHandle(IntPtr handle);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool SetHandleInformation(IntPtr handle, uint mask, uint flags);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern IntPtr CreateFileW(string name, uint access, uint share,
      ref SECURITY_ATTRIBUTES attributes, uint disposition, uint flags, IntPtr template);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool InitializeProcThreadAttributeList(IntPtr list, int count,
      int flags, ref IntPtr size);
    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool UpdateProcThreadAttribute(IntPtr list, uint flags,
      IntPtr attribute, IntPtr value, IntPtr length, IntPtr previous, IntPtr returnSize);
    [DllImport("kernel32.dll")]
    static extern void DeleteProcThreadAttributeList(IntPtr list);

    internal sealed class Outcome {
      internal string Status = "BLOCK_NOT_STARTED";
      internal uint Pid;
      internal uint ExitCode;
      internal bool ChildTerminationConfirmed;
      internal bool JobContainmentEstablished;
      internal string StdoutSha256 = "";
      internal string StderrSha256 = "";
    }

    static void Demand(bool valid, string code) {
      if (!valid) throw new InvalidOperationException(code);
    }
    static bool ValidHandle(IntPtr h) {
      return h != IntPtr.Zero && h != new IntPtr(-1);
    }
    static string HashFile(string path) {
      using (FileStream stream = File.Open(path, FileMode.Open, FileAccess.Read, FileShare.Read)) {
        using (SHA256 sha = SHA256.Create()) {
          return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
      }
    }
    static void DemandProjectLocal(string path, string root) {
      string full = Path.GetFullPath(path);
      string baseRoot = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar);
      Demand(full.StartsWith(baseRoot + Path.DirectorySeparatorChar,
        StringComparison.OrdinalIgnoreCase), "BLOCK_OUTSIDE_PROJECT");
      string current = Path.GetDirectoryName(full);
      while (!String.IsNullOrEmpty(current)) {
        if (Directory.Exists(current)) {
          Demand((File.GetAttributes(current) & FileAttributes.ReparsePoint) == 0,
            "BLOCK_REPARSE_PARENT");
        }
        if (String.Equals(current, baseRoot, StringComparison.OrdinalIgnoreCase)) break;
        string parent = Path.GetDirectoryName(current);
        Demand(parent != current, "BLOCK_PROJECT_PARENT");
        current = parent;
      }
      Demand(String.Equals(current, baseRoot, StringComparison.OrdinalIgnoreCase),
        "BLOCK_WORKSPACE_ROOT");
      if (File.Exists(full)) {
        Demand((File.GetAttributes(full) & FileAttributes.ReparsePoint) == 0,
          "BLOCK_REPARSE_FILE");
      }
    }
    static void SafeClose(ref IntPtr handle) {
      if (ValidHandle(handle)) {
        CloseHandle(handle);
        handle = IntPtr.Zero;
      }
    }

    // This method is intentionally NOT a program entrypoint. A future authorized
    // launcher must independently verify an exact-source permit and consume
    // its native one-shot marker before calling it. This source does not issue
    // or consume a permit and must NOT be compiled/executed at the design gate.
    internal static Outcome LaunchAfterExternalPermit(string projectRoot,
       string s1ExeAbsolutePath, string pinnedExeSha256,
       string stdoutAbsolutePath, string stderrAbsolutePath) {
      Outcome outcome = new Outcome();
      Demand(Environment.OSVersion.Platform == PlatformID.Win32NT, "BLOCK_NON_WINDOWS");
      Demand(Path.IsPathRooted(s1ExeAbsolutePath), "BLOCK_RELATIVE_EXE");
      Demand(Path.IsPathRooted(stdoutAbsolutePath) && Path.IsPathRooted(stderrAbsolutePath),
        "BLOCK_RELATIVE_LOG");
      Demand(String.Equals(Path.GetFileName(s1ExeAbsolutePath),
        "TTMS1IsolatedCancellationHarness.exe", StringComparison.OrdinalIgnoreCase),
        "BLOCK_WRONG_CHILD_EXE");
      DemandProjectLocal(s1ExeAbsolutePath, projectRoot);
      DemandProjectLocal(stdoutAbsolutePath, projectRoot);
      DemandProjectLocal(stderrAbsolutePath, projectRoot);
      Demand(!String.Equals(stdoutAbsolutePath, stderrAbsolutePath,
        StringComparison.OrdinalIgnoreCase), "BLOCK_IDENTICAL_LOG_PATH");
      Demand(!File.Exists(stdoutAbsolutePath) && !File.Exists(stderrAbsolutePath),
        "BLOCK_EXISTING_LOG");
      Demand(pinnedExeSha256.Length == 64, "BLOCK_EXE_SHA_MISSING");
      Demand(String.Equals(HashFile(s1ExeAbsolutePath), pinnedExeSha256,
        StringComparison.OrdinalIgnoreCase), "BLOCK_EXE_SHA_MISMATCH");
      IntPtr job = IntPtr.Zero, stdin = IntPtr.Zero, attrList = IntPtr.Zero;
      IntPtr handlesArray = IntPtr.Zero;
      bool attributeInitialized = false, childCreated = false, assigned = false;
      bool childExited = false, parentStreamsClosed = false;
      PROCESS_INFORMATION child = new PROCESS_INFORMATION();
      FileStream stdout = null, stderr = null;
      try {
        job = CreateJobObjectW(IntPtr.Zero, null);
        Demand(ValidHandle(job), "BLOCK_CREATE_JOB_" + Marshal.GetLastWin32Error());
        JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits =
          new JOBOBJECT_EXTENDED_LIMIT_INFORMATION();
        limits.BasicLimitInformation.LimitFlags =
          JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_ACTIVE_PROCESS;
        limits.BasicLimitInformation.ActiveProcessLimit = 1;
        Demand(SetInformationJobObject(job, JobObjectExtendedLimitInformation,
          ref limits, (uint)Marshal.SizeOf(typeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION))),
          "BLOCK_SET_JOB_LIMIT_" + Marshal.GetLastWin32Error());

        // CreateNew prevents overwriting previous one-shot evidence.
        stdout = new FileStream(stdoutAbsolutePath, FileMode.CreateNew,
          FileAccess.Write, FileShare.Read, 4096, FileOptions.None);
        stderr = new FileStream(stderrAbsolutePath, FileMode.CreateNew,
          FileAccess.Write, FileShare.Read, 4096, FileOptions.None);
        IntPtr stdOut = stdout.SafeFileHandle.DangerousGetHandle();
        IntPtr stdErr = stderr.SafeFileHandle.DangerousGetHandle();
        Demand(SetHandleInformation(stdOut, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT),
          "BLOCK_STDOUT_INHERIT");
        Demand(SetHandleInformation(stdErr, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT),
          "BLOCK_STDERR_INHERIT");
        SECURITY_ATTRIBUTES sa = new SECURITY_ATTRIBUTES();
        sa.nLength = Marshal.SizeOf(typeof(SECURITY_ATTRIBUTES));
        sa.bInheritHandle = true;
        stdin = CreateFileW("NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE,
          ref sa, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, IntPtr.Zero);
        Demand(ValidHandle(stdin), "BLOCK_STDIN_NUL");

        // STARTUPINFOEX handle list restricts inheritance to exactly 3 std handles.
        IntPtr needed = IntPtr.Zero;
        InitializeProcThreadAttributeList(IntPtr.Zero, 1, 0, ref needed);
        Demand(needed.ToInt64() > 0, "BLOCK_ATTRIBUTE_SIZE");
        attrList = Marshal.AllocHGlobal(needed);
        Demand(InitializeProcThreadAttributeList(attrList, 1, 0, ref needed),
          "BLOCK_ATTRIBUTE_INITIALIZE_" + Marshal.GetLastWin32Error());
        attributeInitialized = true;
        handlesArray = Marshal.AllocHGlobal(IntPtr.Size * 3);
        Marshal.WriteIntPtr(handlesArray, 0 * IntPtr.Size, stdin);
        Marshal.WriteIntPtr(handlesArray, 1 * IntPtr.Size, stdOut);
        Marshal.WriteIntPtr(handlesArray, 2 * IntPtr.Size, stdErr);
        Demand(UpdateProcThreadAttribute(attrList, 0,
          new IntPtr(ProcThreadAttributeHandleList),
          handlesArray, new IntPtr(IntPtr.Size * 3), IntPtr.Zero, IntPtr.Zero),
          "BLOCK_HANDLE_LIST_" + Marshal.GetLastWin32Error());

        STARTUPINFOEX startup = new STARTUPINFOEX();
        startup.StartupInfo.cb = Marshal.SizeOf(typeof(STARTUPINFOEX));
        startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
        startup.StartupInfo.hStdInput = stdin;
        startup.StartupInfo.hStdOutput = stdOut;
        startup.StartupInfo.hStdError = stdErr;
        startup.lpAttributeList = attrList;
        StringBuilder command = new StringBuilder("\"" + s1ExeAbsolutePath + "\"");
        Demand(CreateProcessW(s1ExeAbsolutePath, command, IntPtr.Zero,
          IntPtr.Zero, true, CREATE_SUSPENDED | CREATE_NO_WINDOW |
          EXTENDED_STARTUPINFO_PRESENT, IntPtr.Zero,
          Path.GetDirectoryName(s1ExeAbsolutePath), ref startup, out child),
          "BLOCK_CREATE_SUSPENDED_" + Marshal.GetLastWin32Error());
        childCreated = true;
        outcome.Pid = child.dwProcessId;
        Demand(AssignProcessToJobObject(job, child.hProcess),
          "BLOCK_ASSIGN_JOB_" + Marshal.GetLastWin32Error());
        assigned = true;
        outcome.JobContainmentEstablished = true;
        Demand(ResumeThread(child.hThread) != 0xffffffff,
          "BLOCK_RESUME_" + Marshal.GetLastWin32Error());

        Stopwatch clock = Stopwatch.StartNew();
        while (true) {
          long spent = clock.ElapsedMilliseconds;
          if (spent >= TIMEOUT_MS) {
            outcome.Status = "BLOCK_WATCHDOG_TIMEOUT";
            break;
          }
          uint slice = (uint)Math.Min(100L, TIMEOUT_MS - spent);
          uint wait = WaitForSingleObject(child.hProcess, slice);
          if (wait == WAIT_OBJECT_0) {
            childExited = true;
            outcome.ChildTerminationConfirmed = true;
            break;
          }
          if (wait == WAIT_FAILED || wait != WAIT_TIMEOUT) {
            outcome.Status = "BLOCK_WAIT_" + Marshal.GetLastWin32Error();
            break;
          }
          // Poll file growth; the post-run hard acceptance cap is 8 KiB.
          // File-system writes may overshoot between polls; native QA must
          // establish an acceptable byte/disk bound before release.
          if (new FileInfo(stdoutAbsolutePath).Length > STDOUT_MAX_BYTES ||
              new FileInfo(stderrAbsolutePath).Length > STDERR_MAX_BYTES) {
            outcome.Status = "BLOCK_OUTPUT_LIMIT";
            break;
          }
        }
        if (!childExited) {
          Demand(TerminateJobObject(job, 3), "BLOCK_TERMINATE_OWN_JOB");
          uint ended = WaitForSingleObject(child.hProcess, TERMINATION_CONFIRM_MS);
          outcome.ChildTerminationConfirmed = ended == WAIT_OBJECT_0;
          return outcome;
        }
        uint exitCode = 0;
        Demand(GetExitCodeProcess(child.hProcess, out exitCode),
          "BLOCK_GET_CHILD_EXIT");
        outcome.ExitCode = exitCode;
        outcome.Status = exitCode == 0 ? "PENDING_STDOUT_PROOF" : "BLOCK_CHILD_EXIT";
      } catch (Exception ex) {
        outcome.Status = "BLOCK_WATCHDOG_" + ex.GetType().Name;
      } finally {
        // A failed AssignProcessToJobObject leaves a suspended child which
        // belongs to THIS launcher, not SCM. Kill only that owned child.
        if (childCreated && !assigned && ValidHandle(child.hProcess)) {
          TerminateProcess(child.hProcess, 3);
        }
        if (childCreated && !childExited && assigned && ValidHandle(job)) {
          TerminateJobObject(job, 3);
        }
        if (childCreated && !childExited && ValidHandle(child.hProcess)) {
          uint ended = WaitForSingleObject(child.hProcess, TERMINATION_CONFIRM_MS);
          if (ended == WAIT_OBJECT_0) outcome.ChildTerminationConfirmed = true;
          else outcome.Status = "BLOCK_TERMINATION_UNCONFIRMED";
        }
        SafeClose(ref child.hThread);
        SafeClose(ref child.hProcess);
        SafeClose(ref job); // KILL_ON_JOB_CLOSE applies only to this job.
        SafeClose(ref stdin);
        if (attributeInitialized) DeleteProcThreadAttributeList(attrList);
        if (handlesArray != IntPtr.Zero) Marshal.FreeHGlobal(handlesArray);
        if (attrList != IntPtr.Zero) Marshal.FreeHGlobal(attrList);
        if (stdout != null) stdout.Dispose();
        if (stderr != null) stderr.Dispose();
        parentStreamsClosed = true;
      }
      if (parentStreamsClosed && outcome.Status == "PENDING_STDOUT_PROOF" &&
          outcome.ChildTerminationConfirmed && outcome.JobContainmentEstablished) {
        byte[] outBytes = File.ReadAllBytes(stdoutAbsolutePath);
        byte[] errBytes = File.ReadAllBytes(stderrAbsolutePath);
        if (outBytes.Length > STDOUT_MAX_BYTES || errBytes.Length != 0) {
          outcome.Status = "BLOCK_OUTPUT_BYTES";
        } else {
          string output = new UTF8Encoding(false, true).GetString(outBytes);
          string[] lines = output.Replace("\r\n", "\n").TrimEnd('\n').Split('\n');
          if (lines.Length == 3 &&
              lines[0] == "TTM_S1_IDLE_ACCEPT=PASS_COMPLETED_ABORTED" &&
              lines[1] == "TTM_S1_SILENT_READ=PASS_COMPLETED_ABORTED" &&
              lines[2] == "TTM_S1_VERDICT=PASS_ISOLATED_CANCELLATION_ONLY") {
            outcome.Status = "PASS_ISOLATED_S1_ONLY";
          } else {
            outcome.Status = "BLOCK_STDOUT_CONTRACT";
          }
        }
        outcome.StdoutSha256 = HashFile(stdoutAbsolutePath);
        outcome.StderrSha256 = HashFile(stderrAbsolutePath);
      }
      return outcome;
    }
  }
}
