# Bonnes pratiques
Dans ce paragraphe, nous allons voir quelques bonnes pratiques dans l'utilisation d'Airflow:
* réduire au maximum la taille des tâches pour qu'elles puissent tourner ou re-tourner de manière indépendantes
* éviter de faire tourner du code en dehors de la définition des tâches et des DAGs dans le dossier dags
* éviter d'utiliser Airflow pour des tâches sur de trop gros volumes de données: préférer lancer des tâches sur des moteurs de calcul dédiés (Spark, Hadoop, SQL, ...)
* contrairement à ce que nous avons fait dans le cours, préférer un start_date statique
* passer la plupart des arguments communs aux différentes tâches dans l'argument default_args dans la définition du DAG
* éviter de supprimer des tâches dans un DAG pour conserver l'historique d'exécution de ces tâches: préférer construire un nouveau DAG
* implémenter des tâches de vérifications avec des Sensors notamment après des insertions
bien documenter les tâches et les DAG
