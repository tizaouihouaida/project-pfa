# GestionPharmacie

Bienvenue sur le projet GestionPharmacie, un système de gestion de stock et de vente pour les pharmacies développé avec Django.

## Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Contribution](#contribution)
- [Collaborateurs](#collaborateurs)
- [Licence](#licence)

## Description

GestionPharmacie est une application web conçue pour aider les pharmacies à gérer leurs stocks de médicaments et leurs ventes. Le projet est développé en utilisant le framework Django, ce qui permet une gestion efficace et sécurisée des données.

## Fonctionnalités

- Gestion des stocks de médicaments
- Suivi des ventes
- Gestion des utilisateurs
- Rapports et statistiques
- Interface utilisateur intuitive
## Captures d'écran
  
  ![Capture 4](https://github.com/user-attachments/assets/963b64c0-272f-45ab-b0bc-7585c8545103)

  ![Capture 5](https://github.com/user-attachments/assets/3bcc07f1-a92d-41f5-9e83-1367d5e983f4)

  ![Capture 6](https://github.com/user-attachments/assets/95fef471-1e4b-400d-a483-01ea70ca8c3c)

  ![Capture 7](https://github.com/user-attachments/assets/edc7993e-2210-44b9-8f05-be35f1d7fee0)

  ![Capture 8](https://github.com/user-attachments/assets/dab43788-2277-44ab-bd49-3624193846e1)

  ![Capture 9](https://github.com/user-attachments/assets/ea1b2a0b-f944-4afb-88dc-735ee89b8936)

  ![Capture 10](https://github.com/user-attachments/assets/a9ab1172-03f6-4b85-96bb-77359724401c)


## Installation

Pour installer et configurer le projet, suivez ces étapes :

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/GestionPharmacie.git
   cd GestionPharmacie
2. Créez et activez un environnement virtuel :
    ```bash
    python -m venv env
    source env/bin/activate
    # Sur Windows,
    utilisez `env\Scripts\activate`
3. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
4. Appliquez les migrations :
   ```bash
   python manage.py migrate
5. Insérer des données dans la base de données:
   copier le contenue du fichier backup.sql dans le logiciel
   avec laquel vous avez ouvert la base de donnée db.sqlite3
   de préférence DbBrowser Sqlite et exécuter les requêtes.
6. Lancez le serveur de développement :
   ```bash
   python manage.py runserver
## Utilisation
1. Accédez à l'application en ouvrant votre navigateur et en allant à l'adresse http://127.0.0.1:8000/.
2. Connectez-vous avec les identifiants du superutilisateur que vous avez créés.
3. Utilisez l'interface pour gérer les stocks et les ventes de la pharmacie.
## Contribution
Nous apprécions les contributions de la communauté. Pour contribuer au projet, suivez ces étapes :
Fork le dépôt.
Créez une branche pour votre fonctionnalité (git checkout -b feature/nouvelle-fonctionnalité).
Committez vos modifications (git commit -am 'Ajout de la nouvelle fonctionnalité').
Poussez vers la branche (git push origin feature/nouvelle-fonctionnalité).
Ouvrez une Pull Request.
##Collaborateurs
GoldenDev74
dollardking
Roi12122525
JBDEV-stack

