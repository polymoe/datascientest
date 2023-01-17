from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
import datetime as dt
import requests
import json
import logging
from airflow import settings
from airflow.models import Connection
import os
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from joblib import dump
from airflow.utils.session import provide_session
from airflow.models import XCom

my_dag = DAG(
    dag_id='exam_dag',
    doc_md="""
    # Examen Airflow
    * Mohamed TOUMI
    * promo BC DE oct 2022

    ## Description du DAG
    DAG qui permet de récupérer des informations depuis une API de données météo disponible en ligne (openweathermap.org), les stocke, les transforme et entraîne des algorithmes dessus, et alimente un dashboard.
    Son architecture est la suivante:
    
    - 1_get_weather_data : récupère les données météo de la liste de villes sélectionnées à partir de l'API du site openweathermap.org, et les stocke dans un fichier json
    - 1s_sensor_json : vérifie la bonne création du fichier json (datée) dans le système de fichiers (en ayant créé une Connection)
    - 2_transform_data_into_csv : à partir de l'ensemble des fichiers json créés, récupère les données correspondant aux 20 json les plus récents et les stockent dans un fichier csv (dans clean_data), qui sera utilisé pour alimenter un dashboard
    - 2s_sensor_data_csv : vérifie la bonne création du fichier csv
    - 3_transform_all_data_into_csv : à partir de l'ensemble des fichiers json créés, récupère l'ensemble des données et les stocke dans un fichier csv (qui sera utilisé pour alimenter des modèles de machine learning)
    - 3s_sensor_all_data_csv ; vérifie la bonne création du fichier csv
    - 4_prepare_data : à partir du fichier csv destiné à la modélisation, effectue un preprocessing des données, pour déterminer les features d'une part, et les target d'autre part. Ces données sont stockées chacune dans un fichier csv (features.csv, et target.csv), qui seront ensuite utilisés pour entrainer les modèles
    - 4s1_sensor_features_csv: vérifie la bonne création du fichier csv des features
    - 4s2_sensor_target_csv : vérifie la bonne création du fichier csv des target
    - 4z_clear_old_xcom : permet de vider le contenu de la base de données XCom, qui aura été généré lors des précédents run du DAG (afin de générer de nouvelles variables dans les tâches suivantes)
    - 4a_lin_reg_compute_score : permet de calculer le score après crossvalidation du modèle de régression linéaire, et sauvegarde le résultat dans les Xcoms
    - 4b_dec_tree_compute_score : permet de calculer le score après crossvalidation du modèle d'arbres de décision, et sauvegarde le résultat dans les XComs
    - 4c_rf_compute_score : permet de calculer le score après crossvalidation du modèle de foret aléatoire, et sauvegarde le résultat dans les XComs
    - 5_select_train_save_best_model: récupère les scores des modèles sauvegardés dans les Xcoms et en déduit le modèle le plus performant, l'entraine, et le sauvegarde dans clean_data
    """,
    tags=['exam', 'datascientest'],
    schedule_interval='* * * * *',
    # schedule_interval=None,
    default_args={
        'owner': 'airflow',
        'start_date': dt.datetime(2022, 12, 28)
    },
    catchup=False
)

api_key='9f258f6fedc72b409f5df29dfe329b61'
cities=['paris', 'london', 'washington']
json_path="/app/raw_files/"
json_file_name="{}.json".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
csv_path="/app/clean_data"
path_to_model="/app/clean_data/best_model.pickle"

def create_conn(conn_id, conn_type, login, pwd):
    conn = Connection(conn_id=conn_id,
                      conn_type=conn_type,
                      login=login,
                      password=pwd)
    session = settings.Session()
    conn_name = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()

    if str(conn_name) == str(conn.conn_id):
        logging.warning(f"Connection {conn.conn_id} already exists")
        return None

    session.add(conn)
    session.commit()
    logging.info(Connection.log_info(conn))
    logging.info(f'Connection {conn_id} is created')
    return conn

def get_weather_data():
    response_list = []

    for city in cities:
        requestUrl = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(city,api_key)
        requestHeaders = {
            "Accept": "application/json"
            }

        response = requests.get(requestUrl, headers=requestHeaders)
        response_list.append(response.json())

    jsonString = json.dumps(response_list)
    jsonFile = open(json_path+json_file_name, "w")
    jsonFile.write(jsonString)
    jsonFile.close()

def transform_data_into_csv(n_files=None, filename='data.csv'):
    parent_folder = '/app/raw_files'
    files = sorted(os.listdir(parent_folder), reverse=True)
    if n_files:
        files = files[:n_files]

    dfs = []

    for f in files:
        with open(os.path.join(parent_folder, f), 'r') as file:
            data_temp = json.load(file)
        for data_city in data_temp:
            dfs.append(
                {
                    'temperature': data_city['main']['temp'],
                    'city': data_city['name'],
                    'pression': data_city['main']['pressure'],
                    'date': f.split('.')[0]
                }
            )

    df = pd.DataFrame(dfs)

    print('\n', df.head(10))

    df.to_csv(os.path.join(csv_path, filename), index=False)

