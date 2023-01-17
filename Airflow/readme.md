# Examen Airflow

* Mohamed TOUMI
* promo BC DE oct 2022
* 30 dec 2022

## Description du livrable et des choix effectués

* le livrable est le fichier my_exam_dag.py. Il comporte le code intégral du DAG répondant à l'énoncé de l'examen
* la structure du DAG est décrite dans la documentation de ce dernier, dans le fichier .py
* [BONUS] en plus de ce qui est demandé dans l'énoncé, le DAG met en oeuvre l'utilisation de FileSensor afin de vérifier la bonne création des différents fichiers par les tâches (les json de données météo datés, le csv des 20 derniers json, le csv de tous les json, le csv des features, le csv des target)
* pour pouvoir utiliser ces FileSensor, une 'connection' (my_exam_filesystem_connection) est établie par le DAG 
* afin de passer les dataframes features et target aux différents modèles, il a été choisi de recourir à une tâche qui lorsqu'elle termine le preprocessing des données, sauvegarde les dataframes features et target dans deux fichiers csv. Ces fichiers sont ensuite utilisés par les différents modèles pour en lire les X et y pour l'entrainement
* la communication des score entre les différentes tâches impliquées s'est faite avec les Xcom
* afin de ne garder dans la base des Xcom, en permanence, qu'un seul résultat (i.e trois variables : 1 pour chaque modèle), une tâche permet de vider, avant chaque nouvel entrainement, le contenu de la base Xcom issu des anciens run du DAG