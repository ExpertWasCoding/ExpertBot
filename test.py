import pymongo

# Assuming you have already created a MongoClient and selected a database and collection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['server_data']
collection = db['servers']

# Initialize an empty dictionary to store the loaded documents
server_data = {}

# Iterate over all documents in the collection and load them into the dictionary
for document in collection.find():
    server_id = document['server_id']
    is_running = document['IsRunning']
    server_data[server_id] = {'IsRunning': is_running}

# Print the loaded server_data dictionary
print(server_data) 
