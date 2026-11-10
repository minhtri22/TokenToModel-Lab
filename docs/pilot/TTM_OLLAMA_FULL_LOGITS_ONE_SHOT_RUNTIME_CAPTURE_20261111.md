# TTM — Ollama full logits: isolated one-shot FL01–FL04

Source branch: research/ttm-t5-ollama-full-logits-20261111 (not main). Build candidate 818fec27008b0a8555ecbae09c8c95e6a076d2b2fa4c26377b8bdb248232210a passed in owner Windows build; read-only RemoteDesktop inspected the original receipt. No inference yet.

Frozen reference 4 × 2048, SHA256 1e098a643c9bce66431adf3dc0296ce6b628731d33c4532753d2f2acd664d082; seal SHA256 571a1a654bad1b97de066d6fb3b690e910ecc71777deb4b16b7b15968f444939. Neither TEST, retraining nor previous T5 v5 are touched.

Windows PowerShell launcher: tools/ollama_full_logits_v1/Invoke-TTM-Ollama-FullLogits-Once-PS51.ps1. Runs eight no-model tests then one owner Windows Python 3.12 process. Validates exact Git head, build receipt, candidate runner, Ollama executable, existing GGUF and full reference hashes. Fresh stage is _tmp/fl3 and cannot be overwritten; port 127.0.0.1:12651 must be free.

Copy original v5 local model registry into stage, run only private candidate Ollama CLI with local HOME, OLLAMA_MODELS, no cloud, no GPU, KV F32, Flash off, one thread, context 256. Send exactly FL01, FL02, FL03, FL04 with raw=true, stream=false, temperature 0, one token requested. After each HTTP call require a new raw JSONL row, exact fixture token IDs, 2048 finite values, raw logits before sampler. While parent is live, independently inspect child PID, parent PID, path and flags using Windows CIM, require same child on four requests and observed F32/Flash-off in logs. Terminate only the owned process tree.

After all four rows, use frozen independent_full_logits_audit.py to measure every logit, per-fixture max-abs <=0.001 and top1 equal. Keep numeric PASS/FAIL distinct from independent process-provenance adjudication. Preserve _tmp/fl3 raw data, log, receipt and SHA. If any failure, HOLD without automatic replay, preserve any partial evidence.

Initial decision: INFERENCE_NOT_EXECUTED. Next action: run the one-shot after offline QA, inspect receipt and raw evidence and then create independent numerical and provenance adjudication, never modify T5 v5 or main.