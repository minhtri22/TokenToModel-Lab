
# Backlog: TTM width512 controlled scaling ablation

Date 2026-11-09. Status DEFERRED_RESEARCH. Do not run, alter current T4 model, GPU train or GGUF export under causal6.

Two separate interventions:
1. Only change token embedding from [2048,256] to [2048,512] but retain decoder hidden 256: requires 512->256 projector, adds 524,288 embedding rows worth of parameters if independent; a linear expansion of learned 256 vectors has rank <=256 and creates no novel information by itself.
2. Change both token embedding and Transformer d_model to 512: attention/MLP layers approximately 4x in parameters (quadratic in width); the 4M model may become around 14M tied parameters, exact count depends on source; old 256-width checkpoint cannot load unchanged into the wider decoder. A 2048x512 Gemma donor lookup can be consumed without dimensional reduction but token alignment/coordinate mismatch persists.

A future scientifically fair control is width512 TTM without donor versus width512 TTM with donor, same tokenizer/training/data/parameter budget controls. Do not infer donor semantics from width-only gains. Separate from current six-arm investigation of C2048 (width256).

Application inference/RAM/CPU/sampling and GGUF C2048 backlog remains separately DEFERRED.
