# Readme pour API génératrice de QCM
auteur : Mohamed TOUMI
date : 22/12/2022
promo : BC DE oct 22

## Présentation de la structure de l'API et des choix effectués

1) l'API comporte 4 routes : 2 GET, 1 POST, 1 PUT
2) ces routes sont organisés en 2 parties
  - home : pour ce qui est des 2 routes GET qui ne traitent pas directement des questions
  - questions : pour ce qui est des 2 routes restantes (1 POST, 1 PUT) qui traitent directement des questions
3) 2 schémas sont définis : 
  - Questions_criteria: qui définit les 3 critères utiliser pour choisir les questions (la taille du QCM, le type du test, la ou les catégories voulues)
  - New_question: qui définit les champs et valeurs associées pour ajouter une question dans la base (fichier csv), par l'utilisateur admin
4) une authentification est nécessaire pour utiliser l'API:
  - par un utilisateur connu, pour interroger la base
  - par un admin pour écrire dans la base (ajouter une question)
5) une chiffrage des données d'identification est opéré en utilisant CryptContext
6) au-delà des routes demandées dans l'énnoncé de l'évaluation, une route [BONUS] est présentée ici (GET /criteria). Elle permet de récupérer les valeurs possibles pour les trois paramètres servant à requêter la base, à savoir : la taille du QCM, les types de test, et les catégories. De cette manière, l'utilisateur pourra connaitre les paramètres à utiliser pour requêter ensuite correctement l'API pour récupérer des questions
7) Au-delà de la documentation des différentes routes, classes et fonctions, des exceptions sont définies dans le code, notamment dans la route POST /questions (qui récupère les questions): 
  - exception ValueError qui retourne un code 498 : elle indique que bien qu'il n'y ait pas d'erreur dans les paramètres de la requête, la taille du QCM demandée est trop grande par rapport aux questions disponibles et correspondant aux critères demandés.
  - exception ValueError qui retourne un code 499 : elle indique qu'un ou plusieurs arguments de la requête ont une valeur non autorisée (pour la taille du QCM, le type du test, ou la catégorie)

## Instructions pour utiliser l'API

1) pour lancer l'API : lancer la commande suivante dans le terminal
uvicorn main:api --reload
Ensuite, ouvrir un autre terminal pour exécuter d'autres commandes (cf. ci-dessous) pour utiliser l'API

2) les différentes routes mises en oeuvre dans l'API nécessitent une authentification:
  - d'un utilisateur connu, pour interroger la base
  - d'un admin pour écrire dans la base (ajouter une question)

Nous pouvons donc tester que pour un utilisateur inconnu (dans la base des utilisteurs autorisés), requêter l'API renvoie une erreur.
Dans le terminal, lancer la requête suivante:
curl -X 'GET' \
  'http://127.0.0.1:8000/' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic ZGFuaWVsOmRhbmllbA=='

Le header "Authorization" contient les identifiants de l'utilisateur. Ici, nous avons essayé username=daniel et password=daniel. Mais ceux-ci sont chiffrés, et sont donc représentés par la suite de caractères "ZGFuaWVsOmRhbmllbA=="

Nous pouvons constater que la requête renvoie une erreur (daniel ne figurant pas dans la base des utilisateurs autorisés) : 
401 Unauthorized
detail":"Incorrect user or password

3) pour vérifier que l'API est bien fonctionnelle, lancer la requête suivante dans le terminal
curl -X 'GET' \
  'http://127.0.0.1:8000/' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA=='

Ici, nous faisons un GET sur la route "/" en spécifiant les identifiants de l'utilisateur alice (mot de passe : wonderland), qui sont chiffrés (YWxpY2U6d29uZGVybGFuZA==)
Le message qui devrait alors s'afficher est le suivant : 
{"message": "tout va bien alice ! l'API est fonctionnelle"}

