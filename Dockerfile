# Image de base Python
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers du projet dans le conteneur
COPY . .

# Créer le répertoire pour la base de données si nécessaire
RUN mkdir -p /app/data

# Exposer le port par défaut de Streamlit
EXPOSE 8501

# Définir les variables d'environnement pour Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Commande pour lancer l'application Streamlit
CMD ["streamlit", "run", "planning_gui.py", "--server.address=0.0.0.0"]
