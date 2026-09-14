# Security audit — VoiceStudio

| | |
|---|---|
| **Target** | [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) |
| **Commit** | `eaf8bb953855cab3b687d547b3835f86fa38b308` |
| **Scope** | 2 240 tracked files · license AGPL-3.0 |
| **Date** | 2026-09-13 |
| **Verdict** | **No malicious code found.** Residual risks are structural, not intentional. |

Swedish reader-facing version: [`VoiceStudio-sakerhetsgranskning.pdf`](VoiceStudio-sakerhetsgranskning.pdf).
Regenerate it with `python3 generate-report.py` (needs `reportlab` and DejaVu fonts).

---

## 1. Method and results

Pattern search across the full tree plus targeted reading of the security-critical
modules. Not a line-by-line read of every file — see [Limitations](#7-limitations).

| Area | Looked for | Result |
|---|---|---|
| Install hooks | `preinstall` / `postinstall` / `prepare` in every `package.json` — the classic npm hijack vector | **Clean** — zero occurrences |
| Droppers | `curl … \| bash` to unknown hosts, `base64 -d` piped to a shell, decode-then-`exec` | **Clean** — every hit is a documented installer targeting the project's own or well-known domains (`voicestudio.sh`, `astral.sh`, `bun.sh`) |
| Code execution | `eval()`, `exec()`, `os.system()`, `shell=True`, `pickle.loads`, unsafe `yaml.load` | **Clean** — no hits in backend or scripts (the `.eval()` matches are PyTorch eval mode) |
| Credential theft | `~/.ssh`, `.aws/credentials`, `.netrc`, keychain, browser cookies, wallet files | **Clean** — no hits |
| Outbound traffic | Every domain in executable code (py/js/ts/rs/sh/ps1) enumerated and classified | **Clean** — Hugging Face, PyTorch, GitHub, own domains, opt-in telemetry only |
| Committed binaries | ELF / Mach-O / PE files anywhere in the tree | **Clean** — none |
| CI supply chain | `pull_request_target` / `workflow_run` checking out PR code ("pwn request"), broadly scoped secrets | **Clean** — the pattern is not used; secrets appear only in release/docker/evals |
| Network exposure | Default bind address, CORS, API authentication | **Clean** — loopback by default; LAN sharing is opt-in and PIN-gated |
| Deserialization | `torch.load()` without `weights_only` (pickle ⇒ arbitrary code execution) | **2 hits**, both in `omnivoice/eval/` research tooling — see risk #4 |

## 2. What actually leaves the machine

The claim "no audio ever leaves your computer" holds, and is enforced harder than
the marketing copy suggests. Telemetry exists (PostHog, EU host
`eu.i.posthog.com`) but is **off by default** and structurally unable to leak content:

- **Two independent gates** must both be true: a configured destination *and* the
  user's explicit preference. The code default is `False`.
- **Hard kill switch**: `OMNIVOICE_ANALYTICS_DISABLED=1` outranks both gates.
- **Allowlist in code, not in a policy document.** ~15 fields may pass
  (engine id, language, seconds, *character count* — never the text, never file
  names, never voice names). Anything not on the list is dropped.
- **Autocapture and session recording explicitly disabled.** The SDK default would
  otherwise transmit the text of whatever the user clicks — in this app, the script
  about to be synthesized.
- **Stack traces deliberately not captured** — they can carry absolute paths and
  Hugging Face tokens. Only the exception *class name* is sent.
- **Identity** is a random per-install UUID, not derived from hardware, hostname
  or username.
- The uninstall script sends one final `app_uninstalled` event **only** if the user
  had opted in; otherwise nothing is sent and nothing is printed.

The committed PostHog project token is intentional and harmless: it is a
*publishable*, write-only ingestion key that names a destination and cannot read data.

## 3. Previously reported findings

No published GitHub Security Advisories, no CVEs, and no user reports of malicious
code or data exfiltration. Real findings exist and are fixed — which is a good sign,
not a bad one:

| Finding | Impact | Status |
|---|---|---|
| Admin routes reachable unauthenticated (#1213) | In server mode a trusted-network client could reach `/system/*` and `/api/settings/*` without a credential. The project classes these routes as "RCE-class". The short share PIN also granted admin. | **Fixed** in v0.4.0 — API key or genuine loopback required |
| 35 + 5 dependency advisories (#1456, #2030, #2031) | Python and Rust dependency CVEs; protobuf/transformers in CosyVoice 3 | **Fixed** by upgrades |
| Invalid voice profile could be persisted (#1141) | Free-form text in a profile field persisted a profile that failed every later generation — "re-exploited three times through different clients" | **Fixed** — server sanitizes all profile kinds |
| Unsigned installers on Windows and macOS (#1712, #134, #72) | Windows: no Authenticode signature, SmartScreen warns. macOS: ad-hoc signed but not notarized, so Gatekeeper blocks the first launch. Neither publisher can be cryptographically verified. | **Not planned / unfunded** — Windows signing is declined; macOS notarization needs a paid Apple Developer account |
| Missing watermark in API (#1169) | `/v1/audio/speech` returned unwatermarked audio — EU AI Act Art. 50(2) compliance, not an attack vector | **Fixed** |

## 4. Residual risks, ranked

1. **Third-party model files — largest.** The app downloads models from Hugging
   Face. A `.pt`/`.bin` file is pickle-serialized Python and can execute code on
   load. This is an ecosystem problem, not this project's.
   *Mitigation:* stick to the engines the app offers. The project's own
   `SECURITY.md` states it plainly: no privately distributed model archives, never
   run executables bundled with a model archive.
2. **Unsigned Windows installer.** Only the checksum can be verified, not the publisher.
   *Mitigation:* on Windows, build from source, or verify SHA256 against the
   release `checksums` file. macOS is **also** unsigned in the Apple sense — the
   DMG is ad-hoc code-signed but **not notarized** (the release workflow is wired
   for it and activates only once Apple Developer secrets are set), so Gatekeeper
   blocks the first launch and the same SHA-256 check applies there.
3. **`curl … | sh` install.** `scripts/install.sh` does verify SHA256, but
   `verify_sha256()` returns 0 with a warning when neither `shasum` nor
   `sha256sum` exists, and the checksum file comes from the same origin as the
   binary (so it protects against corruption, not a compromised release).
   *Mitigation:* download the script, read it, then run it — or build from source.
4. **`torch.load()` without `weights_only`** in `omnivoice/eval/speaker_similarity/sim.py`
   and `omnivoice/eval/mos/utmos.py`. Not on the app's normal code path; these are
   quality-measurement research tools.
   *Mitigation:* irrelevant if you only run the app. Do not point the eval tools at
   untrusted checkpoints.
5. **LAN sharing** binds a second server to `0.0.0.0` — but only when explicitly
   enabled, and it is PIN-gated.
   *Mitigation:* enable only on trusted networks; never expose the port to the
   internet without an API key.
6. **Dependency advisories are non-gating in CI.** `pip-audit` and `bun audit`
   report but do not block a PR; only the secret scan gates.
   *Mitigation:* a deliberate trade-off by the project. Update regularly — they do
   clear advisories in practice.

## 5. Positive signals

- **Its own SSRF test suite.** `tests/test_gptsovits_endpoint_security.py` attempts
  to make the app reach `169.254.169.254` (the cloud metadata endpoint — classic
  credential theft) and simulates **DNS rebinding**, where a host resolves to
  `127.0.0.1` first and something else afterwards. That is not beginner-level.
- **Secret scanning gates merges.** gitleaks is a hard gate in CI; CodeQL, bandit
  and dependency auditing run on every PR and weekly.
- **Layered authorization model** — anonymous, loopback, trusted network, PIN,
  API key, admin session — rather than one boolean.
- **Redaction throughout**: dedicated modules for error sanitization
  (`core/failure.py`), path security, CSRF and diagnostic bundles. HF tokens are
  redacted out of logs.
- **Public security policy** with a private reporting channel and an explicit
  model-supply-chain stance.
- **AGPL-3.0** — no open-source-washing with commercial add-on clauses.

## 6. Recommendation

Safe to run, with three habits:

1. Run from source (the submodule in `localVoice/VoiceStudio`), or verify SHA256
   when pulling a release.
2. Leave telemetry off — it already is. For certainty, set
   `OMNIVOICE_ANALYTICS_DISABLED=1`.
3. Never add a model file from a private source. It is the one way in the project
   cannot close for you.

## 7. Limitations

Pattern search over 2 240 files plus targeted reading of the security-critical
paths — not a line-by-line review of the whole codebase. A well-hidden backdoor in
a single engine integration could evade this method. Probability is low given the
project's openness, CI chain and active review bots, but it is not zero.

## Sources

- Local review of commit `eaf8bb9`
- `CHANGELOG.md`, `.github/SECURITY.md`, `.github/workflows/security.yml`
- GitHub Security Advisories for the repository (empty)
- The project's public issue history
