# TTM T5 — One-shot compatibility V5 (PID0/TIME_WAIT fix)

Muc dich: chi kiem tra GGUF F32 TTM-Small-4M co nap duoc vao Ollama 0.40.14 va sinh toi da 32 token hay khong. KHONG kiem dinh tuong duong logits (FAIL 7/8 duoc giu nguyen).

## Goc sua
V4 dung truoc `ollama create`: HTTP GET `/api/version` da tra 200 nhung Windows giu dong TCP `PID=0, state=11 (TIME_WAIT)`. V4 nham dong nay thanh PID khac; sau do lai xem TIME_WAIT sau shutdown la server chua dung. V5 chi bo qua TIME_WAIT PID0 loopback co ket noi da ket thuc; PID khac, bind wildcard, listener con chay van HOLD. Khong gan state=0 thanh Listen.

## Pham vi
- Nguon chinh `t5_final_minimal_smoke_v5.py`; cong `12648`, model `ttm-t5-f32-compat-only-v5final:latest`.
- Evidence root moi `_tmp/ttm_t5_ollama_compat_only_single_v5final`, KHONG duoc ghi de, xoa, hay chay lai khi co `CLAIM.json`.
- GGUF va executable Ollama 0.40.14 khong thay doi; kho model va Ollama HOME rieng trong thu muc evidence TTM.
- V1, V2, V3 RC1 va V4 da CONSUMED, khong truy cap de sua. `lineage.md` chi ghi khoa hoc, khong ghi QA ha tang.
- `State=0` giu nguyen la UNKNOWN; readiness yeu cau PID dung, path dung, creation time dung, loopback dung, HTTP 200 phien ban 0.40.14, snapshot truoc/sau phu hop. Chi ignore dong `state=11 PID=0 TIME_WAIT` da dong ket noi local.
- Docker/GPU/driver, service 11434, PATH system khong bi thay doi. PATH loc thu muc ggml nghien cuu CHI trong process con.

## Cac lenh
Giai nen vao `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_T5_OLLAMA_V5_TIMEWAIT_GUARD_20261109`; chay PowerShell 5.1:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_T5_OLLAMA_V5_TIMEWAIT_GUARD_20261109\Invoke-TTM-T5-Timewait-V5-PS51.ps1' -Mode Preview
# Neu Preview PASS, CHI MOT LAN Smoke:
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_T5_OLLAMA_V5_TIMEWAIT_GUARD_20261109\Invoke-TTM-T5-Timewait-V5-PS51.ps1' -Mode Smoke
```

QA source 47/47 PASS tren assistant container voi mock; chua thuc hien Ollama that. Khi chay Windows, wrapper tu xac minh source SHA, origin repo, Python 3.12, 47 test mock va preview truoc khi claim. V5 one-shot sau khi claim duoc tinh CONSUMED ke ca FAIL.

Sau khi chay, gui `RESULT.json` va `READINESS_ATTEMPTS.jsonl` hoac console. KHONG dua toan bo `serve.log` hoac thu muc `home/.ollama` len GitHub vi co the chua SSH key.
