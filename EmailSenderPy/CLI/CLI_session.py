import os.path
from pymongo import MongoClient
from Session import Session as Email_Session
from email.message import EmailMessage
import Mongo_db
import email_manager
class CLI_session():
    def __init__(self,db_connection:MongoClient|None = None, email_reader_session:Email_Session|None = None,email_sender_session:Email_Session|None = None, preconstructed_email:EmailMessage|None = None  ):
        self.running = True
        self.version = "0.0.2"
        self.implemented_commands = self.get_implemented_commands()
        self.email_reader_session = email_reader_session
        self.email_sender_session = email_sender_session
        self.db_connection = db_connection
        self.preconstructed_email = preconstructed_email





        self.main()
        
    def main(self) -> None:
        print(f"EmailSender CLI tool version {self.version}\nType help voor commands")
        while self.running:
            user_command = self.split_into_subcategories(input())
            
            match user_command["command"]:
                case "help" :
                    self.help_command(user_command)
                    
                case "exit":
                    self.exit_command(user_command)

                case "send_emails_to_users":
                    self.send_emails_to_users_command(user_command)

                case "send_email_to_user":
                    self.send_email_to_user_command(user_command)

                case _:
                    print(f"Could not find the command {user_command["command"]}")
    
    def split_into_subcategories(self,input_str:str) -> dict[str:str,str:any] | None:
        '''
        Takes a string and returns a dictionary which contains the following categories:
        "command": "some_command" (str)
        "params": {"param_name" : value, ...}
        '''
        all_params_and_values = {}
        parsed_str = input_str.replace(" ", "")

        split_str = parsed_str.split("--")
        
        main_command = split_str[0]
        if len(split_str) >1:
            try:
                params_and_values = [dict([p_and_val.split("=")]) for p_and_val in split_str[1:]]

            except ValueError:
                print('Syntax error: Ensure parameters are in the form -param=value')
                return None
            for d in params_and_values:
                all_params_and_values.update(d)
            #convert the value to int or float if necessary after removing the "" or '' 
            all_params_and_values = {param: self.check_conversion_to_int_or_float(value) for param,value in all_params_and_values.items()}

        return {"command":main_command,
                "params": all_params_and_values}
    
    def get_command_description(self,command_name):
        absolute_path = os.path.dirname(__file__)
        
        with open(f"{absolute_path}/command_descriptions/help_{command_name}.txt" ,"r") as help_command:
            return help_command.read()
    def get_implemented_commands(self) -> list[str]:
        absolute_path = os.path.dirname(__file__)
        all_commands = os.listdir(f"{absolute_path}/command_descriptions")
        return [command.replace("help_", "").replace(".txt","") for command in all_commands]

    def check_conversion_to_int_or_float(self,value:str)-> str|int|float:
        '''
        Checks if the value can be converted to float or string
        returns: int | float if can be converted
        returns: str if cannot be converted with removed "" or ''
        '''
        
        try:
            if int(value) == float(value):
                return int(value)
            return float(value)

        except ValueError:
            return value.replace("'","").replace('"','')
    #=====Command behaviour=======
    def exit_command(self,user_command:dict[str:str,str:any]):
        print("Closing...")
        self.running = False


    def help_command(self,user_command:dict[str:str,str:any]) ->None:
        if "command" in user_command["params"]:
            try:
                print(self.get_command_description(user_command["params"]["command"]))
            except FileNotFoundError:
                print("could not find the command you are describing")
        else:


            print(f'''Syntax for CLI:
            main_command --some_param=some_value --param=...
            
            this CLI tool is not white-space sensitive and will remove any whitespace
            to know more about a specific command type:
            help --command=<command_name>
            
                  
            In order for some of the commands to work .env file should be configured
            if you want to know what should be configured for each command type
            help --command=<command_name>
            All possible configurations in the .env file:
            
            SENDER_EMAIL= <email from which you are planning to send the emails>
            SENDER_EMAIL_PORT= <an SMTP port for the server email (mostly 587)>
            SENDER_EMAIL_PASSWORD = <password of your email>
            SERVER_SENDER_EMAIL <SMTP server email of your email provider>

            READER_EMAIL = <email to which you recieve the unsubscribe requests (can be the same as the sender email)>
            SENDER_EMAIL_PASSWORD <password for this email>
            READER_EMAIL_PORT = <IMAP port (mostly 993)>
            SERVER_READER_EMAIL = <IMAP server email of your email provider>

            SUBJECT = <subject of your email>
            EMAIL_CONTENTS_PATH_TXT = <Path/to/your/email.txt>
            EMAIL_CONTENTS_PATH_HTML = <Path/to/your/email.html>
            Availabe commands:
            {"\n".join(self.implemented_commands)}
            '''.replace("    ",""))

    def send_emails_to_users_command(self,user_command:dict[str:str,str:any]) -> None:
        #check for correct configuration
        if self.db_connection is None:
            print("No email session was provided. Check configuration")
            return
        if self.email_sender_session is None:
            print("No database session sender was provided. Check configuration")
            return
        if self.email_reader_session is None:
            print("No database session reader was provided. Check configuration")
        if self.preconstructed_email is None:
            print("No preconstructed email was provided. Check configuration")
        #setting parameters
        
        #default values:
        LIMIT = -1 #no limit
        DELAY = 600 #600 seconds between emails
        START_FROM = 0
        if "limit" in user_command["params"]:
            LIMIT = user_command["params"]["limit"]
        if "delay" in user_command["params"]:
            DELAY = user_command["params"]["delay"]
        if "start_from" in user_command["params"]:
            START_FROM =  user_command["params"]["start_from"]
        
        print(f"Starting sending emails with the following parameters\ndelay: {DELAY}\nlimit: {LIMIT}\nstart_from: {START_FROM}")


        email_manager.send_emails_to_users(self.db_connection,self.email_reader_session,self.email_sender_session,LIMIT,self.preconstructed_email,START_FROM,DELAY)
    def send_email_to_user_command(self,user_command:dict[str:str,str:any]) -> None:
        #check correct configuration
        if self.email_sender_session is None:
            print("No database session sender was provided. Check configuration")
            return
        
        #check params
        if "user" in user_command["params"]:
            USER = user_command["params"]["user"]

        else:
            print("No --user specified. Please specify the user")
            return
        print(f"Sending an email to {USER}")
        self.email_sender_session.send_email(self.preconstructed_email,USER)
        

    

        
