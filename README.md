# SageAttention Wheels

Reproducible Linux wheels built from pinned
[`thu-ml/SageAttention`](https://github.com/thu-ml/SageAttention) source commits.

This repository contains packaging and release automation only. It does not
carry a modified copy of SageAttention. Keeping the wheel pipeline separate
from the source fork makes the provenance of every binary explicit and lets
the `pixeloven/SageAttention` fork track the canonical project directly.

## Scope

- Linux x86-64 wheels for ComfyUI container images
- Explicit SageAttention, Python, PyTorch, and CUDA versions
- CUDA architectures selected at build time
- Import validation before an artifact can be published
- GitHub artifact attestations for produced wheels

Windows wheels are currently maintained by
[`woct0rdho/SageAttention`](https://github.com/woct0rdho/SageAttention/releases)
and are intentionally not duplicated here.

## Build a wheel

Run the **Build Linux wheel** workflow and provide the desired compatibility
tuple. Its defaults follow the current PixelOven ComfyUI CUDA image:

| Input | Default |
| --- | --- |
| SageAttention ref | `v2.2.0` |
| Python | `3.12` |
| PyTorch | `2.13.0` |
| PyTorch index | `cu130` |
| CUDA toolkit | `13.0.2` |
| CUDA architectures | `8.0;8.6;8.9;9.0;12.0` |

Upstream SageAttention v2.2.0 compiles kernels only for compute capabilities
8.0, 8.6, 8.9, 9.0, and 12.0 and silently ignores anything else in
`TORCH_CUDA_ARCH_LIST`; the build fails fast if the architecture list requests
an unsupported entry. GPUs with another capability of a supported major
version, such as sm_121, execute the sm_120 kernels.

The workflow resolves the requested ref through the canonical repository and
passes the immutable commit SHA to the build. The resulting package version
includes the CUDA and PyTorch compatibility tuple, for example:

```text
sageattention-2.2.0+cu130.torch2.13.0-cp312-cp312-linux_x86_64.whl
```

Publishing a GitHub release is an explicit workflow option. Manual runs
produce an attested workflow artifact without changing release state unless
publishing is selected.
Pull requests build and import-test the default compatibility tuple, then
upload the wheel as a workflow artifact without attesting or publishing it.

## Compatibility

These wheels contain compiled PyTorch/CUDA extensions. Python wheel tags alone
do not guarantee compatibility: use a wheel built for the exact PyTorch and
CUDA channel used by the target image. A successful import validates linkage,
but inference correctness and performance still require testing on the target
GPU architecture and representative ComfyUI workflows.

## Relationship to SageAttention

SageAttention is developed by the
[`thu-ml/SageAttention`](https://github.com/thu-ml/SageAttention) project. This
repository is an independent binary packaging project and is not an official
SageAttention distribution.
