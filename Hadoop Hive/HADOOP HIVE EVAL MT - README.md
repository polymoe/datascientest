# Evaluation Hadoop Hive
* Mohamed TOUMI
* Bootcamp DE oct 2022
* 2023 01 12

## Schéma des tables et choix d'optimisation du stockage
Ci-dessous une proposition de schéma et de choix d'optimistaion du stockage pour chaque table.

### La table 'title.akas'
Le schéma suivant est proposé:
* `titleId (STRING)` : identifiant alphanumérique unique par titre
* `ordering (INT)` : un nombre pour identifier de manière unique les lignes pour un film donné
* `title (STRING) `: le titre localisé 
* `region (STRING)` : la région pour la version indiquée du titre 
* `language (STRING)` : la langue du titre 
* `types (ARRAY STRING) `: une liste d'attributs pour le titre. Un ou plusieurs parmis les suivants : "alternative", "dvd", "festival", "tv", "video", "working", "original", "imdbDisplay"
* `attributes (ARRAY STRING)` : d'autres termes pour décrire le titre alternatif
* `isOriginalTitle (BOOLEAN)` – 0: titre non original; 1: titre original

Pour cette table, nous pouvons opter pour un choix d'optimisation du stockage en partitionnant la table selon la variable `isOriginalTitle`. Ainsi, deux partitions seront créées selon si le titre est un titre original ou non.

### La table 'title.basics'
Le schéma suivant est proposé:
* `tconst (STRING)` : identifiant alphanumérique unique par titre
* `titleType (STRING) `:  le type/format du titre (movie, short, tvseries, tvepisode, video, etc)
* `primaryTitle (STRING)` : le titre le plus populaire pour le film 
* `originalTitle (STRING)` - le titre original, dans la langue originale 
* `isAdult (BOOLEAN)` - 0: titre pour non-adultes ; 1: titre pour adultes
* `startYear (STRING)` : représente l'année de sortie du titre 
* `endYear (STRING)` : l'anée de la fin d'une série (vaut ‘\N’ pour tous les autres types)
* `runtimeMinutes (FLOAT)` :  la durée d'un titre en minutes
* `genres (arrays)` :  peut inclure jusqu'à trois genres associés au titre 

Pour cette table, nous pouvons opter pour un choix d'optimisation du stockage en partitionnant la table selon la variable `titleType`. Ainsi une partition sera créée pour chaque type de titre (movie, short, tvseries, etc.)

### La table 'title.crew'
Le schéma suivant est proposé:
* `tconst (STRING)` : identifiant alphanumérique unique par titre
* `directors (arrays)` : liste des directeurs pour un titre donné
* `writers (arrays)` : liste des auteurs d'un titre donné

Pour cette table, nous pouvons opter pour un choix d'optimisation du stockage en utilisant des buckets. Nous pouvons choisir de le faire sur la variable `writes`, et en indiquant un nombre souhaité de `10` buckets par exemple. Un tel choix (plutot qu'une partition, car les deux principales variables ici sont fournies dans des listes qui sont très variables, et donc semble peu pertinent de partitionner selon ces variables).

### La table 'title.episode'
Le schéma suivant est proposé:
* `tconst (STRING)` : identifiant alphanumérique de l'épisode
* `parentTconst (STRING)` : identifiant alphanumérique de la série parente
* `seasonNumber (INT)` : le numéro de la saison à laquelle appartient l'épisode
* `episodeNumber (INT)` : numéro de l'épisode dans la série 

Pour cette table, nous pouvons opter pour un choix d'optimisation du stockage en partitionnant la table selon la variable `seasonNumber`. Ainsi, une partition sera créée pour chaque saison de la série tv. 

