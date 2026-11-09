# SOURCE PIN — TTM-Small × EmbeddingGemma2 64-step CPU adaptation
- **State before any training**: `SOURCE_PINNED_NOT_EXECUTED`.
- One scientific operation only: `ttm_small4m_gemma2_equal64_adapt_cpu_20261109_v1`.
- Preregistration committed **before source pin/training**: `efdc8fa8a3b71fa9e05b26821c22d39f88c3e22f`.
- Source runner `ttm_adapt64_cpu_once_20261109.py` SHA-256 **`e423daccc678d893947f93c13b2e8a12c8dca3a4875c5546f3a80131cd0d61ca`**.
- Complete source archive `TTM_SHORT_ADAPT64_CPU_RUNNER_SOURCE_20261109.zip` SHA-256 **`0db4efe16aa2dc68811e029b5d74d7baa6bc615802ea94d0e4b9f49f33f2cadf`**, 5634 bytes, uploaded *privately* to [owner Google Drive](https://drive.google.com/file/d/182Q3r71f6965mojeO-VhaRR5DL0O9Pfz/view).
- Runner reads only exact-hash-pinned TTM checkpoint + mapped Gemma candidate and TRAIN/VAL pack; does not use TEST, network downloads, RAG, Colab GPU, original T4 optimizer state, or modify past artifacts.
- Exactly 64 steps per arm × 512 target labels; same precomputed sampler for A/B/C/D. AdamW, constant LR, random control seed, bootstrap and loss were preregistered. Private per-story data/checkpoints must not be published in GitHub.
- Owner explicitly authorized this bounded comparison. No source/parameter adjustments after first CLAIM; any exception remains a preserved failed run, never automatic rerun.
