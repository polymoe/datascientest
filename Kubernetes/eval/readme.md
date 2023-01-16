# Kubernetes - Evaluation
* Mohamed TOUMI
* Bootcamp DE - oct 2022
* 2023 jan 08

## Présentation des choix effectués

### dans main.py : 
* les deux champs à compléter sont passés en variables d'environnement
* en particulier, le mot de passe de la base de données est déjà connu 'datascientest1234'. Il sera mis dans un Secret dans le "default" de Kubernetes, avant de déployer les POD 
* en revanche, l'adresse IP de la base de données, qui sera la même que celle du POD n'est pas encore connue. Elle sera passée en variable d'environnement lors du déploiement du POD
* pour ce qui est du port pour accéder à la base MySQL, celui-ci est indiqué dans le descriptif de l'image sur dockerhub (3306)

### my-secret-eval.yml
* contient le mot de passe de la base MySQL, dans un stringdata

### my-deployment-eval.yml
* chaque POD va contenir les deux conteneurs (API Et base de données)
* l'API expose sur le port 8000, et la base de données sur le port 3306 (comme indiqué plus haut)
* en outre, deux variables d'environnement sont définies : pour le mot de passe de la base et pour l'adresse IP du POD
* le mot de passe de la base est défini dans le Secret my-secret-eval, avec la clé db-pass
* l'adresse IP du POD est obtenue avec 'status.podIP'. Cette adresse IP permettra au conteneur de l'API de requêter la base de données MySQL

### my-service-eval.yml
* permet de définir les ports où sont exposés les conteneurs : 3306 pour la base MySQL et 8001 pour l'API

### my-ingress-eval.yml
* où nous n'exposons au monde extérieur que le port de l'API

## Déroulé des commandes pour lancer les livrables
* minikube start
* minikube dashboard --url=true    # (puis copier l'url qui est indiquée pour accéder au dashboard kubernetes)
* kubectl proxy --address='0.0.0.0'--disable-filter=true
* kubectl apply -f ./my-secret-eval.yml
* kubectl create -f ./my-deployment-eval.yml
* kubectl create -f ./my-service-eval.yml
* minikube addons enable ingress
* kubectl create -f ./my-ingress-eval.yml
* kubectl get ingress    # (pour récupérer l'adresse IP du POD. Pour nous, c'est : 192.168.49.2)
* curl -X GET -i 192.168.49.2/status     # (pour tester le statut de l'API)
* curl -X GET -i 192.168.49.2/users      # (pour récupérer la liste des utilisateurs et champs associés depuis l'API qui interroge la base MySQL)
* curl -X GET -i 192.168.49.2/users/1    #(pour récupérer les informations du premier utilisateur depuis l'API qui interroge la base MySQL)
* Pour pouvoir accéder à l'API depuis le navigateur, il sera nécessaire de créer un tunnel ssh entre l'API et le port 8000 de notre machine personnelle