4) [BONUS - non demandé dans l'énnoncé] afin que l'utilisateur puisse savoir quelles sont les différentes valeurs possibles pour les arguments de la requête qui génère un QCM, une route a été définie.
Il s'agit de la route "GET /criteria". 
Dans le terminal, lancer la requête suivante (tjrs pour l'utilisateur alice):
curl -X 'GET' \
  'http://127.0.0.1:8000/criteria' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA=='

Nous obtenons alors la réponse suivante :
{
  "User": "alice",
  "Taille_QCM": [
    5,
    10,
    20
  ],
  "Type_test": [
    "Test de positionnement",
    "Test de validation",
    "Total Bootcamp"
  ],
  "Categories": [
    "BDD",
    "Systèmes distribués",
    "Streaming de données",
    "Docker",
    "Classification",
    "Sytèmes distribués",
    "Data Science",
    "Machine Learning",
    "Automation"
  ]
}

5) Pour ce qui est de notre requête principale, à savoir celle qui génère un QCM sur la base de critères, lancer la requête suivante dans le terminal (tjrs avec alice)
curl -X 'POST' \
  'http://127.0.0.1:8000/questions' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "nb": 5,
  "use": "Total Bootcamp",
  "subject": [
    "Data Science"
  ]
}'

Nous obtenons la réponse suivante, qui génère donc un QCM de 5 questions pour un test de type "Total Bootcamp", portant sur la catégorie "Data Science":
[
  "When building a model, you have to",
  "Are every datasets worth a Data Science project ?",
  "Data science is ...",
  "What are the first things you want to do when you start a Data Science project ?",
  "Its applications are ..."
]

En relançant, cette même requête, nous obtenons 5 nouvelles questions générées aléatoirement à partir du stock de questions disponibles.

Lancer la requête suivante dans le terminal génère une exception de type 498, indiquant qu'il n'y a pas suffisamment de questions en stock pour générer un QCM de la taille demandée:
curl -X 'POST' \
  'http://127.0.0.1:8000/questions' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "nb": 20,
  "use": "Total Bootcamp",
  "subject": [
    "Data Science"
  ]
}'

La réponse obtenue est : 
{
  "detail": "alice, the sample requested is larger than possible questions"
}

Lancer la requête suivante génère une exception de type 499, indiquant que l'un des paramètres de la requête a une valeur non autorisée (soit pour la taille du QCM, le type du test ou la catégorie):
curl -X 'POST' \
  'http://127.0.0.1:8000/questions' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWxpY2U6d29uZGVybGFuZA==' \
  -H 'Content-Type: application/json' \
  -d '{
  "nb": 3,
  "use": "Total Bootcamp",
  "subject": [
    "Data Science"
  ]
}'

la réponse obtenue est : 
{
  "detail": "alice, the question criteria is not in correct range of (nb, use, subject)"
}

6) la dernière route (PUT /questions) permet à un utilisateur "admin" de créer une nouvelle question dans la base (dans le fichier csv).
Lancer la requête suivante (pour un utilisateur admin):
curl -X 'PUT' \
  'http://127.0.0.1:8000/questions' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic YWRtaW46NGRtMU4=' \
  -H 'Content-Type: application/json' \
  -d '{
  "Question": "Quelle commande pour exécuter un docker-compose.yaml ?",
  "Subject": "Docker",
  "Use": "Test de positionnement",
  "Correct": "A",
  "ResponseA": "docker-compose up",
  "ResponseB": "docker compose up",
  "ResponseC": "compose down",
  "ResponseD": "docker-compose down",
  "Remark": "Docker is so much fun !"
}'

La réponse obtenue est : 
{
  "User": "admin:",
  "message": "la question qui comporte les champs suivants: ['Quelle commande pour exécuter un docker-compose.yaml ?', 'Docker', 'Test de positionnement', 'A', 'docker-compose up', 'docker compose up', 'compose down', 'docker-compose down', 'Docker is so much fun !'], a bien été ajoutée"
}
