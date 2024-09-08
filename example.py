import dotenv
from email_creator import email_constructor, view_html
import command_objects
import SMTP_session

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
    session = SMTP_session.SMTPsession(config["SERVER_EMAIL"],
                                       config["PORT"],
                                       config["EMAIL"],
                                       config["PASSWORD"])



    while session.is_alive():
        
        test_email =email_constructor(
        config["RECIEVER_EMAIL"], #reciever
        config["EMAIL"], #sender
        config["SUBJECT"], #subject
        view_html(config["EMAIL_CONTENTS_PATH_TXT"]), #message txt
        view_html(config["EMAIL_CONTENTS_PATH_HTML"]) #html view

        )

        session.add_command(command_objects.SendMessageCommand(test_email,config["RECIEVER_EMAIL"]))
        
        session.add_command(command_objects.TerminateCommand(1))

    print("closed")
        