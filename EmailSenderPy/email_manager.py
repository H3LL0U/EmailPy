import dotenv
from email_creator import *
from .Session import Session

from email.message import EmailMessage
#from MYSQL import *
import pymongo
from .Mongo_db import *
import time

def clear_inactive_emails(database_connection:MongoClient,reader_session:Session,mark_seen = True):
    '''
    Removes all emails that are inactive by checking the reply from mailer-daemon@gmx.net and removing the mentioned email
    '''
    for inactive_email in reader_session.find_first_mentioned_email_in_emails("mailer-daemon@gmx.net",mark_seen=mark_seen):
        #delete_document_by_email(connection=database_connection,email=inactive_email)
        add_property_to_documents(database_connection,"exists",False,filter_query={"email":inactive_email})

def send_emails_to_users(mongo_client:pymongo.MongoClient,email_session_reader:Session,email_session:Session,limit:int,msg:EmailMessage,start_from=0,timeout_between_emails_seconds=0):
    '''
    Sends the messages to users from the database

    mongo_client: connection to the mongodatabase

    email_session_reader: an object of type Session.Session that has mode="r" enabled and is correctly configured (will be used to read emails)
    
    email_session: an object of type Session.Session that has "w" enabled and is correctly configured (can be the same as email_session_reader)
    
    limit: sets a limit on how many emails should be sent
    
    msg_func: function that creates a sent email you can use email_creator.email_constructor_preconstructed(config=config)
    
    start_from:speciefies after how many iterations you can start sending emails
    
    limit:speciefies how many emails should be sent
    '''
    remove_users_who_unsubscribed(database_connection=mongo_client,session=email_session_reader)
    email_session_reader.terminate()
    emails_to_send_to = get_subscribed_emails(mongo_client)[start_from:]
    
    
    limit-=start_from
    for idx, reciever in enumerate(emails_to_send_to):
        if idx <limit:
            
            del msg["To"]
            msg["To"] = reciever
            encrypted_email = get_encrypted_version(mongo_client,reciever)
            replace_text_of_the_message(msg,"https://phishing-awareness-website.onrender.com/",f"https://phishing-awareness-website.onrender.com/{encrypted_email}")
                
            print("errors:" , email_session.send_email(message=msg,reciever=reciever))
            print(f"email sent to: {reciever}")
            time.sleep(timeout_between_emails_seconds)
            
            
def remove_users_who_unsubscribed(session:Session,database_connection:MongoClient):
    '''
    Reads all unseen emails and unsubscribes users who replied with "unsubscribe" or had a subject "unsubscribe"
    
    session: a Session.Session object with mode="r" enabled
    database_connection: MongoClient object connection
    '''
    unseen_emails = session.read_unseen_emails(mark_seen=True)
    for email in unseen_emails:

        _from,subject,text, = email.from_,email.subject,email.text
        text = text.lower()
        subject = subject.lower()
        if "unsubscribe" in subject or "unsubscribe" in text:
            _from = _from[:_from.rfind("@")] + "@leerling.o2g2.nl"
            update_subscribed_by_email(database_connection, encrypt_value(_from))
            print(f"unsubscribed user: {_from}")