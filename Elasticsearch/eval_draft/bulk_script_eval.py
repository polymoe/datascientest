#! /usr/bin/python
from elasticsearch import Elasticsearch, helpers
import csv

# Connexion au cluster
client = Elasticsearch(hosts = "http://@localhost:9200")

with open('./../Womens_Clothing.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    helpers.bulk(client, reader, index='ecom')