#!/bin/bash

# #################################################################################################
# <!> Ce fichier doit être lancé en mode "source" pour pouvoir créer les variables d'environnement
# la commande shell est : source ./setup.sh
# #################################################################################################

# définir le nom du conteneur de l'API dans une variable d'environnement
# ce nom sera utilisé dans les requêtes vers l'API, au lieu de l'adresse IP
export api_name="api_from_compose"

# définir la valeur de la variable LOG (=1 pour enregistrer)
export LOG=1

# définir les phrases pour Alice et bob
export pos_sentence="life is beautiful"
export neg_sentence="that sucks"

# lancer le docker-compose
docker-compose up -d
# il a été remarqué que docker n'écrivait pas dans le volume de log au premier lancement. 
# un restart est donc nécessaire 
docker-compose start

# supprimer la variable d'environnement
unset api_name
unset LOG
unset pos_sentence
unset neg_sentence
