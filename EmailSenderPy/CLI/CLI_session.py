from command_from_function import Command, create_commands_by_imports
from EmailSenderPy import email_manager
from EmailSenderPy import Mongo_db
from email.message import EmailMessage
from EmailSenderPy import Session as Email_Session
from pymongo import MongoClient
import os.path
import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))


class CLI_session():
    def __init__(self, db_connection: MongoClient | None = None, email_reader_session: Email_Session | None = None, email_sender_session: Email_Session | None = None, preconstructed_email: EmailMessage | None = None):
        self.running = True
        self.version = "0.0.2"
        self.implemented_commands = self.get_implemented_commands()
        self.email_reader_session = email_reader_session
        self.email_sender_session = email_sender_session
        self.db_connection = db_connection
        self.preconstructed_email = preconstructed_email
        BLACK_LIST = ["convert_string_to_urlsafe_base64",
                      "email_constructor",
                      "log",
                      "pad",
                      "remove_newline_from_emails",
                      "replace_text_of_the_message",
                      "unpad",
                      "view_html"]  # functions which should not be included
        self.all_commands = create_commands_by_imports(email_manager, black_list=BLACK_LIST, mongo_client=db_connection,
                                                       email_session_reader=email_reader_session,
                                                       email_session=email_sender_session,
                                                       database_connection=db_connection,
                                                       session=email_reader_session,
                                                       connection=db_connection)

        self.main()

    def main(self) -> None:
        print(
            f"EmailSender CLI tool version {self.version}\nType help voor commands")
        while self.running:
            user_command = self.split_into_subcategories(input())

            for command in self.all_commands:

                if not user_command is None and command.name == user_command["command"]:
                    try:
                        print(command.call_command(**user_command["params"]))
                    except TypeError as e:
                        print(
                            "Not all necessary parameters were satisfied or there are non-existant parameters")
                    user_command = None
                    break

            if user_command is None:
                continue
            match user_command["command"]:
                case "help":
                    self.help_command(user_command)

                case "exit":
                    self.exit_command(user_command)

                # case "send_emails_to_users":
                #    self.send_emails_to_users_command(user_command)

                # case "send_email_to_user":
                #    self.send_email_to_user_command(user_command)

                case _:
                    print(
                        f"Could not find the command {user_command["command"]}")

    def split_into_subcategories(self, input_str: str) -> dict[str:str, str:any] | None:
        '''
        Takes a string and returns a dictionary which contains the following categories:
        "command": "some_command" (str)
        "params": {"param_name" : value, ...}
        '''
        all_params_and_values = {}
        parsed_str = input_str.replace(" ", "")

        split_str = parsed_str.split("--")

        main_command = split_str[0]
        if len(split_str) > 1:
            try:
                params_and_values = [
                    dict([p_and_val.split("=", maxsplit=1)]) for p_and_val in split_str[1:]]

            except ValueError:
                print('Syntax error: Ensure parameters are in the form -param=value')
                return None
            for d in params_and_values:
                all_params_and_values.update(d)
            # convert the value to int or float if necessary after removing the "" or ''
            all_params_and_values = {param: self.check_conversion_to_int_or_float(
                value) for param, value in all_params_and_values.items()}

        return {"command": main_command,
                "params": all_params_and_values}

    def get_command_description(self, command_name):
        absolute_path = os.path.dirname(__file__)

        with open(f"{absolute_path}/command_descriptions/help_{command_name}.txt", "r") as help_command:
            return help_command.read()

    def get_implemented_commands(self) -> list[str]:
        absolute_path = os.path.dirname(__file__)
        all_commands = os.listdir(f"{absolute_path}/command_descriptions")
        return [command.replace("help_", "").replace(".txt", "") for command in all_commands]

    def check_conversion_to_int_or_float(self, value: str) -> str | int | float:
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
            return value.replace("'", "").replace('"', '')
    # =====Command behaviour=======

    def exit_command(self, user_command: dict[str:str, str:any]):
        print("Closing...")
        self.running = False

    def help_command(self, user_command: dict[str:str, str:any]) -> None:
        if "command" in user_command["params"]:
            try:
                print(self.get_command_description(
                    user_command["params"]["command"]))
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
            '''.replace("    ", ""))
