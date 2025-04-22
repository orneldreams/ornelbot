FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requis
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Définir le port par défaut (utile en local)
ENV PORT=8501

# Commande de démarrage Streamlit avec les bonnes options
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]