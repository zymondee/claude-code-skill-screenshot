# localVoice

Local/offline voice tooling kept as pinned upstream checkouts, so this repo stays small
while the exact upstream revision is reproducible.

## VoiceStudio

- Upstream: https://github.com/debpalash/VoiceStudio
- Path: `localVoice/VoiceStudio` (git submodule, shallow)
- What it is: local voice cloning, video dubbing, dictation and long-form audio
  production — 16 TTS engines, 11 ASR engines, macOS/Windows/Linux/Docker.
  No account or API key needed for the local workflow; audio never leaves the machine.

### Fetch it

Fresh clone of this repo:

```bash
git clone --recurse-submodules <this-repo-url>
```

Already cloned:

```bash
git submodule update --init --depth 1 localVoice/VoiceStudio
```

VoiceStudio has its own nested submodule (`omnivoice-gallery`). It is not needed for
the core app; pull it only if you want the gallery:

```bash
git -C localVoice/VoiceStudio submodule update --init --depth 1 omnivoice-gallery
```

### Update to a newer upstream revision

```bash
git -C localVoice/VoiceStudio fetch --depth 1 origin main
git -C localVoice/VoiceStudio checkout FETCH_HEAD
git add localVoice/VoiceStudio && git commit -m "chore(localVoice): bump VoiceStudio"
```

### Setup

[`SETUP-APPLE-SILICON.md`](SETUP-APPLE-SILICON.md) — build-from-source checklist for
an Apple Silicon Mac with 16 GB, including which engines to pick, the Swedish
dictation path, and the memory setting to leave alone.

### Moving this to a private repo

`./localVoice/bootstrap-private-repo.sh [repo-name]` builds a standalone private
repo from this folder — same docs, VoiceStudio re-added as a submodule pinned to
the same upstream commit — and pushes it with `gh`. Without `gh` it stops and
prints the two manual commands. Clone it elsewhere with
`gh repo clone <name> -- --recurse-submodules`.

### Security audit

A review of this pinned commit for malicious code, outbound traffic, telemetry and
known vulnerabilities lives in [`security-audit/`](security-audit/) — English
markdown for reading and diffing, plus a Swedish PDF. Verdict: no malicious code
found; residual risks are structural (third-party model files, unsigned Windows
installers, `curl | sh` install) and documented with mitigations.

Re-run it after bumping the submodule — the findings are pinned to commit `eaf8bb9`.

### Install / run

Follow `localVoice/VoiceStudio/README.md` — it is the upstream source of truth for
install paths (desktop app, Docker, source) and hardware requirements.
