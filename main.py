import dotenv
from email_creator import email_constructor, view_html ,email_constructor_preconstructed
from Session import Session

from email.message import EmailMessage
#from MYSQL import *
import pymongo
from Mongo_db import *
import time
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

def send_emails_to_users(mongo_client:pymongo.MongoClient,email_session_reader:Session,email_session:Session,limit,msg_func,start_from=0,timeout_between_emails_seconds=0):
    
    remove_users_who_unsubscribed(database_connection=mongo_client,session=email_session_reader)
    email_session_reader.terminate()
    emails_to_send_to = get_subscribed_emails(mongo_client)[start_from:]
    
    for idx, reciever in enumerate(emails_to_send_to):
        if idx <limit:
            
            msg = msg_func(reciever)
            print("errors:" , email_session.send_email(message=msg,reciever=reciever))
            print(f"email sent to: {reciever}")
            time.sleep(timeout_between_emails_seconds)
            
            
def remove_users_who_unsubscribed(session:Session,database_connection:MongoClient):
    unseen_emails = session.read_unseen_emails(mark_seen=True)
    for email in unseen_emails:

        _from,subject,text, = email.from_,email.subject,email.text
        
        if "unsubscribe" in subject or "unsubscribe" in text:
            _from = _from[:_from.rfind("@")] + "@leerling.o2g2.nl"
            update_subscribed_by_email(database_connection,_from)
            print(f"unsubscribed user: {_from}")
def from_txt_to_db(path_to_txt_file,database_connection,should_have_second_and_top_level_domain=""):
    '''
    Gets emails stored on a txt line and ads them line by line to the database if they were not yet there
    '''
    with open(path_to_txt_file,"r") as txt:
        for email in txt.readlines():
            email = email.strip("\n")
            if email.endswith(should_have_second_and_top_level_domain):
                print(add_unique_email(database_connection,email))

if __name__ == "__main__":
    
    #initialising variables
    dotenv.load_dotenv()
    config=dotenv.dotenv_values()
    
    session = Session(server_email_SMTP=config["SERVER_EMAIL"],
                    server_port_SMTP=config["PORT"],
                    sender_email=config["EMAIL"],
                    sender_password=config["PASSWORD"],
                    mode="w")
    
    reader_session = Session(sender_email=config["READER_EMAIL"],
                    sender_password=config["READER_EMAIL_PASSWORD"],
                    server_port_IMAP= 993,
                    server_email_IMAP="imap.gmx.com", #imap-mail.outlook.com
                    mode="r")
    print("Sessions started")   
    database_connection = MongoClient(config["MONGO_DB_LINK"])

    #send_emails_to_users(database_connection,10)
    
    

    #from_txt_to_db(path_to_txt_file="leerling_emails_db\leerling_emails4.txt",database_connection=database_connection,should_have_second_and_top_level_domain="leerling.o2g2.nl")
    #print(get_ammount_documents(database_connection))
    #time.sleep(600)
    send_emails_to_users(database_connection,email_session=session, email_session_reader=reader_session,limit=9999,start_from=130, msg_func = email_constructor_preconstructed(config=config), timeout_between_emails_seconds=600)
    #session.send_email(email_constructor_preconstructed(config)("3007651@leerling.o2g2.nl"),"3007651@leerling.o2g2.nl")
    #cleanup

    #session.terminate()
    database_connection.close()
    reader_session.terminate()
        