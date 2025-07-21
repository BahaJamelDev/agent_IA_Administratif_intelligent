# Étape 1 : choisir une image Python officielle
FROM python:3.11

# Étape 2 : définir le répertoire de travail
WORKDIR /app

# Étape 3 : copier tout le code source dans le conteneur
COPY . .

# Étape 4 : installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : lancer le script principal (ex : main.py ou API)
CMD ["python", "master_agent.py"]
