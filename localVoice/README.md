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

### Install / run

Follow `localVoice/VoiceStudio/README.md` — it is the upstream source of truth for
install paths (desktop app, Docker, source) and hardware requirements.
