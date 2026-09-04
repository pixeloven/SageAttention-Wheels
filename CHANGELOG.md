# Changelog

This repo repackages [thu-ml/SageAttention](https://github.com/thu-ml/SageAttention)
as prebuilt wheels. **The version here is ours, not upstream's** — it describes
this build, so a rebuild of the same upstream release is a patch bump.

Which upstream release, Torch, CUDA and GPU architecture a wheel targets is in
its filename and its `BUILD-INFO`, which is where that belongs — a tag cannot
carry five axes without becoming unreadable.

## 1.0.0 — 2026-09-04

First semver release. The wheels themselves are unchanged; what changes is that
they can now be depended on by version.

Previously the tag *was* the compatibility tuple —
`sageattention-v2.2.0-cu130-torch2.13.0` — with no room to express "same target,
rebuilt". A rebuild therefore reused the tag, and the guard meant to prevent
that compared `BUILD-INFO`, which records only the tuple. So a rebuild from a
**changed build script** produced identical `BUILD-INFO`, passed the guard, and
reached `gh release upload --clobber`, replacing wheel bytes under a tag
consumers pin by URL.

- Releases are cut from a `vX.Y.Z` tag, and CI refuses a tag that disagrees with
  `VERSION`.
- Publishing is refused outright if that release already exists. There is no
  clobber path left, so the guard cannot be blind — a rebuild is a new version.
- `workflow_dispatch` still builds any tuple for experimentation, but no longer
  publishes.
- Release assets keep the tuple: wheels, `SHA256SUMS-*`, `BUILD-INFO-*` and
  `TOOLCHAIN-*` per architecture.

Targets SageAttention v2.2.0 · Torch 2.13.0 · cu130 · sm80, sm86, sm89, sm90, sm120.
