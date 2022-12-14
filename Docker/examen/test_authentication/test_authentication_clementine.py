import os
import requests

# définition de l'adresse de l'API
api_address = os.environ.get('api_name')
# port de l'API
api_port = 8000

# requête
r = requests.get(
    url='http://{address}:{port}/permissions'.format(address=api_address, port=api_port),
    params= {
        'username': 'clementine',
        'password': 'mandarine'
    }
)

output = '''
============================
    Authentication test
============================

request done at "/permissions"
| username="clementine"
| password="mandarine"

expected result = 403
actual restult = {status_code}

==>  {test_status}

'''


# statut de la requête
status_code = r.status_code

# affichage des résultats
if status_code == 200:
    test_status = 'SUCCESS'
else:
    test_status = 'FAILURE'
output = output.format(status_code=status_code, test_status=test_status)
print(output)

# impression dans un fichier
if os.environ.get('LOG') == '1':
    with open('../my_log/api_test.log', 'a+') as file:
        file.write(output)