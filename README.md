# GestionPharmacie

## Description

GestionPharmacie est une application web développée avec Django pour la gestion des ventes et des stocks dans une pharmacie. 
Ce projet est conçu pour être utilisé par deux types de gestionnaires : le gestionnaire de ventes et le gestionnaire de stocks.

## Prérequis

- Python 3.x
- pip (gestionnaire de paquets Python)
- Git

## Installation

### 1. Cloner le dépôt

  ```bash
    git clone https://github.com/GoldenDev74/GestionPharmacie.git
    cd GestionPharmacie
  ```

### 2. Créer et activer un environnement virtuel (recommandé)
  Sur Windows
  
  ```bash
    python -m venv env
    .\env\Scripts\activate
  ```
  Sur macOS/Linux

  ```bash
    python3 -m venv env
    source env/bin/activate
  ```

### 3. Installer les dépendances

  ```bash
    pip install -r requirements.txt
  ```

### 4. Appliquer les migrations

  ```bash
    python manage.py migrate
  ```

### 5. Lancer le serveur de développement

  ```bash
    python manage.py runserver
  ```
Vous pouvez maintenant accéder à l'application en ouvrant votre navigateur web et en allant à l'adresse http://127.0.0.1:8000/.

# Structure du Projet
GestionVentes : Application pour la gestion des ventes.
GestionStocks : Application pour la gestion des stocks.
Utilisateurs : Application pour la gestion des utilisateurs.

## Contribuer
 ### 1. Forker le dépôt
    Cliquez sur le bouton "Fork" en haut à droite de la page du dépôt sur GitHub.
 ### 2. Cloner votre fork
  ```bash
    git clone https://github.com/votre_nom_utilisateur/GestionPharmacie.git
    cd GestionPharmacie
  ```

 ### 3. Créer une branche

  ```bash
   git checkout -b ma-branche
  ```
travailler sur votre branche, la base de donnée est dispo jusqu'à la fin du projet donc plus bésoin de faire des migrations
 ### 5. Commiter vos modifications
 ```bash
   git add .
   git commit -m "Description de vos modifications"
 ```

### 6.  Pousser vos modifications

 ```bash
  git push origin ma-branche

 ```

### 7. Ouvrir une Pull Request
fait un pull request avec une description précise de ce que vous avez eu à faire. Je viendrai
le voir et si c'est bon le merge au projet

    
