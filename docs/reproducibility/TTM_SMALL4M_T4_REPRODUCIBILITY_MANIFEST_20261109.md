# TTM-Small-4M T4 — Manifest tái lập (Reproducibility)

**Ngày:** 2026-11-09 · **Loại:** tài liệu tái lập, không thực thi huấn luyện/TEST mới.  
**Phán quyết:** REPRO_DOC=SCOPED · FULL_CLEAN_ROOM_REPRO=NOT_DEMONSTRATED · TEST_64=CONSUMED.

## 1. Nguồn sự thật và mã ghim

- [TTM GitHub](https://github.com/minhtri22/TokenToModel-Lab): main source pin tại thời điểm rà soát **b57b44e7287f842e81050c1faee337f636333dd0**. Nhánh tài liệu độc lập với PR #13.
- P02 decoder-only source Git blob SHA1 **9762343e06cf800b50574c2871ae1ed58537fb18**, đường dẫn src/p02/transformer_core.py.
- Colab T4 run thực: [A2 protocol](../pilot/TTM_T4_A2_CONTINUOUS_1024_STEPS_PROTOCOL_AMENDMENT_20261108.md) và [H1 formal adjudication](../pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md).
- TinyStories upstream: [roneneldan/TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories), revision **f54c09fd23315a6f9c86f9dc80f725de7d8f9c64**; chỉ TinyStories-train.txt và TinyStories-valid.txt. Không thay bằng TinyStoriesV2 hoặc parquet chuyển đổi.
- [TEST one-shot receipt](../pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md): một phép đo đã tiêu thụ, không được dùng để tune hoặc chạy lại.

## 2. Manifest vật liệu SHA-256

| Hiện vật | SHA-256 |
|---|---|
| TinyStories TRAIN raw | c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f |
| TinyStories VALID raw | 94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4 |
| T1 split manifest | 9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9 |
| BPE2048 TRAIN-only manifest | cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc |
| T4 private TRAIN/VAL pack | 184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913 |
| T4 private pack manifest | ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650 |
| Step1024 checkpoint | cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b |
| Step1280 exploratory continuation | ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc |
| T5 trained GGUF F32 from 1024 | 5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5 |

Các chuỗi SHA là dấu nhận dạng bytes, **không chứng minh quyền công bố**. Không tải tệp không rõ nguồn chỉ vì tên giống hiện vật. Tài liệu phát hành ở nhánh riêng không bao gồm checkpoint, tokenizer merge data hay private TRAIN/VAL/TEST.

## 3. Cấu hình run H1 có bằng chứng

| Thuộc tính | Giá trị |
|---|---|
| Model | 3.749.376 tham số, context256, embd256, 4 blocks, 4 heads, BPE2048, LayerNorm |
| Split | TRAIN 2048 stories, VAL 256, TEST 64 sealed; tokenizer fit từ 768 TRAIN |
| RunID | t4_science_4m_1024_a2_20261108_v1 |
| Seed | 20261108 |
| Optimizer/schedule | AdamW, peak LR 3e-4, warmup32, cosine xuống 3e-5, gradient clip 1.0 |
| Budget | 1024 optimizer steps, đúng 4096 valid target positions/step = 4.194.304 exposures |
| Platform | Google Colab Free Tesla T4, FP16, microbatch 8 windows, dynamic accumulation |
| VAL | 128-step cadence; chọn trước final step1024 cho primary H1 |
| Checkpoint | READY-last tại 256/512/768/1024; lưu model/optimizer/scheduler/sampler/cursor/RNG/GradScaler |
| H1 baseline | TRAIN-only bigram add-alpha=0.1; 1.000 story bootstrap rounds seed20261109 |

**Môi trường chính xác:** các lượt Colab đã ghi nhận Tesla T4 / torch 2.14.1+cu130 ở những hồ sơ liên quan, nhưng **không tự coi** phiên bản đó là pip freeze của run H1 nếu chưa đọc trực tiếp bản môi trường của run đó. Full clean-room bit-exact rerun trên máy/GPU khác là **NOT DEMONSTRATED**.

## 4. Lệnh kiểm tra chỉ đọc trên Windows PowerShell 5.1

Chỉ chạy từ project root đã biết; không ghi gì hoặc mở TEST. Dấu kiểm ở đây chỉ là phép kiểm nguồn, **không** huấn luyện.

~~~powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) {
    throw 'PROJECT_ROOT_NOT_GIT'
}
Push-Location -LiteralPath $root
try {
    $pin = 'b57b44e7287f842e81050c1faee337f636333dd0'
    $kind = (git cat-file -t $pin).Trim()
    if ($kind -ne 'commit') { throw 'PIN_MISSING' }
    $sourceRef = $pin + ':src/p02/transformer_core.py'
    $blob = (git rev-parse $sourceRef).Trim()
    if ($blob -ne '9762343e06cf800b50574c2871ae1ed58537fb18') {
        throw 'P02_BLOB_MISMATCH'
    }
    Write-Output 'PINNED_P02_SOURCE=PASS'
    $ckpt = Join-Path $root '_tmp\authorized_private\checkpoint_step1024.pt'
    if (Test-Path -LiteralPath $ckpt -PathType Leaf) {
        $actual = (Get-FileHash -LiteralPath $ckpt -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b') {
            throw 'CHECKPOINT_HASH_MISMATCH'
        }
        Write-Output 'CHECKPOINT_1024=PASS_EXACT'
    } else {
        Write-Output 'CHECKPOINT_1024=NOT_AVAILABLE'
    }
} finally {
    Pop-Location
}
~~~

**Lưu ý:** đường dẫn checkpoint là ví dụ; chỉ đọc file thật có quyền truy cập và nằm trong project root. Kiểm tra không ghi hoặc tải lại file. Không cho phép tự sao chép private data ra GitHub. Không đánh dấu PASS cho file không tồn tại.

## 5. Kết quả có và không có tính tái lập

**Đã có chứng cứ:** 1024-step T4 checkpoint READY SHA readback; H1 VAL model NLL 3.5223388517 được tính lại độc lập trên CPU (sai khác khoảng 5,2e-9); synthetic resume 20 vs 10+10 exact; exporter GGUF F32 52/52 tensors; Ollama create/import/generation thành công. TEST 64 chỉ chạy một lần; strict trained llama.cpp logits vẫn FAIL7/8.

**Chưa chứng minh:** bất kỳ người ngoài nào có thể dựng lại split/weights bằng GitHub public đơn độc; bit-exact 1024-step CUDA rerun; nhiều seed/robust prompt adherence; quyền phân phối mọi tệp nguồn/weights; sản phẩm thương mại. Step1280 thuộc thăm dò riêng, không thay checkpoint H1 đã chọn.

## 6. Ranh giới tái lập và thứ tự tiếp theo

Có thể thực hiện kiểm nguồn commit/blob SHA, metadata/manifest đối chiếu read-only, hoặc synthetic CPU QA đã khóa nếu người thực hiện có môi trường phù hợp. Muốn lấy/đóng gói TinyStories, tái dựng split, chạy Colab, mở TEST mới hoặc phân phối weights phải có hợp đồng và quyền riêng. Không chạy lại TEST pilot đã tiêu thụ, không sửa các receipt cũ.

**Bước thực hiện tiếp theo:** kiểm toán độc lập source-only và quyền phát hành; giữ nguyên training/TEST/lineage.  
REPRO_DOC=SCOPED · FULL_REPRO=HOLD · TEST_CONSUMED · MAIN_UNCHANGED.
