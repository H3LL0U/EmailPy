
from pymongo import MongoClient
from pymongo import errors
from .cryptography_db import *

DEFAULT_VALUES = {"subscribed":True,
                  "encrypted":False,
                  "exists":True,
                  "visited": 0,
                  "member_type": "unknown",
                  "started_typing": False, 
                  "organisation": "unknown",
                  "date_of_visit": "None",
                  "date_of_email": "None"}

ENABLE_LOGGING =  True

def log(message):
    if ENABLE_LOGGING:
        print(message)

def get_subscribed_emails(mongo_client:MongoClient, db_name="Emails", collection_name = "Emails"):
    
    client = mongo_client
    db = client[db_name]
    collection = db[collection_name]

    # Get both encrypted and unencrypted emails
    query = {"subscribed":True,"exists":True,"encrypted":False}

    
    documents = collection.find(query, {"_id": 0, "email": 1})

    
    emails = [doc["email"] for doc in documents]
    
    query["encrypted"] = True
    
    documents = collection.find(query, {"_id": 0, "email": 1})
    encrypted_emails = list(map(decrypt_value,[doc["email"] for doc in documents]))
    emails +=encrypted_emails

    
    return emails
def get_emails(mongo_client:MongoClient, db_name="Emails", collection_name = "Emails",auto_decrypt = True, query=None):
    '''
    returns a tuple with (id, decrypted_emails)
    '''
    client = mongo_client
    db = client[db_name]
    collection = db[collection_name]

    # Get unencrypted
    if query is None:
        query = {"encrypted":False}

        
    documents = collection.find(query, {"_id": 1, "email": 1})

        
    emails = [(doc["_id"],doc["email"]) for doc in documents]
    
    #get encrypted
    query["encrypted"] = True
    
    documents = collection.find(query, {"_id": 1, "email": 1})
    for doc in documents:
        if auto_decrypt:
            emails.append((doc["_id"],decrypt_value(doc["email"])))
        else:
            emails.append((doc["_id"],doc["email"]))

    
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



def update_subscribed_by_email(mongo_client:MongoClient,email,new_subscribed_value = False, db_name = "Emails", collection_name = "Emails" ):
    '''
    Returns result -> None if no document found
    -> True if modiefied
    -> False if not modified
    '''
    
    client = mongo_client
    db = client[db_name]
    collection = db[collection_name]

    query = {"email": email}
    update = {"$set": {"subscribed": new_subscribed_value}}
    
    result = collection.update_one(query, update)

    
    if result.matched_count == 0:
        
        email_id = get_id_of_an_email(mongo_client=mongo_client,email=email,db_name=db_name,collection_name=collection_name)
        if email_id is None:
            return None
        
        result = collection.update_one({"_id":email_id},update)
        if result.matched_count == 0:
            log(f"No document found with email: {email}")
            return None

        elif result.modified_count == 0:
            log(f"Encrypted Document with email {email} was already set to subscribed={new_subscribed_value}.")
            return False
        else:
            log(f"Encrypted Document with email {email} was successfully updated to subscribed={new_subscribed_value}.")
            return True
                



    elif result.modified_count == 0:
        log(f"Document with email {email} was already set to subscribed={new_subscribed_value}.")
        return False
    else:
        log(f"Document with email {email} was successfully updated to subscribed={new_subscribed_value}.")
        return True

    

    
def get_visited_ammount(mongo_client:MongoClient, db_name:str = "Emails", collection_name:str = "Emails"):
    return len(get_emails(mongo_client,auto_decrypt=False,query={"encrypted":False,"visited":True},collection_name=collection_name,db_name=db_name,))
    

def get_id_of_an_email(mongo_client:MongoClient,email:str,db_name:str = "Emails",collection_name:str = "Emails", auto_decrypt = True):
    '''
    returns: objectID of an email from the database by email name
    If no email returns False
    '''
    email = get_email_properties(mongo_client,email=email,db_name=db_name,collection_name=collection_name,auto_decrypt=auto_decrypt)
    
    
    

    
    return email["_id"]



def add_unique_email(mongo_client: MongoClient, email: str, db_name="Emails", collection_name="Emails", encrypt=True):
    """
    Add an email to the MongoDB collection if it is unique.
    
    Returns:
    - The inserted document's ObjectId if successful.
    - None if the email already exists or an error occurs.
    """
    email = email.strip("\n")

    try:
        client = mongo_client
        db = client[db_name]
        collection = db[collection_name]

        
        existing_email = collection.find_one({"email": encrypt_value(email)}) or collection.find_one({"email": email})
        if existing_email:
            return None  

        
        query = DEFAULT_VALUES.copy()  
        query["encrypted"] = encrypt
        query["email"] = encrypt_value(email) if encrypt else email

        # Insert the new email
        result = collection.insert_one(query)
        return result.inserted_id if result.inserted_id else None

    except errors.DuplicateKeyError:
        print(f"Duplicate email detected: {email}")
        return None  

    except errors.PyMongoError as e:
        print(f"Database error: {e}")
        return None  

def get_ammount_documents(mongo_client:MongoClient,db_name = "Emails",collection="Emails"):
    db = mongo_client[db_name]
    collection = db[collection]

    return collection.count_documents({})

