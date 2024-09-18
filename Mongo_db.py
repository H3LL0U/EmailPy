
from pymongo import MongoClient
from pymongo import errors


def get_subscribed_emails(mongo_client:MongoClient, db_name="Emails", collection_name = "Emails"):
    
    client = mongo_client
    db = client[db_name]
    collection = db[collection_name]

    
    query = {"subscribed": True}

    
    documents = collection.find(query, {"_id": 0, "email": 1})

    
    emails = [doc["email"] for doc in documents]

    

    
    return emails

def remove_newline_from_emails(mongo_client:MongoClient, db_name = "Emails", collection_name = "Emails"):
    
    client = mongo_client
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

def update_subscribed_by_email(mongo_client:MongoClient,email,new_subscribed_value = False, db_name = "Emails", collection_name = "Emails" ):
    client = mongo_client
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

    

def reset_cookies(mongo_client:MongoClient, db_name = "Emails", collection_name = "Cookies"):
    
    client = mongo_client
    

    db = client[db_name]
    

    collection = db[collection_name]
    

    collection.delete_many({})
    

    client.close()
def add_unique_email(mongo_client:MongoClient, email:str, db_name = "Emails", collection_name = "Emails"):
    """
    Add an email to the MongoDB collection if it is unique.
    
    Parameters:
    - mongo_uri: The URI for the MongoDB connection
    - db_name: The name of the database
    - collection_name: The name of the collection
    - email: The email address to be added
    
    Returns:
    - A message indicating the result of the operation
    """
    email = email.strip("\n")
    
    try:
        
        client = mongo_client
        
        
        db = client[db_name]
        
        
        collection = db[collection_name]
        
        
        existing_email = collection.find_one({"email": email})
        
        if existing_email:
            return "Email already exists in the collection."
        
        # Insert the new email
        result = collection.insert_one({"email": email})
        
        if result.inserted_id:
            return f"Email added successfully with ID: {result.inserted_id}"
        else:
            return "Failed to add the email."
    
    except errors.PyMongoError as e:
        return f"An error occurred: {e}"

def get_ammount_documents(mongo_client:MongoClient,db_name = "Emails",collection="Emails"):
    db = mongo_client[db_name]
    collection = db[collection]

    return collection.count_documents({})

def delete_document_by_email(connection:MongoClient,email:str, db_name = "Emails", collection_name = "Emails"):
    """
    Remove a document from MongoDB by its email value.
    
    :param connection: The MongoClient connection
    :param db_name: The name of the database
    :param collection_name: The name of the collection
    :param email: The email value to search for and remove
    :return: The result of the delete operation
    """
    
    db = connection[db_name]
    collection = db[collection_name]
    
    # Delete one document that matches the email
    result = collection.delete_one({"email": email})
    
    if result.deleted_count > 0:
        print(f"Document with email {email} deleted successfully.")
    else:
        print(f"No document found with email {email}.")
    
    return result