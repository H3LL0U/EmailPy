
from pymongo import MongoClient



def get_subscribed_emails(mongo_uri, db_name="Emails", collection_name = "Emails"):
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    
    query = {"subscribed": True}

    
    documents = collection.find(query, {"_id": 0, "email": 1})

    
    emails = [doc["email"] for doc in documents]

    
    client.close()

    
    return emails

def remove_newline_from_emails(mongo_uri, db_name = "Emails", collection_name = "Emails"):
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    query = {"email": {"$regex": r"\n$"}} 
    
    
    documents = collection.find(query)
    
    updated_count = 0  

    for doc in documents:
        
        cleaned_email = doc['email'].rstrip("\n")
        
        
        collection.update_one({"_id": doc["_id"]}, {"$set": {"email": cleaned_email}})
        updated_count += 1

    
    client.close()

def update_subscribed_by_email(mongo_uri,email,new_subscribed_value = False, db_name = "Emails", collection_name = "Emails" ):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    query = {"email": email}
    update = {"$set": {"subscribed": new_subscribed_value}}

    result = collection.update_one(query, update)

    
    if result.matched_count == 0:
        print(f"No document found with email: {email}")
    elif result.modified_count == 0:
        print(f"Document with email {email} was already set to subscribed={new_subscribed_value}.")
    else:
        print(f"Document with email {email} was successfully updated to subscribed={new_subscribed_value}.")

    
    client.close()

def reset_cookies(mongo_uri, db_name = "Emails", collection_name = "Cookies"):
    
    client = MongoClient(mongo_uri)
    

    db = client[db_name]
    

    collection = db[collection_name]
    

    collection.delete_many({})
    

    client.close()
