```
docker run --rm -it --platform linux/arm/v7 --entrypoint /bin/bash ghcr.io/villgzs/wheels32bit/armv7/musllinux_1_2/cp314:a66b24f4dc6645d1f1173b897c613ac85a301fd0
```

```
apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    yaml-dev \
    nasm \
    zlib-ng-dev \
    zlib-dev \
    jpeg-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    re2-dev \
    bluez-dev \
    glib-dev \
    eudev-dev \
    libxml2-dev \
    libxslt-dev \
    libpng-dev \
    libjpeg-turbo-dev \
    gmp-dev \
    mpfr-dev \
    mpc1-dev \
    ffmpeg-dev \
    openblas-dev \
    fftw-dev \
    lapack-dev \
    gfortran \
    blas-dev \
    eigen-dev \
    glew-dev \
    harfbuzz-dev \
    hdf5-dev \
    libtbb-dev \
    mesa-dev \
    openexr-dev \
    uchardet-dev
```

```
apk add --no-cache libtool automake autoconf
```


```
git clone --depth 1 --branch v0.16.3 https://github.com/lexiforest/curl_cffi.git
cd curl_cffi

# patch a detect_arch-ba (fentebb)
sed -i 's/libc = glibc_flavor if libc == "glibc" else "musl"/libc = "gnueabihf" if uname.machine in ["armv7l", "armv6l"] else (glibc_flavor if libc == "glibc" else "musl")/' scripts/build.py

make preprocess
pip wheel . --no-deps -w ../dist/
```

```
find / -type f -name "*.whl"
```

```
auditwheel repair ../dist/curl_cffi-0.16.3-cp310-abi3-linux_armv7l.whl -w ./wheelhouse/
```
