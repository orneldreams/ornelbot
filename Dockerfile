FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Juste à titre de fallback local (non requis si Railway gère déjà PORT)
ENV PORT=8501  

# ✅ Bonne version du CMD :
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
