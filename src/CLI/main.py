'''
Before running the CLI you need to first configure the tool
There are some values that you need to set so that the script can access your email
and the database. The variables should be set inside of the .env file
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

from CLI_session import CLI_session
import dotenv
from email_creator import *
from Session import Session

#from MYSQL import *
from Mongo_db import *



if __name__ == "__main__":

    
    #initialising variables
    dotenv.load_dotenv()
    config=dotenv.dotenv_values()
    
    test_message = email_constructor(
        None, #Will be replaced inside of the function based on the recieving email
        config["SERVER_SENDER_EMAIL"],
        config["SUBJECT"],
        view_html(config["EMAIL_CONTENTS_PATH_TXT"]),
        view_html(config["EMAIL_CONTENTS_PATH_HTML"])
    )

    session = Session(server_email_SMTP=config["SERVER_SENDER_EMAIL"],
                    server_port_SMTP=config["SENDER_EMAIL_PORT"],
                    sender_email=config["SENDER_EMAIL"],
                    sender_password=config["SENDER_EMAIL_PASSWORD"],
                    mode="w")
    
    reader_session = Session(sender_email=config["READER_EMAIL"],
                    sender_password=config["READER_EMAIL_PASSWORD"],
                    server_port_IMAP= config["READER_EMAIL_PORT"],
                    server_email_IMAP=config["SERVER_READER_EMAIL"], #imap-mail.outlook.com
                    mode="r")
    log("Sessions started")   
    database_connection = MongoClient(config["MONGO_DB_LINK"])

    CLI_session(db_connection=database_connection,email_reader_session=reader_session,email_sender_session = session,preconstructed_email = test_message)

    database_connection.close()
    reader_session.terminate()
        