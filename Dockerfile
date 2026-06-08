# Base Python
FROM python:3.9-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV IN_DOCKER=1

# Variables pour GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so.36

# Répertoire de travail
WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    gcc \
    g++ \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/lib/x86_64-linux-gnu/libgdal.so.36 /usr/lib/libgdal.so

# Récupérer la version GDAL installée (pour GDAL Python)
RUN gdal-config --version

# Copier requirements et installer
COPY requirements_linux.txt ./

RUN pip install --upgrade pip

# Installer GDAL Python en fonction de la version système
RUN pip install GDAL==$(gdal-config --version)

# Installer les autres dépendances (sans GDAL dans le fichier !)
RUN pip install -r requirements_linux.txt

# Copier le projet
COPY . .

# Exposer le port pour Django
EXPOSE 8000

# Commande par défaut pour Channels + Daphne
CMD ["python", "-m", "daphne", "-b", "0.0.0.0", "-p", "8000", "project.asgi:application"]