### La table 'title.principals'
Le schéma suivant est proposé:
* `tconst (STRING)` : identifiant alphanumérique unique du titre
* `ordering (INT)` : nombre pour identifier de manière unique les lignes d'un titre 
* `nconst (STRING)` : identifiant alphanumérique unique d'un nom/personne
* `category (STRING)` : la catégorie de l'emploi de la personne
* `job (STRING)` : le type de l'emploi
* `characters (STRING)` : le nom du personnage joué, si applicable (sinon '\N)

Pour cette table, nous pouvons opter pour un choix d'optimisation du stockage en partitionnant la table selon la variable `job`. Ainsi, une partition sera créée pour chaque type d'emploi des personnes de la table. 

### La table 'title.ratings'
Le schéma suivant est proposé:
* `tconst (STRING) `:  identifiant alphanumérique unique du titre
* `averageRating (FLOAT)` : moyenne pondérée des évaluations
* `numVotes (INT)` :  nombre de votes reçus

Pour cette table, nous pouvons opter pour un choix d'optimisation du stockage en utilisant des buckets. Nous pouvons choisir de le faire sur la variable `averageRating`, et en indiquant un nombre souhaité de `5` buckets par exemple. Un tel choix car la variable intéressante pour nous est dans un format qui lui donne un grand nombre de valeurs différentes. Ainsi, nous souhaitons l'organiser dans un nombre limité de buckets (au lieu d'utiliser des partitions).

### La table 'name.basics'
Le schéma suivant est proposé:
* `nconst (STRING)` : identifiant alphanumérique unique du nom/personne
* `primaryName (STRING)` : le nom avec lequel la personne est le plus souvent désignée
* `birthYear (STRING)` : date de naissance
* `deathYear (STRING)` : date de décès (le cas échéant). Sinon '\N'
* `primaryProfession (arrays)` : top 3 des emplois de la personne
* `knownForTitles (arrays)`  : liste des titres– les plus connus de la personne

Pour cette table, nous pouvons opter pour un choix d'optimisation du stockage en utilisant des buckets. Nous pouvons choisir de le faire sur la variable `birthYear`, et en indiquant un nombre souhaité de `10` buckets par exemple. Un tel choix car il n'y a pas vraiment de variable d'intérêt pour nous ici justifiant une quelconque partition (a priori). En revanche, on peut avoir un intérêt à organiser la table en utilisé des buckets.

## Instructions pour télécharger les données et les placer dans Hive
Nous allons dans ce qui suit télécharger les fichiers de données, et les préparer avant leur mise dans Hive.

### Téléchargement des données
Ci-dessous les instructions pour les différentes tables.

#### La table 'title.akas'
Nous récupérons la tabel 'title.akas' : 
`wget https://datasets.imdbws.com/title.akas.tsv.gz`

Pour décompresser l'archive, utiliser la commande suivante:
`gzip -d title.akas.tsv.gz`

Nous constatons que le fichier tsv décompressé est très volumineux (plus de 1.6 G).
Ainsi, pour des raisons d'espace limité sur la machine virtuelle, nous allons le restreindre au 1000 premières entrées seulement (par exemple).
`head -n 1000 title.akas.tsv > title.akas.light.tsv` 
`rm title.akas.tsv`
Un fichier `title.akas.light.tsv` a donc été créé et le précédent (très volumineux) supprimé

#### La table 'title.basics'
Nous récupérons la tabel 'title.basics' : 
`wget https://datasets.imdbws.com/title.basics.tsv.gz`

Pour décompresser l'archive, utiliser la commande suivante:
`gzip -d title.basics.tsv.gz`

Nous constatons que le fichier tsv décompressé est très volumineux (plus de 778 M).
Ainsi, pour des raisons d'espace limité sur la machine virtuelle, nous allons le restreindre au 1000 premières entrées seulement (par exemple).
`head -n 1000 title.basics.tsv > title.basics.light.tsv` 
`rm title.basics.tsv`
Un fichier `title.basics.light.tsv` a donc été créé et le précédent (très volumineux) supprimé

#### La table 'title.crew'
Nous récupérons la tabel 'title.crew' : 
`wget https://datasets.imdbws.com/title.crew.tsv.gz`

Pour décompresser l'archive, utiliser la commande suivante:
`gzip -d title.crew.tsv.gz`

Nous constatons que le fichier tsv décompressé est très volumineux (plus de 299 M).
Ainsi, pour des raisons d'espace limité sur la machine virtuelle, nous allons le restreindre au 1000 premières entrées seulement (par exemple).
`head -n 1000 title.crew.tsv > title.crew.light.tsv` 
`rm title.crew.tsv`
Un fichier `title.crew.light.tsv` a donc été créé et le précédent (très volumineux) supprimé

#### La table 'title.episode'
Nous récupérons la tabel 'title.episode' : 
`wget https://datasets.imdbws.com/title.episode.tsv.gz`

Pour décompresser l'archive, utiliser la commande suivante:
`gzip -d title.episode.tsv.gz`

Nous constatons que le fichier tsv décompressé est très volumineux (plus de 179 M).
Ainsi, pour des raisons d'espace limité sur la machine virtuelle, nous allons le restreindre au 1000 premières entrées seulement (par exemple).
`head -n 1000 title.episode.tsv > title.episode.light.tsv` 
`rm title.episode.tsv`
Un fichier `title.episode.light.tsv` a donc été créé et le précédent (très volumineux) supprimé

#### La table 'title.principals'
Nous récupérons la tabel 'title.principals' : 
`wget https://datasets.imdbws.com/title.principals.tsv.gz`

Pour décompresser l'archive, utiliser la commande suivante:
`gzip -d title.principals.tsv.gz`

Nous constatons que le fichier tsv décompressé est très volumineux (plus de 2.3 G).
Ainsi, pour des raisons d'espace limité sur la machine virtuelle, nous allons le restreindre au 1000 premières entrées seulement (par exemple).
`head -n 1000 title.principals.tsv > title.principals.light.tsv` 
`rm title.principals.tsv`
Un fichier `title.principals.light.tsv` a donc été créé et le précédent (très volumineux) supprimé

#### La table 'title.ratings'
Nous récupérons la tabel 'title.ratings' : 
`wget https://datasets.imdbws.com/title.ratings.tsv.gz`

Pour décompresser l'archive, utiliser la commande suivante:
`gzip -d title.ratings.tsv.gz`

Nous constatons que le fichier tsv décompressé est très volumineux (plus de 21 M).
Ainsi, pour des raisons d'espace limité sur la machine virtuelle, nous allons le restreindre au 1000 premières entrées seulement (par exemple).
`head -n 1000 title.ratings.tsv > title.ratings.light.tsv` 
`rm title.ratings.tsv`
Un fichier `title.ratings.light.tsv` a donc été créé et le précédent (très volumineux) supprimé

#### La table 'name.basics'
Nous récupérons la tabel 'title.ratings' : 
`wget https://datasets.imdbws.com/name.basics.tsv.gz`

Pour décompresser l'archive, utiliser la commande suivante:
`gzip -d name.basics.tsv.gz`

Nous constatons que le fichier tsv décompressé est très volumineux (plus de 699 M).
Ainsi, pour des raisons d'espace limité sur la machine virtuelle, nous allons le restreindre au 1000 premières entrées seulement (par exemple).
`head -n 1000 name.basics.tsv > name.basics.light.tsv` 
`rm name.basics.tsv`
Un fichier `name.basics.light.tsv` a donc été créé et le précédent (très volumineux) supprimé


### Transfert des données dans Hive
Nous allons maintenant progressivement transférer nos 7 tables dans Hive.
* Nous créons nos tables non-partitionnées
* Nous les alimentons avec nos fichiers tsv
* Nous créons enfin nos tables partitionnées sur la base des tables non-partitionnée en leur indiquant les colonnes sélectionnées dans les tables non-partitionnées (la dernière colonne étant la variable de partitionnement)

La première étape est bien sûr de lancer le docker-compose : 
`docker-compose up -d`

Une fois nos conteneurs lancés, nous gardons ouvertes 3 fenêtres du terminal:
* une pour utiliser la machine virtuelle datascientest
* une pour naviguer dans et utiliser le conteneur de hive-server
* une pour utiliser hive

mettons nos fichiers tsv dans le répertoire `~/data`, de manière à ce que celles-ci soient également passées au cluster, car ce dossier est monté sur le dossier `/data` du cluster.
`mv -t ./data name.basics.light.tsv title.akas.light.tsv title.basics.light.tsv title.crew.light.tsv title.episode.light.tsv title.principals.light.tsv title.ratings.light.tsv`

Allons maintenant dans le conteneur du cluster (un second onglet terminal à ouvrir le cas échéant)
`docker exec -it hive-server bash`

mettons nos fichiers tsv à la racine du HDFS
`hdfs dfs -put /data/name.basics.light.tsv /name.basics.light.tsv`
`hdfs dfs -put /data/title.akas.light.tsv /title.akas.light.tsv`
`hdfs dfs -put /data/title.basics.light.tsv /title.basics.light.tsv`
`hdfs dfs -put /data/title.crew.light.tsv /title.crew.light.tsv`
`hdfs dfs -put /data/title.episode.light.tsv /title.episode.light.tsv`
`hdfs dfs -put /data/title.principals.light.tsv /title.principals.light.tsv`
`hdfs dfs -put /data/title.ratings.light.tsv /title.ratings.light.tsv`

nous pouvons vérifier que le transfert a bien été fait : 
`hdfs dfs -ls /`

Nous allons passer dans Hive. Ouvrir un (3eme) onglet terminal qui donne dans le conteneur du cluster (comme indiqué plus haut).Puis, taper la commande : 
`hive`

Nous créons maintenant notre base de données 'my_eval_db':
```
-- creating a database 
CREATE DATABASE my_eval_db;

-- selecting the database
USE my_eval_db;
```

#### Création de la table 'title_akas_partitions'
Comme indiqué plus haut, en partitionnant la table selon la variable `isOriginalTitle`.

Nous créons la table non-partitionnée : 'title_akas'

```
USE my_eval_db;

CREATE TABLE title_akas
(
    titleId STRING,
    ordering INT,
    title STRING,
    region STRING,
    language STRING,
    types ARRAY <STRING>,
    attributes ARRAY <STRING>,
    isOriginalTitle BOOLEAN
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons ensuite cette table avec nos données:
```
LOAD DATA INPATH '/title.akas.light.tsv'
INTO TABLE title_akas;
```

Nous créons la table partitionnée : title_akas_partitions

```
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;

CREATE TABLE title_akas_partitions
(
    titleId STRING,
    ordering INT,
    title STRING,
    region STRING,
    language STRING,
    types ARRAY <STRING>,
    attributes ARRAY <STRING>
)
PARTITIONED BY (isOriginalTitle BOOLEAN)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons enfin sur cette base notre table partitionnée.
```
INSERT INTO TABLE title_akas_partitions
PARTITION (isOriginalTitle)
SELECT titleId, ordering, title, region, language, types, attributes ,isOriginalTitle
FROM title_akas;
```

#### Création de la table 'title.basics'
Comme indiqué plus haut, en partitionnant la table selon la variable `titleType`.

Nous créons la table non-partitionnée : 'title_basics'
```
CREATE TABLE title_basics
(
    tconst STRING,
    titleType STRING,
    primaryTitle STRING,
    originalTitle STRING,
    isAdult BOOLEAN,
    startYear STRING,
    endYear STRING,
    runtimeMinutes FLOAT,
    genres ARRAY <STRING>
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons ensuite cette table avec nos données:
```
LOAD DATA INPATH '/title.basics.light.tsv'
INTO TABLE title_basics;
```

Nous créons ensuite la table partitionnée : title_basics_partitions

```
CREATE TABLE title_basics_partitions
(
    tconst STRING,
    primaryTitle STRING,
    originalTitle STRING,
    isAdult BOOLEAN,
    startYear STRING,
    endYear STRING,
    runtimeMinutes FLOAT,
    genres ARRAY <STRING>
)
PARTITIONED BY (titleType STRING)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons enfin sur cette base notre table partitionnée.
```
INSERT INTO TABLE title_basics_partitions
PARTITION (titleType)
SELECT tconst, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres ,titleType
FROM title_basics;
```

#### Création de la table 'title.crew'
Comme indiqué plus haut, en utilisant des buckets basés sur la variable `writers`, et en indiquant un nombre souhaité de `10` buckets.

Nous créons la table non-partitionnée : 'title_crew'
```
CREATE TABLE title_crew
(
    tconst STRING,
    directores ARRAY <STRING>,
    writers ARRAY <STRING>
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons ensuite cette table avec nos données:
```
LOAD DATA INPATH '/title.crew.light.tsv'
INTO TABLE title_crew;
```

Nous créons ensuite les buckets : title_crew_buckets

```
CREATE TABLE title_crew_buckets
(
    tconst STRING,
    directores ARRAY <STRING>,
    writers ARRAY <STRING>
)
CLUSTERED BY (writers) INTO 10 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons enfin sur cette base notre table de buckets.
```
INSERT INTO TABLE title_crew_buckets
SELECT tconst, directores, writers
FROM title_crew;
```

#### Création de la table 'title.episode'
Comme indiqué plus haut, en partitionnant la table selon la variable `seasonNumber`.

Nous créons la table non-partitionnée : 'title_episode'
```
CREATE TABLE title_episode
(
    tconst STRING,
    parentTconst STRING,
    seasonNumber INT,
    episodeNumber INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons ensuite cette table avec nos données:
```
LOAD DATA INPATH '/title.episode.light.tsv'
INTO TABLE title_episode;
```

Nous créons ensuite la table partitionnée : title_episode_partitions

```
CREATE TABLE title_episode_partitions
(
    tconst STRING,
    parentTconst STRING,
    episodeNumber INT
)
PARTITIONED BY (seasonNumber INT)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons enfin sur cette base notre table partitionnée.
```
INSERT INTO TABLE title_episode_partitions
PARTITION (seasonNumber)
SELECT tconst, parentTconst, episodeNumber, seasonNumber
FROM title_episode;
```

#### Création de la table 'title.principals'
Comme indiqué plus haut, en partitionnant la table selon la variable `job`.

Nous créons la table non-partitionnée : 'title_principals'
```
CREATE TABLE title_principals
(
    tconst STRING,
    ordering INT,
    nconst STRING,
    category STRING,
    job STRING,
    characters STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons ensuite cette table avec nos données:
```
LOAD DATA INPATH '/title.principals.light.tsv'
INTO TABLE title_principals;
```

Nous créons ensuite la table partitionnée : title_principals_partitions

```
CREATE TABLE title_principals_partitions
(
    tconst STRING,
    ordering INT,
    nconst STRING,
    category STRING,
    characters STRING
)
PARTITIONED BY (job STRING)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons enfin sur cette base notre table partitionnée.
```
INSERT INTO TABLE title_principals_partitions
PARTITION (job)
SELECT tconst, ordering, nconst, category, characters, job
FROM title_principals;
```

#### Création de la table 'title.ratings'
Comme indiqué plus haut, en utilisant des buckets basés sur la variable `averageRating`, et en indiquant un nombre souhaité de `5` buckets.

Nous créons la table non-partitionnée : 'title_ratings'
```
CREATE TABLE title_ratings
(
    tconst STRING,
    averageRating FLOAT,
    numVotes INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons ensuite cette table avec nos données:
```
LOAD DATA INPATH '/title.ratings.light.tsv'
INTO TABLE title_ratings;
```

Nous créons ensuite les buckets : title_ratings_buckets

```
CREATE TABLE title_ratings_buckets
(
    tconst STRING,
    averageRating FLOAT,
    numVotes INT
)
CLUSTERED BY (averageRating) INTO 5 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons enfin sur cette base notre table de buckets.
```
INSERT INTO TABLE title_ratings_buckets
SELECT tconst, numVotes, averageRating
FROM title_ratings;
```

#### Création de la table 'name.basics'
Comme indiqué plus haut, en utilisant des buckets basés sur la variable `birthYear`, et en indiquant un nombre souhaité de `10` buckets.

Nous créons la table non-partitionnée : 'name_basics'
```
CREATE TABLE name_basics
(
    nconst STRING,
    primaryName STRING,
    birthYear STRING,
    deathYear STRING,
    primaryProfession ARRAY <STRING>,
    knownForTitles ARRAY <STRING>
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons ensuite cette table avec nos données:
```
LOAD DATA INPATH '/name.basics.light.tsv'
INTO TABLE name_basics;
```

Nous créons ensuite les buckets : name_basics_buckets

```
CREATE TABLE name_basics_buckets
(
    nconst STRING,
    primaryName STRING,
    birthYear STRING,
    deathYear STRING,
    primaryProfession ARRAY <STRING>,
    knownForTitles ARRAY <STRING>
)
CLUSTERED BY (birthYear) INTO 10 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY "\t"
LINES TERMINATED BY "\n"
STORED AS TEXTFILE;
```

Nous alimentons enfin sur cette base notre table de buckets.
```
INSERT INTO TABLE name_basics_buckets
SELECT nconst, primaryName, birthYear, deathYear, primaryProfession, knownForTitles
FROM name_basics;
```

## Démonstration
Ci-dessous, quelques requêtes pour démontrer l'utilisation de la base.

`SHOW TABLES;`
`SELECT * FROM name_basics_buckets LIMIT 5;`
pour requêter en tenant compte de notre variable utilisée pour créer les buckets de la table name_basics_buckets: 
`SELECT * FROM name_basics_buckets WHERE birthYear > 1970 LIMIT 5;`
pour requêter en tenant comtpe de la variable utilisée pour partitionner la table title_episode_partitions:
`SELECT seasonNumber, COUNT(*) FROM title_episode_partitions GROUP BY seasonNumber;`
