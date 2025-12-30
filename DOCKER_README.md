# Planning Obeya - Docker

Ce document explique comment utiliser Planning Obeya avec Docker.

## Prérequis

- Docker Desktop installé sur votre machine Windows
- Télécharger depuis : https://www.docker.com/products/docker-desktop/

## Utilisation avec Docker Compose (Recommandé)

### 1. Lancer l'application

```bash
docker-compose up -d
```

L'application sera accessible sur : http://localhost:8501

### 2. Arrêter l'application

```bash
docker-compose down
```

### 3. Voir les logs

```bash
docker-compose logs -f
```

## Utilisation avec Docker seul

### 1. Construire l'image

```bash
docker build -t planning-obeya .
```

### 2. Lancer le conteneur

```bash
docker run -d -p 8501:8501 -v "%cd%/data:/app/data" --name obeya planning-obeya
```

Sur Windows PowerShell, utilisez `${PWD}` au lieu de `%cd%` :
```powershell
docker run -d -p 8501:8501 -v "${PWD}/data:/app/data" --name obeya planning-obeya
```

### 3. Arrêter le conteneur

```bash
docker stop obeya
docker rm obeya
```

## Persistance des données

Les données de la base de données sont sauvegardées dans le dossier `./data` sur votre machine hôte. Même si vous supprimez le conteneur, vos données seront conservées.

## Mise à jour de l'application

1. Arrêter et supprimer le conteneur actuel :
```bash
docker-compose down
```

2. Reconstruire l'image avec les nouvelles modifications :
```bash
docker-compose up -d --build
```

## Partage de l'image

### Sauvegarder l'image Docker

```bash
docker save planning-obeya > planning-obeya.tar
```

### Charger l'image sur un autre PC

```bash
docker load < planning-obeya.tar
```

Puis lancer avec docker-compose ou la commande docker run.

## Dépannage

### Le port 8501 est déjà utilisé

Modifiez le port dans `docker-compose.yml` ou dans la commande docker run :
```yaml
ports:
  - "8502:8501"  # Utilise le port 8502 sur votre machine
```

### Problèmes de permissions sur le dossier data

Sur Windows, assurez-vous que Docker Desktop a accès au dossier partagé dans les paramètres.

### L'application ne démarre pas

Vérifiez les logs :
```bash
docker-compose logs
```
