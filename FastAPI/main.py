import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from random import sample
from fastapi import HTTPException
from fastapi import Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from csv import writer

# définition de la classe qui nous servira à passer des informations dans le corps de notre requête
class Questions_criteria(BaseModel):
    """Les critères qui sont transmis pour choisir les questions
    """
    nb: int
    use: str
    subject: List[str]

# définition de la classe qui nous servira à ajouter une question dans la base de questions
class New_question(BaseModel):
    """Les champs correspondant à la nouvelle question à ajouter
    """
    Question: str
    Subject: str
    Use: str
    Correct: str
    ResponseA: str
    ResponseB: str
    ResponseC: str
    ResponseD: str
    Remark: str

### définition de l'API ###
api = FastAPI(
    title="Eval module FastAPI",
    description="Développée par Mohamed TOUMI - dec 2022",
    version="1.0",
    openapi_tags=[
        {
            'name': 'home',
            'description': 'default functions'
        },
        {
            'name': 'questions',
            'description': 'functions that are used to deal with questions'
        }
    ]
)
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
### définition du champs des valeurs possibles ###
users = {

    "alice": {
        "username": "alice",
        "hashed_password": pwd_context.hash('wonderland'),
    },

    "bob" : {
        "username" :  "bob",
        "hashed_password" : pwd_context.hash('builder'),
    },

    "clementine" : {
        "username" :  "clementine",
        "hashed_password" : pwd_context.hash('mandarine'),
    },
    
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash('4dm1N'),
    }

}

admin_users = {

    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash('4dm1N'),
    }

}

nb_questions = [5, 10, 20]   # nb de questions à renvoyer

df = pd.read_csv("questions.csv", sep = ",")

use_list = df['use'].unique()   # liste des usages possibles
subject_list = df['subject'].unique()    # list des sujets possibles

### définition de la fonction qui permettra de fournir un formulaire d'authentification et de vérification d'identifiant pour les utilisateurs autorisés ###
def get_current_user(needs_admin):
    """ pour vérifier si les identifiants figurent bien dans la base des utilisateurs autorisés
        l'argument needs_admin permet de savoir dans quelle base d'utilisateurs regarder:
            - si on a besoin de droits non admin (needs_admin = True), on regarde dans la base : users
            - si on a besoin de droits admin (needs_admin = False), on regarde dans la base : admin_users
    """
    if not needs_admin:
        user_ref = users
    else :
        user_ref = admin_users 
    def get_user_(credentials: HTTPBasicCredentials = Depends(security)):
        username = credentials.username
        if not(user_ref.get(username)) or not(pwd_context.verify(credentials.password, user_ref[username]['hashed_password'])):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect user or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username
    return get_user_

### définition des fonctions qui génèrent les questions ###
def gen_q(df_, use_, subj_):  # retourne toutes les questions possibles pour les critères choisis  
    """fonction qui retourne toutes les questions disponibles vérifiant les critères use et subject
    """
    possible_q = []
    for subj_i in subj_:
        tmp_restult = (df_.loc[(df_['use'] == use_) & (df_['subject'] == subj_i)])["question"]
        for item in tmp_restult.iteritems():
            possible_q.append(item[1])   # [1] pour ne récupérer que la question dans le tuple (index, question)
    return possible_q    

def sel_q(possible_q_, nb_): # retourne le nbre souhaité de questions choisies aléatoirement
    """fonction qui échantionne aléatoirement parmi l'ensemble des questions vérifiant les critères use et subject
    """
    selected_q = sample(possible_q_, nb_)
    return selected_q

### définition de la fonction qui vérifie que les critères renseignés sont bien dans le champs des possibles ###
def check_criteria(questions_criteria_, nb_questions_, use_list_, subject_list_):
    """fonction qui qui vérifie que les critères renseignés sont bien dans le champs des possibles
    """
    raise_exception = False
    if questions_criteria_.nb not in nb_questions_:
        raise_exception = True 
    if questions_criteria_.use not in use_list_:
        raise_exception = True
    if questions_criteria_.subject not in subject_list_:
        raise_exception = True
    if raise_exception:
        raise ValueError

### point de terminaison pour vérifier que l'API est bien fonctionnelle ###
@api.get('/', name="Vérif API fonctionnelle", tags=['home'])
def get_index(username: str = Depends(get_current_user(False))):
    """Point de terminaison permettant de vérifier que l'API est fonctionnelle
    """
    return {
        "message" : "tout va bien {} ! l'API est fonctionnelle".format(username)
        }
    
### [BONUS] point de terminaison pour récupérer les différents champs possibles pour extraire des questions, et leurs valeurs ###
@api.get('/criteria', name="[BONUS] Valeurs possibles pour champs requêtes", tags=['home'])
def get_criteria(username: str = Depends(get_current_user(False))):
    """ [BONUS] Point de terminaison pour récupérer les différents champs possibles pour extraire des questions, et leurs valeurs
    """
    return dict(
        User=username,
        Taille_QCM=nb_questions,
        Type_test=list(use_list),
        Categories=list(subject_list))

### point de terminaison pour récupérer les questions souhaitées ###
responses = {
    498: {"description": "Sample Size Error"},
    499: {"description": "Incorrect nb, use or subject"},
}
@api.post('/questions', name="post les critères et récupère les questions souhaitées", tags=['questions'], responses=responses)
def post_questions_criteria(questions_criteria: Questions_criteria, username: str = Depends(get_current_user(False))):
    """Point de terminaison permettant de poster les critères des questions et de récupérer ensuite ces questions
    """
    try:
        check_criteria(questions_criteria, nb_questions, use_list, subject_list)
        pass
    except ValueError:
        raise HTTPException(
            status_code=499,
            detail='{}, the question criteria is not in correct range of (nb, use, subject)'.format(username)
        )
    try:
        possible_questions = gen_q(df, questions_criteria.use, questions_criteria.subject)
        return sel_q(possible_questions, questions_criteria.nb)
    except ValueError:
        raise HTTPException(
            status_code=498,
            detail='{}, the sample requested is larger than possible questions'.format(username)
        )    

### point de terminaison permettant à l'utilisateur admin de créer une nouvelle question ###
@api.put('/questions', name="Ajouter Nouvelle Question par ADMIN", tags=['questions'])
def put_questions(new_question_: New_question, username: str = Depends(get_current_user(True))):
    """Point de terminaison permettant à l'utilisateur admin de créer une nouvelle question
    """
    new_question = []
    new_question.append(new_question_.Question)
    new_question.append(new_question_.Subject)
    new_question.append(new_question_.Use)
    new_question.append(new_question_.Correct)
    new_question.append(new_question_.ResponseA)
    new_question.append(new_question_.ResponseB)
    new_question.append(new_question_.ResponseC)
    new_question.append(new_question_.ResponseD)
    new_question.append(new_question_.Remark)
    
    with open('questions.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(new_question)
        f_object.close()
    return {
        "User" : "{}:".format(username),
        "message" : "la question qui comporte les champs suivants: {}, a bien été ajoutée".format(new_question)
        }
