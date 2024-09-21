
from pymongo import MongoClient
from pymongo import errors
from cryptography_db import *

DEFAULT_VALUES = {"subscribed":True,
                  "encrypted":False,
                  "exists":True}
def get_subscribed_emails(mongo_client:MongoClient, db_name="Emails", collection_name = "Emails",check_subscribed = True):
    
    client = mongo_client
    db = client[db_name]
    collection = db[collection_name]

    # Get both encrypted and unencrypted emails
    query = DEFAULT_VALUES

    
    documents = collection.find(query, {"_id": 0, "email": 1})

    
    emails = [doc["email"] for doc in documents]
    
    query["encrypted"] = True
    
    documents = collection.find(query, {"_id": 0, "email": 1})
    encrypted_emails = list(map(decrypt_value,[doc["email"] for doc in documents]))
    emails +=encrypted_emails

    
    return emails
def get_emails(mongo_client:MongoClient, db_name="Emails", collection_name = "Emails",check_subscribed = True):
    '''
    returns a tupple with (id, decrypted_emails)
    '''
    client = mongo_client
    db = client[db_name]
    collection = db[collection_name]

    # Get unencrypted
    query = DEFAULT_VALUES

    
    documents = collection.find(query, {"_id": 1, "email": 1})

    
    emails = [(doc["_id"],doc["email"]) for doc in documents]
    
    #get encrypted
    query["encrypted"] = True
    
    documents = collection.find(query, {"_id": 1, "email": 1})
    for doc in documents:
        emails.append((doc["_id"],decrypt_value(doc["email"])))
    

    
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
        for doc in collection.find({"encrypted":True}):
            if decrypt_value(doc["email"]) == email:
                result = collection.update_one({"_id":doc["_id"]},update)
                break

        if result.matched_count == 0:
            print(f"No document found with email: {email}")
        elif result.modified_count == 0:
            print(f"Encrypted Document with email {email} was already set to subscribed={new_subscribed_value}.")
        else:
            print(f"Encrypted Document with email {email} was successfully updated to subscribed={new_subscribed_value}.")

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

def get_id_of_an_email(mongo_client:MongoClient,email:str):
    '''
    returns objectID of an email from the database by email name
    '''
    all_emails = get_emails(mongo_client)
    
    
    email_dict = {email[1]: email[0] for email in all_emails}

    
    return email_dict.get(email, None)



def add_unique_email(mongo_client:MongoClient, email:str, db_name = "Emails", collection_name = "Emails", encrypt = True):
    """
    Add an email to the MongoDB collection if it is unique.
    
    Parameters:
    - mongo_uri: The URI for the MongoDB connection
    - db_name: The name of the database
    - collection_name: The name of the collection
    - email: The email address to be added
    - encrypt: encrypts the email when inserted
    Returns:
    - A message indicating the result of the operation
    """
    email = email.strip("\n")
    
    try:
        client = mongo_client
        db = client[db_name]
        collection = db[collection_name]
        
        
        all_emails = get_emails(client)
        
        try:
            
            idx_email = [email[1] for email in all_emails].index(email)
        except ValueError:
            
        
        
            
            
        
        # Insert the new email
            if encrypt:
                query = DEFAULT_VALUES
                query["encrypted"] = True
                query["email"] = encrypt_value(email)
            else:
                query = DEFAULT_VALUES
                query["email"] = email
            
                
            result = collection.insert_one(query)
            
            if result.inserted_id:
                return f"Email added successfully with ID: {result.inserted_id}"
            else:
                return "Failed to add the email."
        return "Email already exists in the collection."
    
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

    id_email = get_id_of_an_email(connection,email=email)
    if id_email is None:
        print("Email not found")
        return None



    result = collection.delete_one({"_id": id_email})
    
    if result.deleted_count > 0:
        print(f"Document with email {email} deleted successfully.")
    else:
        print(f"No document found with email {email}.")
    
    return result



def add_property_to_documents(connection:MongoClient,property_name:str,property_value:int|bool|str,db_name = "Emails", collection_name = "Emails",filter_query={}):
    client = connection 

    
    db = client[db_name]

    
    collection = db[collection_name]

    
    update_query = {"$set": {property_name: property_value}}


    result = collection.update_many(filter_query, update_query)

    if result.modified_count > 0:
        print(f"Successfully updated the document: {result.modified_count} document(s) modified.")
    else:
        print("No document was updated, or the property already exists with the given value.")

def encrypt_values_in_db(connection:MongoClient,property_name:str = "email",db_name = "Emails", collection_name = "Emails",filter_query={"encrypted":False}):
    client = connection

    
    db = client[db_name]
    collection = db[collection_name]

    
    cursor = collection.find(filter_query)

    for doc in cursor:
        
        original_value = doc[property_name]
        
        
        encrypted_value = encrypt_value(original_value,)
        
       
        collection.update_one(
            {"_id": doc["_id"]},  
            {"$set": {property_name: encrypted_value, "encrypted": True}},
            
        )
        print(f"Encrypted and updated document with _id: {doc['_id']} to {encrypted_value}")
        
def decrypt_values_in_db(connection:MongoClient,property_name:str = "email",db_name = "Emails", collection_name = "Emails",filter_query={"encrypted":True}):
    client = connection

    
    db = client[db_name]
    collection = db[collection_name]

    
    cursor = collection.find(filter_query)

    for doc in cursor:
        
        original_value = doc[property_name]
        
        
        encrypted_value = decrypt_value(original_value,)
        
       
        collection.update_one(
            {"_id": doc["_id"]},  
            {"$set": {property_name: encrypted_value, "encrypted": False}})
        print(f"Decrypted and updated document with _id: {doc['_id']} to {encrypted_value}")