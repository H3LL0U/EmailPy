import dotenv
from email_creator import email_constructor, view_html
from Session import Session
import mysql.connector
from mysql.connector import Error, MySQLConnection
import sqlite3
from email.message import EmailMessage
from MYSQL import *
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


if __name__ == "__main__":
    
    #initialising variables
    dotenv.load_dotenv()
    config=dotenv.dotenv_values()
    
    session = Session(server_email_SMTP=config["SERVER_EMAIL"],
                    server_port_SMTP=config["PORT"],
                    sender_email=config["EMAIL"],
                    sender_password=config["PASSWORD"],
                    server_port_IMAP= 993,
                    server_email_IMAP="imap-mail.outlook.com", #imap-mail.outlook.com
                    mode="")
    
    print("Session started")   
    test_email =email_constructor(
        config["RECIEVER_EMAIL"], #reciever
        config["EMAIL"], #sender
        config["SUBJECT"], #subject
        view_html(config["EMAIL_CONTENTS_PATH_TXT"]), #message txt
        view_html(config["EMAIL_CONTENTS_PATH_HTML"]) #html view
        )
    
    database_connection = connect_to_database(
        database=config["DATABASE_NAME"],
        host=config["DATABASE_HOST"],
        user = config["DATABASE_USER"],
        password=config["DATABASE_PASSWORD"],
        port=config["DATABASE_PORT"]
    )

    
    all_subscribed_emails = get_all_subscribed_emails(database_connection)
    #session.send_email(test_email, config["RECIEVER_EMAIL"])
    
    #send_messages_to_users(all_subscribed_emails,session=session,msg=test_email,limit=400)
    #send_query(database_connection,"TRUNCATE TABLE visited;")
    database_connection.close()
    session.terminate()
        