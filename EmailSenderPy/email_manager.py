import dotenv
from .email_creator import *
from .Session import Session

from email.message import EmailMessage
#from MYSQL import *
import pymongo
from .Mongo_db import *
import time

import datetime

def clear_inactive_emails(database_connection:MongoClient,reader_session:Session,mark_seen = True):
    '''
    Removes all emails that are inactive by checking the reply from mailer-daemon@gmx.net and removing the mentioned email
    '''
    for inactive_email in reader_session.find_first_mentioned_email_in_emails("mailer-daemon@gmx.net",mark_seen=mark_seen):
        #delete_document_by_email(connection=database_connection,email=inactive_email)
        add_property_to_documents(database_connection,"exists",False,filter_query={"email":inactive_email})

def send_emails_to_users(mongo_client:pymongo.MongoClient,email_session_reader:Session,email_session:Session ,msg_location:str, email_type:str,subject:str,message_location_html:str = "", limit = 955,start_from=0,timeout_between_emails_seconds=0):
    '''
    Sends the messages to users from the database

    mongo_client: connection to the mongodatabase

    email_session_reader: an object of type Session.Session that has mode="r" enabled and is correctly configured (will be used to read emails)
    
    email_session: an object of type Session.Session that has "w" enabled and is correctly configured (can be the same as email_session_reader)
    
    limit: sets a limit on how many emails should be sent
    
    start_from:speciefies after how many iterations you can start sending emails
    
    limit:speciefies how many emails should be sent

    msg_location: path to the email that you want to send

    subject: the subject of the email

    message_location_html: path to the email written using html (optional)

    timeout_between_emails_seconds: delay between each sent email
    '''
    try:
        remove_users_who_unsubscribed(database_connection=mongo_client,session=email_session_reader)
        
        emails_to_send_to = get_subscribed_emails(mongo_client)[start_from:]
        
        
        limit-=start_from
        for idx, reciever in enumerate(emails_to_send_to):
            if idx <limit:
                
                print(f"reciever number: {idx}")
                
                send_email_to_user(email_session=email_session,
                                email=reciever,
                                msg_location=msg_location,
                                message_location_html=message_location_html,
                                email_type=email_type,
                                database_connection=mongo_client,
                                text_to_replace="https://phishing-awareness-website.onrender.com/",
                                new_text=f"https://phishing-awareness-website.onrender.com/{email_type}/{encrypt_value(reciever)}",
                                subject=subject)

                

                print(f"email sent to: {reciever}")
                time.sleep(timeout_between_emails_seconds)
    except KeyboardInterrupt:
        print("Stopping...")
        return
            
            
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

def send_email_to_user(email_session: Session, email:str,msg_location:str,subject:str, message_location_html = "", email_type = None, database_connection = None,text_to_replace = None, new_text = None) -> None:
    '''
    Sends an email to user based on provided parameters

    if email_type and database_connection are set it will also update the date_of_email parameter in the database
    for that user
    '''
    try:
        msg_text_content = view_html(msg_location)
        msg_html_content = view_html(message_location_html)
    except FileNotFoundError:
        print("One of the provided file locations does not exist")
        return
    msg = email_constructor(email,
                            email_session.sender_email,
                            subject,
                            msg_text_content,
                            msg_html_content)

    if not text_to_replace is None and not new_text is None:

        replace_text_of_the_message(msg,text_to_replace,new_text)



    if email_session is None:
        print("No database session sender was provided. Check configuration")
        return
    


    # Updating the database if needed based on email_type and database connection parameters
    if email_type and database_connection :
        #validating the email type

        redirect_type_doc = get_documents_by_query(database_connection,{"allowed_type": email_type},collection_name="redirect_types") 
        if not redirect_type_doc:
            print("This Email type is not allowed")
            return
        else:
            try:
                date_of_visit_value = get_email_properties(database_connection,email,auto_decrypt=False)["date_of_email"]
            except KeyError:
                
                date_of_visit_value = "None"
            
            if date_of_visit_value == "None":
                new_date_of_visit_value = {email_type:datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}
            elif email_type in date_of_visit_value:
                new_date_of_visit_value = date_of_visit_value
            else:
                new_date_of_visit_value = date_of_visit_value
                new_date_of_visit_value[email_type] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            email_id = get_id_of_an_email(database_connection,encrypt_value(email),auto_decrypt=False)
            print(email_id)

            add_property_to_documents(database_connection,"date_of_email",new_date_of_visit_value,filter_query={"_id":email_id})



    print(f"Sending an email to {email}")
    try:
        email_session.send_email(msg, email)
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print("Something went wrong when sending an e-email check the configuration")
        print (e)