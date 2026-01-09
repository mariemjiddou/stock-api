FROM python:3.10-slim

WORKDIR /app

# Installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Exposer le port
EXPOSE 8000

# Lancer l'API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
