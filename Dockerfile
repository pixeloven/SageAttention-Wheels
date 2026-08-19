# syntax=docker/dockerfile:1.7

ARG CUDA_VERSION=13.0.2
FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu24.04 AS builder

ARG SAGE_COMMIT
ARG PYTHON_VERSION=3.12
ARG TORCH_VERSION=2.13.0
ARG TORCH_INDEX=cu130
ARG CUDA_ARCH_LIST="8.0;8.6;8.9;9.0;12.0"

RUN test -n "${SAGE_COMMIT}"

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        ninja-build \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python${PYTHON_VERSION}-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python${PYTHON_VERSION} -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN python -m pip install --upgrade "pip==26.2.1" \
    && python -m pip install \
        "packaging==23.2" \
        "setuptools==74.1.3" \
        "wheel==0.43.0" \
        "ninja==1.13.0" \
    && python -m pip install \
        --index-url "https://download.pytorch.org/whl/${TORCH_INDEX}" \
        "torch==${TORCH_VERSION}"

RUN git clone https://github.com/thu-ml/SageAttention.git /src \
    && git -C /src checkout --detach "${SAGE_COMMIT}" \
    && test "$(git -C /src rev-parse HEAD)" = "${SAGE_COMMIT}"

COPY scripts/prepare_source.py /usr/local/bin/prepare-source

RUN python /usr/local/bin/prepare-source \
        --source /src \
        --local-version "${TORCH_INDEX}.torch${TORCH_VERSION}" \
        --arch-list "${CUDA_ARCH_LIST}"

ENV TORCH_CUDA_ARCH_LIST="${CUDA_ARCH_LIST}"
ENV MAX_JOBS=1

RUN cd /src \
    && python setup.py bdist_wheel \
    && python -m pip freeze --all > /src/dist/TOOLCHAIN.txt

FROM builder AS test

RUN python -m pip install --force-reinstall --no-deps /src/dist/*.whl \
    && cd /tmp \
    && python -c "import sageattention; print(sageattention.__file__)"

FROM scratch AS export

COPY --from=test /src/dist/ /
