# VoiceStudio on Apple Silicon — setup checklist

Target: Mac Mini, Apple Silicon, 16 GB unified memory, macOS 13.3+.
Pinned upstream commit: `eaf8bb9` (see [`security-audit/`](security-audit/) for the
review of that exact commit).

## Why build from source

The released DMG is ad-hoc code-signed but **not notarized**, so Gatekeeper blocks
the first launch and the publisher cannot be verified. Building from source removes
that question entirely — you compile what you can read. It also matches the
recommendation in the security audit.

If you'd rather take the DMG: download `VoiceStudio.Studio_<version>_aarch64.dmg`
(not `x64`), verify it against the `.dmg.sha256` on the release page, then
right-click → **Open**. On macOS 15 Sequoia: double-click once, then
System Settings → Privacy & Security → **Open Anyway**.

Do **not** use Docker on this machine: images are `linux/amd64` only and the
container cannot reach the Apple GPU through MPS or MLX.

## 1. Toolchain

```bash
xcode-select --install                       # git + C toolchain
brew install python@3.11 rust                # or pyenv, if you already have 3.11+
curl -fsSL https://bun.sh/install | bash     # Bun
```

Reopen the terminal (or `source "$HOME/.cargo/env"`) after installing rustup.

FFmpeg is **not** a prerequisite — the app resolves its own checksummed build.
If you'd rather it used your Homebrew copy, point it there in
**Settings → Audio tools** after first launch.

## 2. Build and launch

```bash
git submodule update --init --depth 1 localVoice/VoiceStudio
cd localVoice/VoiceStudio
bun install
bun run desktop-prod
```

First launch builds the Tauri shell, creates the Python venv via `uv`, syncs
dependencies and downloads ~2.4 GB of model weights. Budget ~10 GB of disk and
watch the splash screen for per-step progress. Later launches reuse both.

## 3. Engines to pick

| Role | Choose | Why |
|---|---|---|
| TTS | **MLX-Audio**, or OmniVoice on MPS | Neural Engine + Metal; roughly 2× the CPU path |
| ASR | **MLX Whisper**, plus **Parakeet TDT v3 (MLX)** for dictation | ~2 GB unified memory, word timestamps |

**Swedish dictation works.** `sv` is in Parakeet's 25-language set
(`backend/services/asr_backend.py`, `_PARAKEET_MLX_LANGS`), so with a Swedish
system language the app auto-prefers Parakeet once you install its weights from
**Model Catalogue → ASR → Weights**. It is never downloaded without that.

**Never force WhisperX here.** It is built on CTranslate2, which has no Metal
backend at all — it would run whisper-large-v3 on the CPU. The project's own
measurement on an M2: 90 s per 30-second chunk on CPU versus 20 s on GPU, and the
slowest chunks blew past the per-chunk timeout and were dropped, leaving holes in
the transcript. The app picks MLX on Apple Silicon by itself; let it.

## 4. The 16 GB caveat

16 GB is the configuration this project has historically struggled with. The
"Can't reach the local backend" errors on such machines were never networking —
the backend was being OOM-killed, because two TTS engines could end up resident at
once (the core model and the switched-to engine lived in separate caches).

That is fixed: only one TTS engine stays resident.

> **Leave `OMNIVOICE_SINGLE_ENGINE_RESIDENT` alone.** It defaults to `1`, which is
> what you want. Setting it to `0` re-enables keeping several engines warm and puts
> you back in OOM territory on 16 GB.

Expect a re-load when A/B-switching engines (~8 s for the core, 1–2 s for the
lighter ones). That is the trade you want here.

## 5. Optional

- **Hugging Face token** — not needed to start, but diarization
  (`pyannote/speaker-diarization-3.1`) is gated. Wanted if you plan to dub video
  with multiple speakers. Settings → API Keys, or `export HF_TOKEN=hf_…` in `~/.zshrc`.
- **Self-check** if anything fails: Settings → About → Run self-check, or
  `uv run python backend/main.py --diagnose --deep`.

## Keeping it current

The submodule is pinned. To move to a newer upstream revision:

```bash
git -C localVoice/VoiceStudio fetch --depth 1 origin main
git -C localVoice/VoiceStudio checkout FETCH_HEAD
git add localVoice/VoiceStudio && git commit -m "chore(localVoice): bump VoiceStudio"
```

Re-run the security audit after a bump — its findings are pinned to `eaf8bb9`.
