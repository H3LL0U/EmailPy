
import dotenv
from email_creator import email_constructor, view_html ,email_constructor_preconstructed
from Session import Session

from email.message import EmailMessage
#from MYSQL import *
import pymongo
from Mongo_db import *
import time
import unittest
from cryptography_db import *
'''
In order for the test to run properly there should be a local mongoDB database hosted on the machine
'''
mongo_uri = "mongodb://localhost:27017"
mongo_client = MongoClient(mongo_uri)
class TestEmailFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.db_name = "TestEmailsDB"
        self.collection_name = "TestEmailsCollection"
        self.client = mongo_client
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        self.collection.delete_many({})  

        # Sample email documents


    @classmethod
    def setUp(self):
        #Reset values for each test

        self.db_name = "TestEmailsDB"
        self.collection_name = "TestEmailsCollection"
        self.client = mongo_client
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        self.collection.delete_many({})  

        self.encrypted_email = encrypt_value("test3@gmail.com")
        self.collection.insert_many([
            {"email": "test1@gmail.com", "subscribed": True, "encrypted": False,"exists":True},
            {"email": "test2@gmail.com", "subscribed": False, "encrypted": False, "exists":True},
            {"email": self.encrypted_email, "subscribed": True, "encrypted": True, "exists":True},
        ])

    
    def test_get_subscribed_emails(self):

        emails = get_subscribed_emails(self.client, db_name=self.db_name, collection_name=self.collection_name)
        #Only test1@gmail.com and test3@gmail.com are subscribed
        self.assertIn("test1@gmail.com", emails)
        self.assertNotIn("test2@gmail.com", emails)
        self.assertIn("test3@gmail.com",emails)

    def test_get_emails(self):
        emails = get_emails(self.client, db_name=self.db_name, collection_name=self.collection_name)
        self.assertTrue(any(email == "test3@gmail.com" for _, email in emails))
        self.assertTrue(any(email == "test1@gmail.com" for _, email in emails))
        self.assertFalse(any(email == "test6@gmail.com" for _, email in emails))

    def test_remove_newline_from_emails(self):
        
        self.collection.insert_one({"email": "newline_email@gmail.com\n"})
        remove_newline_from_emails(self.client, db_name=self.db_name, collection_name=self.collection_name)
        doc = self.collection.find_one({"email": "newline_email@gmail.com"})
        self.assertIsNotNone(doc)
        self.assertEqual(doc["email"], "newline_email@gmail.com")

    def test_update_subscribed_by_email(self):
        result = update_subscribed_by_email(self.client, "test1@gmail.com", new_subscribed_value=False, db_name=self.db_name, collection_name=self.collection_name)
        self.assertTrue(result)
        subscribed_emails = get_subscribed_emails(self.client,db_name=self.db_name,collection_name=self.collection_name)
        self.assertFalse("test1@gmail.com" in subscribed_emails)
        update_subscribed_by_email(self.client, "test1@gmail.com", new_subscribed_value=True, db_name=self.db_name, collection_name=self.collection_name)
        subscribed_emails = get_subscribed_emails(self.client,db_name=self.db_name,collection_name=self.collection_name)
        self.assertTrue("test1@gmail.com" in subscribed_emails)

    def test_get_id_of_an_email(self):
        obj_id = get_id_of_an_email(self.client, "test1@gmail.com",db_name=self.db_name,collection_name=self.collection_name)
        self.assertIsNotNone(obj_id)

    def test_add_unique_email(self):
        new_email = "new_test@gmail.com"
        obj_id = add_unique_email(self.client, new_email, db_name=self.db_name, collection_name=self.collection_name, encrypt=False)
        self.assertIsNotNone(obj_id)
        doc = self.collection.find_one({"_id": obj_id})
        self.assertEqual(doc["email"], new_email)

    def test_delete_document_by_email(self):
        delete_result = delete_document_by_email(self.client, "test1@gmail.com", db_name=self.db_name, collection_name=self.collection_name)
        self.assertIsNotNone(delete_result)
        self.assertEqual(delete_result.deleted_count, 1)

    def test_encrypt_values_in_db(self):
        email_count = encrypt_values_in_db(self.client, property_name="email", db_name=self.db_name, collection_name=self.collection_name, filter_query={"encrypted": False})
        self.assertGreater(email_count, 0)  

    def test_decrypt_values_in_db(self):
        encrypt_values_in_db(self.client, property_name="email", db_name=self.db_name, collection_name=self.collection_name, filter_query={"encrypted": False})
        decrypted_count = decrypt_values_in_db(self.client, property_name="email", db_name=self.db_name, collection_name=self.collection_name, filter_query={"encrypted": True})
        self.assertGreater(decrypted_count, 0)  

if __name__ == "__main__":
    unittest.main()

