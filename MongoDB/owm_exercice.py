# Do not forget to create a variable in your console with the export command
# You can choose the city of your choice, you only need to write the name in english

# You will need to create a variable WEATHER with your key of OpenWeatherMap

import os 
import requests
from datetime import datetime
from pymongo import MongoClient
import pprint


def get_weather(ville):

    KEY = os.getenv("WEATHER")
    CITY = ville   
    
    r = requests.get(
        url="https://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(
            CITY, KEY
        )
    )   

    data = r.json()

    clean_data = {i: data[i] for i in ["weather", "main"]}
    clean_data["weather"] = clean_data["weather"][0]

    current = datetime.now().strftime("%H:%M:%S")  
    clean_data["time"] = current
    clean_data["city"] = CITY

    return clean_data

def feed_weather(data):
    # ajoute à la collection weather de la base sample
    client = MongoClient(
        host="localhost",
        port = 27017
    )

    sample = client["sample"]
    #col = sample.create_collection(name="weather")
    sample["weather"].insert_one(data)
    pass

# remplir la collection weather, en itérant sur plusieurs villes
'''villes = ["Maisons-Alfort", "Nanterre", "Nantes", "Marseille", "Alger", "Biskra", "Boulder", "Colorado Springs"]

for ville in villes:
    data = get_weather(ville)
    feed_weather(data)'''

# Récupérez les documents où la sous-clé "main" vaut "Clear" et affichez-y uniquement le nom de la ville sans l'identifiant du document : 
client = MongoClient(
    host="localhost",
    port = 27017
)

sample = client["sample"]
print(list(sample["weather"].find({"weather.main":"Clear"},{"_id":0, "city":1})))

#Combien de documents ont une valeur de clé temp_min supérieure ou égale à 289 et une valeur de clé temp_max inférieure à égale à 291. (Les températures sont en Kelvin)
print(len(list(sample["weather"].find({"main.temp_min":{"$gte":289}, "main.temp_max":{"$lte":291}},{"_id":0, "city":1}))))
# ou autre option:
print(sample["weather"].count_documents({"main.temp_min":{"$gte":289}, "main.temp_max":{"$lte":291}}))

#Renvoyez le nombre de documents que nous avons selon la sous-clé weather.main
print(list(sample["weather"].aggregate([{"$group": {"_id": "$weather.main", "nb": {"$sum": 1}}}])))