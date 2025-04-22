import os
import subprocess

# Utilise la variable d’environnement PORT injectée par Railway
port = os.getenv("PORT", "8501")

subprocess.run([
    "streamlit", "run", "app.py",
    "--server.address", "0.0.0.0",
    "--server.port", port
])
