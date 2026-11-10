# CAUSAL6 — Pre-CLAIM CUDA smoke: sửa nhầm logits thành loss vô hướng

**Ngày:** 2026-11-10 · **RunID:** `ttm_small4m_gemma2_causal6_2048x4096_free_t4_20261109_v1`.

## Lỗi được xác nhận

Owner đã có Tesla T4: PyTorch CUDA 2.14.1+cu130, 14.56317138671875 GiB, nguồn Python đã vá ngưỡng 14 GiB, ZIP/H512 đã niêm phong. Preflight tiến vào `gpu_smoke` rồi dừng tại `require(bool(torch.isfinite(l)))` vì `l,_=model(x,y)` trả về **logits tensor** (nhiều phần tử), không phải loss vô hướng. Mã huấn luyện khóa gốc đang dùng `logits,_=m(x)` và tính loss `F.cross_entropy` riêng biệt.

## Sửa đúng phạm vi

```python
# Old:
l,_=model(x,y)
require(bool(torch.isfinite(l)),'SMOKE_LOSS_FINITE')
l.backward()
# New:
logits,_=model(x)
l=F.cross_entropy(logits.float().reshape(-1,2048),y.reshape(-1),reduction='mean')
require(bool(torch.isfinite(l).item()),'SMOKE_LOSS_FINITE')
l.backward()
```

Số nhãn trong synthetic smoke là 8×256 = 2048 và đều hợp lệ; cross-entropy mean là loss vô hướng giống chia tổng loss cho số nhãn hợp lệ. Không dùng dữ liệu H512 hoặc T4 TRAIN thật trong smoke. Kiểm thử CPU với mô hình giả có hợp đồng `(logits, aux)`: forward, loss finite scalar, backward, gradients **PASS**. Chưa thực hiện lại smoke trên Tesla T4 thật.

**SHA256 nguồn runner trước sửa:** `bf1da76016e134e21c4d21eb7b972fd98cf8563deca965e50bacef457a590e32`. **SHA256 sau sửa:** `84e1377ad526c7822bfe025f9728e91a133fee66483b4dcd8127989bb6360cd4`. **Git blob SHA1 của mã sau sửa:** `f4d25f174c80058aa49eb6102465239a4a4e6a7a`.

## Những gì tuyệt đối không đổi

Không thay nguồn checkpoint, tokenizer, donor, H512, seed, sampler, optimizer, số bước và target budget, kết quả L0017/L0018, mã kiểm độc lập hay output run directory. Cổng thử GPU `max_memory_allocated < 12 GiB`, Tesla T4 duy nhất, GPU >=14 GiB, Drive >=4 GiB và các kiểm tra parity SHA vẫn giữ nguyên. Mã phiên Colab được vá chỉ khi SHA cũ khớp, sau đó phải xác nhận SHA mới, chạy lại preflight trước CLAIM. **Không tự động chạy ô science**.

**Trạng thái:** `GPU_SMOKE_PATCH=SOURCE_COMMITTED` · `REAL_T4_RECHECK=PENDING` · `SCIENCE_CLAIM=NOT_CREATED_BY_THIS_PATCH` · `LINEAGE=UNCHANGED`.
