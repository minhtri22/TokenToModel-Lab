# TTM PR #12 - QA Windows HOLD: dependency selection and cleanup (2026-11-09)

**Ket luan:** `HOLD_QA_ENVIRONMENT_AND_CLEANUP`, khong phai `MODEL_FAIL`. Source of truth: GitHub PR #12; main/lineage khong sua.

## Bien ban goc bat bien
- **QA source head:** `871e421c254953d950a0d2ebb7263edd134eb7eb`.
- **Evidence commit:** `4fb7be402a71b19c4ca7e5d5aa8e314f29113a27`; 13 tep duoc doc lai GitHub PASS.
- **QA_RESULT.json**: static Python AST 34; JSON 22; 5 notebooks khong luu output; 15 source pins.
- **T1T3/T2/T4**: exit 1, stderr goc `C:\Users\minht\AppData\Local\Programs\azure-cli-venv\Scripts\python.exe: No module named pytest`. Day la `NOT_EXECUTED_TEST_DEPENDENCY`, khong phai thua test.
- **T5_V5**: 47/47 PASS; **T5 inference-only**: 12/12 PASS; **Q1Q2 frozen**: PASS.
- Script cu thuc hien `safe_cleanup` sau publish/readback ngay ca khi QA_RESULT=HOLD; Windows `WinError 5` khi xoa file `checkout/.git/objects/36/47c3465a34dfc89906d78a00de1e2a7dadbe46`. Chua du bang chung phan biet readonly attribute, ACL hay security software; khong thay doi ACL he thong.
- Thu muc `_tmp/TTM_PR12_QA_871e421c2549` va `CLAIM` giu nguyen; **khong rerun** cung RunID. Science T4, TEST64, Ollama native khong chay trong batch nay; `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED`.

## Sua ma chinh xac trong PR
1. PowerShell chon interpreter duoc kiem tra `pytest, numpy, torch, regex` + Python 3.11+ **truoc khi tao bootstrap/CLAIM**; cho phep `-PythonExe` explicit, khong auto-install. Khong dung `Get-Command python.exe` de mac dinh chon azure-cli-venv.
2. Python them mot lan check import truoc `run_dir.mkdir(exist_ok=False)`. Neu dependency thieu => HOLD_PRECLAIM, khong dot one-shot.
3. Chi dọn `run_dir` sau **PASS_SCOPED + commit + 13-file readback**. Neu HOLD thi giu lai toan bo. Khi PASS, retry dung file readonly Windows trong **exact claimed subtree** bang `chmod`; khong mo rong den tệp khac. Neu cleanup van loi thi bao `CLEANUP_HOLD`, khong ghi lai ket qua QA.
4. Hai tệp QA da sua tren PR; noi dung old-head khong ghi de. Khong sua ket qua khoa hoc hay `lineage.md`, khong huan luyen hay su dung TEST.

## QA va quyet dinh tiep theo
- `SOURCE_PATCH_STATIC_REVIEW=PASS_SCOPED`: hai chuoi SHA256 va Git blob duoc tinh tu nguon sau sua, source pins chinh xac, run guard da kiem tra bang static assertions.
- `WINDOWS_DYNAMIC_INTEGRATED_QA=PENDING`: can mot lan thuc thi moi tren HEAD moi va RunID moi, khong duoc coi la PASS khi chi static.
- `MERGE_DECISION=HOLD`: T1/T2/T4 chưa có actual pytest pass tren exact HEAD; source rights + final owner review chua dong.
- **Bước kế tiếp:** `TTM_PR12_PYTHON_DEPENDENCY_PREFLIGHT_AND_SINGLE_SUCCESSOR_QA`; khong lap lai RunID `871e421c2549`. Neu preflight khong co interpreter du yeu cau, dung va bao cao interpreter/dependency thieu, khong tu cai qua mang.

