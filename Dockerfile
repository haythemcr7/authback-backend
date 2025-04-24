# Utilise une image Python officielle
FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers
COPY . .

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port utilisé par Flask
EXPOSE 5000

# Lancer l'application
CMD ["python", "run.py"]

