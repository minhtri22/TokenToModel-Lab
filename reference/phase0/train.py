"""Reference byte-token next-token trainer. Use real data for meaningful learning."""
import argparse
from dataclasses import asdict
import torch
from model import GPT, GPTConfig


def main():
    p = argparse.ArgumentParser()
    p.add_argument("text_file", help="UTF-8 training text; no external downloads")
    p.add_argument("--steps", type=int, default=50)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--seq-len", type=int, default=32)
    p.add_argument("--device", default="cpu", choices=["cpu", "cuda", "xpu"])
    p.add_argument("--checkpoint", default="gpt_reference.pt")
    args = p.parse_args()
    torch.manual_seed(2026)
    cfg = GPTConfig(max_seq_len=max(args.seq_len, 32))
    model = GPT(cfg).to(args.device).train()
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4)
    data = torch.tensor(list(open(args.text_file, "rb").read()), dtype=torch.long)
    if len(data) < args.seq_len + 2:
        raise ValueError("training data must exceed seq_len + 1 bytes")
    for step in range(args.steps):
        start = torch.randint(0, len(data) - args.seq_len - 1, (args.batch_size,))
        x = torch.stack([data[i:i + args.seq_len] for i in start]).to(args.device)
        y = torch.stack([data[i + 1:i + args.seq_len + 1] for i in start]).to(args.device)
        _, loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step == 0 or (step + 1) % max(1, args.steps // 5) == 0:
            print(f"step={step + 1:4d} loss={loss.item():.4f}")
    torch.save({"config": asdict(cfg), "model": model.state_dict()}, args.checkpoint)
    print(f"CHECKPOINT={args.checkpoint}")


if __name__ == "__main__":
    main()
