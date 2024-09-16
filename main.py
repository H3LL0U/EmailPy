import dotenv
from email_creator import email_constructor, view_html
from Session import Session

from email.message import EmailMessage
#from MYSQL import *
import pymongo
from Mongo_db import *
'''
Example for the config:
EMAIL=sender@outlook.com
PASSWORD=VerySecurePassword
SERVER_EMAIL=smtp-mail.outlook.com
PORT=587
RECIEVER_EMAIL=reciever@outlook.com


EMAIL_CONTENTS_PATH_TXT=./message.txt
EMAIL_CONTENTS_PATH_HTML=./message.html
SUBJECT=Subject

'''

def send_emails_to_users(mongo_client:pymongo.MongoClient,email_session:Session,limit):
    for idx, reciever in enumerate(get_subscribed_emails(mongo_client)):
        if idx <limit:
            
            email_session.send_email(message=test_email,reciever=reciever)

def remove_users_who_unsubscribed(session:Session,database_connection:MongoClient):
    unseen_emails = session.read_unseen_emails()
    for email in unseen_emails:

        _from,subject,text, = email.from_,email.subject,email.text
        
        if "unsubscribe" in subject or "unsubscribe" in text:
            _from = _from[:_from.rfind("@")] + "@leerling.o2g2.nl"
            update_subscribed_by_email(database_connection,_from)
            print(f"unsubscribed user: {_from}")
if __name__ == "__main__":
    
    #initialising variables
    dotenv.load_dotenv()
    config=dotenv.dotenv_values()
    '''
    session = Session(server_email_SMTP=config["SERVER_EMAIL"],
                    server_port_SMTP=config["PORT"],
                    sender_email=config["EMAIL"],
                    sender_password=config["PASSWORD"],
                    server_port_IMAP= 993,
                    server_email_IMAP="imap-mail.outlook.com", #imap-mail.outlook.com
                    mode="w")
    '''
    reader_session = Session(sender_email=config["READER_EMAIL"],
                    sender_password=config["READER_EMAIL_PASSWORD"],
                    server_port_IMAP= 993,
                    server_email_IMAP="imap.gmx.com", #imap-mail.outlook.com
                    mode="r")
    print("Sessions started")   
    test_email =email_constructor(
        config["RECIEVER_EMAIL"], #reciever
        config["EMAIL"], #sender
        config["SUBJECT"], #subject
        view_html(config["EMAIL_CONTENTS_PATH_TXT"]), #message txt
        view_html(config["EMAIL_CONTENTS_PATH_HTML"]) #html view
        )
    database_connection = MongoClient(config["MONGO_DB_LINK"])

    #send_emails_to_users(database_connection,10)

    

    



    #cleanup

    #session.terminate()
    database_connection.close()
    reader_session.terminate()
        