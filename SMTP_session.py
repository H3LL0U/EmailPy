import threading
import command_objects
import smtplib
import time
from email.message import EmailMessage
class SMTPsession():
    def __init__(self,server_email,server_port,sender_email,sender_password) -> None:
        
        self.commands = []

        self.main_login_thread = threading.Thread( target=lambda: self.login_SMTP_thread(server_email,
                                          server_port,
                                          sender_email,
                                          sender_password))
        self.main_login_thread.daemon = True
        self.main_login_thread.start()


    def login_SMTP_thread(self,email_server_address,server_port,sender_email,password) -> bool|Exception:
        
        command = command_objects.DoNothingCommand()
        try:
            with smtplib.SMTP(email_server_address,server_port) as server:
                server.ehlo()
                server.starttls()
                server.login(sender_email,password=password)

                while server:
                    if self.commands:
                        command = self.commands.pop(0)
                    else:
                        command = command_objects.DoNothingCommand()
                    match type(command):
                        
                        case command_objects.SendMessageCommand:
                            server.send_message(msg=command.message,from_addr=sender_email,to_addrs=command.reciever)
                            time.sleep(5)
                        case command_objects.TerminateCommand:
                            break

                        case _:
                            pass


            return True
        
        except KeyboardInterrupt:
            print("disconecting")
        except Exception as e:
            print(e)
            return e
    

    def add_command(self,command:command_objects._GeneralCommand) -> bool:
        '''
        Returns True if command exists and has been added to the stack
        Returns False if command does not exist
        '''
        if isinstance(command,command_objects._GeneralCommand):
            self.commands.append(command)
            return True
        return False
    
    def send_email(self,message: EmailMessage, reciever: str):
        '''
        message should be of type email.message.EmailMessage
        '''
        self.add_command(
            command_objects.SendMessageCommand(message, reciever)
        )
    def terminate(self) -> None:
        '''
        Terminates the current session
        '''
        self.add_command(command_objects.TerminateCommand(1))

    def clear_commands(self) -> None:
        '''
        Clears all previously sent commands if they were not executed yet 
        '''
        self.commands = []

    def is_alive(self) -> bool:
        '''
        Checks if the current session thread is active
        active -> True
        closed -> False
        '''
        return self.main_login_thread.is_alive()