from pymongo import MongoClient

client = MongoClient(
    host="127.0.0.1",
    port = 27017
)

#print(client.list_database_names())

sample = client["sample"]
#print(sample.list_collection_names())
c_zips = sample["zips"]
#print(c_zips.find_one())

#rand = sample.create_collection(name="rand")
# We can check the creation of the collection with this 
#print(sample.list_collection_names())

'''data = [
  {"name": "Melthouse","bread":"Wheat","sauce": "Ceasar"},
  {"name": "Italian BMT", "extras": ["pickles","onions","lettuce"],"sauce":["Chipotle", "Aioli"]},
  {"name": "Steakhouse Melt","bread":"Parmesan Oregano"}, 
  {"name": "Germinal", "author":"Emile Zola"}, 
  {"pastry":"cream puff","flavour":"chocolate","size":"big"}
]
'''

#rand.insert_many(data)

'''for i in list(c_zips.find({},{"_id":0,"city":1}).limit(12)):
    print(i)
'''

#print(c_zips.find().distinct("state"))

from pprint import pprint

#pprint(client["sample"]["cie"].find_one())

import re 

'''exp = re.compile("^[0-9]*$")
pprint(list(c_zips.find({"city": exp}, {"city": 1})))
'''

'''pprint(
    list(
        client["sample"]["cie"].aggregate(
            [
                {"$match": {"acquisitions.company.name": "Tumblr"}},
                {"$project": {"_id": 1, "society": "$name"}}
            ]
        )
    )
)'''

