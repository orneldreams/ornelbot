# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port (Streamlit par défaut : 8501)
EXPOSE 8501

# Commande de démarrage
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
