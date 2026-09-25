# Ha reprodukálható / pinelt build kell, a pontos verziót érdemes használni, pl.:
# ghcr.io/home-assistant/amd64-base-python:3.14-alpine3.24-2026.06.x (ami a 2026.júniusi release idején aktuális volt).
# https://github.com/home-assistant/wheels/actions/runs/28389244836
#   https://github.com/home-assistant/docker-base/pkgs/container/amd64-base-python/1149340342?tag=3.14-alpine3.24-2026.08.0
# docker pull ghcr.io/home-assistant/amd64-base-python:3.14-alpine3.24-2026.08.0

ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG \
    BUILD_ARCH \
    CPYTHON_ABI \
    # Ha saját wheels indexet használsz, cseréld ki:
    # PIP_EXTRA_INDEX_URL=https://wheels.home-assistant.io/musllinux-index/
    PIP_EXTRA_INDEX_URL="https://villgzs.github.io/musllinux-index/"

SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

COPY rootfs /

# Install requirements
RUN \
    --mount=type=bind,source=.,target=/usr/src/builder/,rw \
    apk upgrade --no-cache \
    && apk add --no-cache \
        rsync \
        openssh-client \
        patchelf \
        build-base \
        cmake \
        ninja \
        git \
        linux-headers \
        autoconf \
        automake \
        cargo \
        libffi \
    && apk add --no-cache --virtual .build-dependencies \
        libffi-dev \
    && pip3 install \
        -r /usr/src/builder/requirements.txt \
        -r /usr/src/builder/requirements_${CPYTHON_ABI}.txt \
        /usr/src/builder/

# Set build environment information
ENV \
    ARCH=${BUILD_ARCH} \
    ABI=${CPYTHON_ABI}

# Runtime
WORKDIR /data

ENTRYPOINT [ "run-builder.sh" ]