def prepare_data():
    # reading data
    path_to_data='/app/clean_data/fulldata.csv'
    df = pd.read_csv(path_to_data)
    # ordering data according to city and date
    df = df.sort_values(['city', 'date'], ascending=True)

    dfs = []

    for c in df['city'].unique():
        df_temp = df[df['city'] == c]

        # creating target
        df_temp.loc[:, 'target'] = df_temp['temperature'].shift(1)

        # creating features
        for i in range(1, 10):
            df_temp.loc[:, 'temp_m-{}'.format(i)
                        ] = df_temp['temperature'].shift(-i)

        # deleting null values
        df_temp = df_temp.dropna()

        dfs.append(df_temp)

    # concatenating datasets
    df_final = pd.concat(
        dfs,
        axis=0,
        ignore_index=False
    )

    # deleting date variable
    df_final = df_final.drop(['date'], axis=1)

    # creating dummies for city variable
    df_final = pd.get_dummies(df_final)

    features = df_final.drop(['target'], axis=1)
    target = df_final['target']

    # writing output to csv files to be used by models
    features.to_csv(csv_path+'/features.csv')
    target.to_csv(csv_path+'/target.csv')

def compute_model_score(model, features_file, target_file, task_instance):
    # getting X and y from our csv files
    X = pd.read_csv(features_file)
    y = pd.read_csv(target_file)
    # computing cross val
    cross_validation = cross_val_score(
        model,
        X,
        y,
        cv=3,
        scoring='neg_mean_squared_error')

    model_score = cross_validation.mean()

    task_instance.xcom_push(key='score', value=model_score)

def select_train_save_best_model(features_file, target_file, task_instance):
    scores = task_instance.xcom_pull(
        key='score',
        task_ids=['4a_lin_reg_compute_score', '4b_dec_tree_compute_score', '4c_rf_compute_score']
    )
    list_models = [LinearRegression(), DecisionTreeRegressor(), RandomForestRegressor()]
    min_score = min(scores)
    index_min_score = scores.index(min_score)
    model = list_models[index_min_score]
    X = pd.read_csv(features_file)
    y = pd.read_csv(target_file)
    # training the model
    model.fit(X, y)
    # saving model
    print(str(model), 'saved at ', path_to_model)
    dump(model, path_to_model)

@provide_session
def _delete_xcoms(session=None):
    num_rows_deleted = 0

    try:
        num_rows_deleted = session.query(XCom).delete()
        session.commit()
    except:
        session.rollback()

    print(f"Deleted {num_rows_deleted} XCom rows")

# definition of connection parameters
conn_conn_id = 'my_exam_filesystem_connection'
conn_conn_type = 'File (path)'
conn_login = 'airflow'
conn_pwd = 'airflow'
create_conn(conn_conn_id, conn_conn_type, conn_login, conn_pwd)

task1 = PythonOperator(
    task_id='1_get_weather_data',
    python_callable=get_weather_data,
    doc_md="""
    # task1
    appelle la fonction get_weather_data
    elle permet de récupérer les données météo de la liste de villes sélectionnées à partir de l'API du site openweathermap.org, et les stocke dans un fichier json""",
    dag=my_dag
)

sensor1 = FileSensor(
    task_id="1s_sensor_json",
    fs_conn_id='my_exam_filesystem_connection',
    filepath="{}".format(json_path+json_file_name),
    poke_interval=10,
    dag=my_dag,
    timeout=5 * 10,
    doc_md="""
    # sensor1
    vérifie la bonne création du fichier json (datée) dans le système de fichiers (une Connection ayant été créé à cet effet)""",    
    mode='reschedule'
)

task2 = PythonOperator(
    task_id='2_transform_data_into_csv',
    python_callable=transform_data_into_csv,
    op_kwargs={'n_files':20, 'filename':'data.csv'},
    doc_md="""
    # task2
    appelle la fonction transform_data_into_csv
    à partir de l'ensemble des fichiers json créés, récupère les données correspondant aux 20 json les plus récents et les stockent dans un fichier csv (dans clean_data), qui sera utilisé pour alimenter un dashboard""",    
    dag=my_dag
)

sensor2 = FileSensor(
    task_id="2s_sensor_data_csv",
    fs_conn_id='my_exam_filesystem_connection',
    filepath="{}".format(csv_path+'/data.csv'),
    poke_interval=10,
    dag=my_dag,
    timeout=5 * 10,
    doc_md="""
    # sensor2
    vérifie la bonne création du fichier data.csv dans le système de fichiers (une Connection ayant été créé à cet effet)""",    
    mode='reschedule'
)

