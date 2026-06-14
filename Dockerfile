FROM python:3.9-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        gdal-bin \
        libgdal-dev \
        libgeos-dev \
        libproj-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel \
    && grep -v "^twisted-iocpsupport==" requirements.txt > requirements-linux.txt \
    && python -m pip install --prefix=/install "GDAL==$(gdal-config --version)" \
    && python -m pip install --prefix=/install -r requirements-linux.txt


FROM python:3.9-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    IN_DOCKER=1 \
    GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so.32

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgdal32 \
        libgeos-c1v5 \
        libproj25 \
        libpq5 \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

RUN mkdir -p /app/logs /app/staticfiles /app/img

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "project.asgi:application"]
