FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# PORT par défaut pour dev local
ENV PORT=8501

# ✅ Commande en ligne unique (shell mode)
CMD sh -c "streamlit run app.py --server.port=\${PORT:-8501} --server.address=0.0.0.0"