task3 = PythonOperator(
    task_id='3_transform_all_data_into_csv',
    python_callable=transform_data_into_csv,
    op_kwargs={'n_files':None, 'filename':'fulldata.csv'},
    doc_md="""
    # task3
    appelle la fonction 3_transform_all_data_into_csv
    à partir de l'ensemble des fichiers json créés, récupère l'ensemble des données et les stocke dans un fichier csv (qui sera utilisé pour alimenter des modèles de machine learning)""",
    dag=my_dag
)

sensor3 = FileSensor(
    task_id="3s_sensor_all_data_csv",
    fs_conn_id='my_exam_filesystem_connection',
    filepath="{}".format(csv_path+'/fulldata.csv'),
    poke_interval=10,
    dag=my_dag,
    timeout=5 * 10,
    doc_md="""
    # sensor3
    vérifie la bonne création du fichier fulldata.csv dans le système de fichiers (une Connection ayant été créé à cet effet)""",    
    mode='reschedule'
)

task4 = PythonOperator(
    task_id='4_prepare_data',
    python_callable=prepare_data,
    doc_md="""
    # task4
    appelle la fonction prepare_data
    à partir du fichier csv destiné à la modélisation (fulldata.csv), effectue un preprocessing des données, pour déterminer les features d'une part, et les target d'autre part. Ces données sont stockées chacune dans un fichier csv (features.csv, et target.csv), qui seront ensuite utilisés pour entrainer les modèles""",
    dag=my_dag
)

sensor4f = FileSensor(
    task_id="4s1_sensor_features_csv",
    fs_conn_id='my_exam_filesystem_connection',
    filepath="{}".format(csv_path+'/features.csv'),
    poke_interval=10,
    dag=my_dag,
    timeout=5 * 10,
    doc_md="""
    # sensor4f
    vérifie la bonne création du fichier features.csv dans le système de fichiers (une Connection ayant été créé à cet effet)""", 
    mode='reschedule'
)

sensor4t = FileSensor(
    task_id="4s2_sensor_target_csv",
    fs_conn_id='my_exam_filesystem_connection',
    filepath="{}".format(csv_path+'/target.csv'),
    poke_interval=10,
    dag=my_dag,
    timeout=5 * 10,
    doc_md="""
    # sensor4t
    vérifie la bonne création du fichier target.csv dans le système de fichiers (une Connection ayant été créé à cet effet)""", 
    mode='reschedule'
)

task4z = PythonOperator(
    task_id='4z_clear_old_xcom',
    python_callable=_delete_xcoms,
    doc_md="""
    # task4z
    appelle la fonction _delete_xcoms
    permet de vider le contenu de la base de données XCom, qui aura été généré lors des précédents run du DAG (afin de générer de nouvelles variables dans les tâches suivantes)""",
    dag=my_dag
)

task4a = PythonOperator(
    task_id='4a_lin_reg_compute_score',
    python_callable=compute_model_score,
    op_kwargs={'model': LinearRegression(), 'features_file': csv_path+'/features.csv', 'target_file': csv_path+'/target.csv'},
    doc_md="""
    # task4a
    appelle la fonction compute_model_score pour le modèle de régression linéaire
    permet de calculer le score après crossvalidation du modèle de régression linéaire, et sauvegarde le résultat dans les Xcoms""",
    dag=my_dag
)

task4b = PythonOperator(
    task_id='4b_dec_tree_compute_score',
    python_callable=compute_model_score,
    op_kwargs={'model':DecisionTreeRegressor(), 'features_file': csv_path+'/features.csv', 'target_file': csv_path+'/target.csv'},
    doc_md="""
    # task4b
    appelle la fonction compute_model_score pour le modèle d'arbres de décision
    permet de calculer le score après crossvalidation du modèle d'arbres de décision, et sauvegarde le résultat dans les Xcoms""",
    dag=my_dag
)

task4c = PythonOperator(
    task_id='4c_rf_compute_score',
    python_callable=compute_model_score,
    op_kwargs={'model': RandomForestRegressor(), 'features_file': csv_path+'/features.csv', 'target_file': csv_path+'/target.csv'},
    doc_md="""
    # task4c
    appelle la fonction compute_model_score pour le modèle de foret aléatoire
    permet de calculer le score après crossvalidation du modèle de foret aléatoire, et sauvegarde le résultat dans les Xcoms""",
    dag=my_dag
)

task5 = PythonOperator(
    task_id='5_select_train_save_best_model',
    python_callable=select_train_save_best_model,
    op_kwargs={'features_file': csv_path+'/features.csv', 'target_file': csv_path+'/target.csv'},
    doc_md="""
    # task5
    appelle la fonction select_train_save_best_model
    récupère les scores des modèles sauvegardés dans les Xcoms et en déduit le modèle le plus performant, l'entraine, et le sauvegarde dans clean_data""",
    dag=my_dag
)

task1 >> sensor1
sensor1 >> [task2, task3]
task2 >> sensor2
task3 >> sensor3
sensor3 >> task4
task4 >> [sensor4f, sensor4t]
[sensor4f, sensor4t] >> task4z
task4z >> [task4a, task4b, task4c]
[task4a, task4b, task4c] >> task5