def delete_document_by_email(mongo_client:MongoClient,email:str, db_name = "Emails", collection_name = "Emails"):
    """
    Remove a document from MongoDB by its email value.
    
    :param connection: The MongoClient connection
    :param db_name: The name of the database
    :param collection_name: The name of the collection
    :param email: The email value to search for and remove
    :return: The result of the delete operation 
    """
    
    db = mongo_client[db_name]
    collection = db[collection_name]
    
    # Delete one document that matches the email

    id_email = get_id_of_an_email(mongo_client,email=email,collection_name=collection_name,db_name=db_name)
    if id_email is None:
        log("Email not found")
        return None



    result = collection.delete_one({"_id": id_email})
    
    if result.deleted_count > 0:
        log(f"Document with email {email} deleted successfully.")
    else:
        log(f"No document found with email {email}.")
    
    return result



def add_property_to_documents(connection:MongoClient,property_name:str,property_value:int|bool|str,db_name = "Emails", collection_name = "Emails",filter_query={}):
    '''
    returns -> a number of emails modified (int)
    '''
    
    client = connection 

    
    db = client[db_name]

    
    collection = db[collection_name]

    
    update_query = {"$set": {property_name: property_value}}

    
    result = collection.update_many(filter_query, update_query)

    if result.modified_count > 0:
        log(f"Successfully updated the document: {result.modified_count} document(s) modified.")
    else:
        log("No document was updated, or the property already exists with the given value.")
    return result.modified_count

def encrypt_values_in_db(connection:MongoClient,property_name:str = "email",db_name = "Emails", collection_name = "Emails",filter_query={"encrypted":False}):
    '''
    returns -> the number of emails encrypted
    '''
    client = connection

    
    db = client[db_name]
    collection = db[collection_name]

    
    cursor = collection.find(filter_query)
    email_num = 0
    for doc in cursor:
        
        original_value = doc[property_name]
        
        
        encrypted_value = encrypt_value(original_value,)
        
       
        collection.update_one(
            {"_id": doc["_id"]},  
            {"$set": {property_name: encrypted_value, "encrypted": True}},
            
        )
        email_num+=1
        log(f"Encrypted and updated document with _id: {doc['_id']} to {encrypted_value}")
    return email_num
def decrypt_values_in_db(connection:MongoClient,property_name:str = "email",db_name = "Emails", collection_name = "Emails",filter_query={"encrypted":True}):
    '''
    returns-> the number of emails decrypted
    '''
    client = connection

    
    db = client[db_name]
    collection = db[collection_name]

    
    cursor = collection.find(filter_query)
    email_num = 0
    for doc in cursor:
        
        original_value = doc[property_name]
        
        
        encrypted_value = decrypt_value(original_value,)
        
       
        collection.update_one(
            {"_id": doc["_id"]},  
            {"$set": {property_name: encrypted_value, "encrypted": False}})
        log(f"Decrypted and updated document with _id: {doc['_id']} to {encrypted_value}")
        email_num+=1
    return email_num

def get_encrypted_version(connection:MongoClient,email:str,db_name = "Emails", collection_name = "Emails"):
    '''
    gets the encrypted version of an email from the database if it exists
    '''
    return encrypt_value(email)

def from_txt_to_db(path_to_txt_file,database_connection,should_have_second_and_top_level_domain="", encoding = "utf-8"):
    '''
    Gets emails stored on a txt line and adds them line by line to the database if they were not yet there
    '''
    with open(path_to_txt_file,"r", encoding=encoding) as txt:
        for email in txt.readlines():
            email = email.strip("\n")
            if email.endswith(should_have_second_and_top_level_domain):
                print(add_unique_email(database_connection,email))

def get_email_properties(mongo_client: MongoClient, email: str, db_name="Emails", collection_name="Emails", auto_decrypt=True):
    """
    Retrieves all properties and their values for a given email.
    Returns a dictionary:
    can also take the encrypted version of an email in the 'email' paramter
    {
        "property1": value1,
        "property2": value2,
        ...
    }
    """
    client = mongo_client
    db = client[db_name]
    collection = db[collection_name]

    # Find the document based on email

    doc = collection.find_one({"email": email})
    if not doc: 
        doc = collection.find_one({"email" : encrypt_value(email)})
    

    if not doc:
        return None  # Email not found

    
    if doc.get("encrypted", True) and auto_decrypt and "email" in doc:
        doc["email"] = decrypt_value(doc["email"])

    return doc
def get_documents_by_query(mongo_client: MongoClient, query=None, db_name="Emails", collection_name="Emails", limit=None):
    """
    Retrieves documents from a MongoDB collection based on a query.
    
    Parameters:
    - mongo_client (MongoClient): The MongoDB client instance.
    - query (dict, optional): The filter query for retrieving documents (default: {}).
    - db_name (str): The name of the database (default: "Emails").
    - collection_name (str): The name of the collection (default: "Emails").
    - limit (int, optional): The maximum number of documents to return (default: None - returns all).

    Returns:
    - list of dicts: A list of matching documents.
    """
    client = mongo_client
    db = client[db_name]
    collection = db[collection_name]

    if query is None:
        query = {}

    cursor = collection.find(query)

    if limit:
        cursor = cursor.limit(limit)

    return list(cursor)
