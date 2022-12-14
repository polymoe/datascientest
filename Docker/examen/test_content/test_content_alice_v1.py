import os
import requests

# définition de l'adresse de l'API
api_address = os.environ.get('api_name')

# définition de la phrase d'Alice
positive_sentence = os.environ.get('pos_sentence_env')
negative_sentence = os.environ.get('neg_sentence_env')

# port de l'API
api_port = 8000

# requête positive sur v1/sentiment
r_vp = requests.get(
    url='http://{address}:{port}/v1/sentiment'.format(address=api_address, port=api_port),
    params= {
        'username': 'alice',
        'password': 'wonderland',
        'sentence': '{sentence}'.format(sentence=positive_sentence)
    }
)

output_vp = '''
============================
    Content test
============================

request done at "/v1/sentiment"
| username="alice"
| password="wonderland"
| sentence="{sentence}"

expected result positive = TRUE
actual restult positive = {score_status}
score value = {score_value}

==>  {test_status}

'''

# score de la requête
score_vp = r_vp.json()["score"]

# affichage des résultats
if score_vp > 0:
    test_status_vp = 'SUCCESS'
    score_status_vp = 'TRUE'
else:
    test_status_vp = 'FAILURE'
    score_status_vp = 'FALSE'
output_vp = output_vp.format(sentence=positive_sentence, score_status=score_status_vp, score_value=score_vp, test_status=test_status_vp)
print(output_vp)

# impression dans un fichier
if os.environ.get('LOG') == '1':
    with open('../my_log/api_test.log', 'a+') as file:
        file.write(output_vp)


#########################
#########################

# requête négative sur v1/sentiment
r_vn = requests.get(
    url='http://{address}:{port}/v1/sentiment'.format(address=api_address, port=api_port),
    params= {
        'username': 'alice',
        'password': 'wonderland',
        'sentence': '{sentence}'.format(sentence=negative_sentence)
    }
)

output_vn = '''
============================
    Content test
============================

request done at "/v1/sentiment"
| username="alice"
| password="wonderland"
| sentence="{sentence}"

expected result positive = FALSE
actual restult positive = {score_status}
score value = {score_value}

==>  {test_status}

'''

# score de la requête
score_vn = r_vn.json()["score"]

# affichage des résultats
if score_vn < 0:
    test_status_vn = 'SUCCESS'
    score_status_vn = 'FALSE'
else:
    test_status_vn = 'FAILURE'
    score_status_vn = 'TRUE'
output_vn = output_vn.format(sentence=negative_sentence, score_status=score_status_vn, score_value=score_vn, test_status=test_status_vn)
print(output_vn)

#impression dans un fichier
if os.environ.get('LOG') == '1':
    with open('../my_log/api_test.log', 'a+') as file:
        file.write(output_vn)
