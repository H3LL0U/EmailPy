import threading
import command_objects
import smtplib
import time
from email.message import EmailMessage
from imap_tools import MailBox, NOT
class Session():
    def __init__(self,sender_email:str,sender_password:str, mode:str,server_email_SMTP:str|None = None,server_port_SMTP:str|None = None,server_email_IMAP:str=None,server_port_IMAP:str|None = None) -> None:
        '''
        Set mode to "r" if you are only using IMAP protocol (read)
        Set mode to "w" if you are only using SMTP  prtotcol (write)
        Set mode to "rw" or "wr" if you are using both protocols (read write)
        '''
        self.alive = True
        self.sender_email = sender_email
        
        self.mail_SMTP = None
        self.mail_IMAP = None



        

        #create an SMTP protocol thread if write is enabled
        if "w" in mode:
            self.mail_SMTP = smtplib.SMTP(server_email_SMTP,server_port_SMTP)
            self.mail_SMTP.ehlo()
            self.mail_SMTP.starttls()
            self.mail_SMTP.login(sender_email,password=sender_password)

        #create an IMAP protocol thread if write is enabled
        if "r" in mode:
            self.mail_IMAP = MailBox(server_email_IMAP,server_port_IMAP)
            self.mail_IMAP.login(sender_email,sender_password)
            
            
            

    '''def login_SMTP_thread(self,email_server_address,server_port,sender_email,password) -> bool|Exception:
        
        command = command_objects.DoNothingCommand()
        try:
            with smtplib.SMTP(email_server_address,server_port) as server:
                server.ehlo()
                server.starttls()
                server.login(sender_email,password=password)

                while server:
                    if self.commands_SMTP:
                        #find a command that uses SMTP protocol
                        if self.commands_SMTP[0].protocol == "SMTP":

                            command = self.commands.pop(0)
                        else:
                            self.commands.pop(0)
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
        








        except KeyboardInterrupt as e:
            
            return False 
        


    def add_command(self,command:command_objects._GeneralCommand) -> bool:
        "
        Returns True if command exists and has been added to the stack
        Returns False if command does not exist
        "
        if isinstance(command,command_objects._GeneralCommand):
            if command.protocol == "SMTP":
                self.commands_SMTP.append(command)
            elif command.protocol == "IMAP":
                self.commands_IMAP.append(command)
            elif command.protocol is None:
                self.commands_IMAP.append(command)
                self.commands_SMTP.append(command)
            return True
        return False
    '''
    def read_unseen_emails(self,inbox_type:str = "Inbox",mark_seen = False):
        self.mail_IMAP.folder = inbox_type
        for msg in self.mail_IMAP.fetch(reverse=True,mark_seen=mark_seen,criteria=NOT(seen=True)):
            yield msg
    def send_email(self,message: EmailMessage, reciever: str):
        '''
        message should be of type email.message.EmailMessage
        '''
        #if not(self.mail_SMTP is None):
        
        return self.mail_SMTP.send_message(msg=message,from_addr=self.sender_email,to_addrs=reciever)
    def terminate(self) -> None:
        '''
        Terminates the current session
        '''
        
        if not (self.mail_SMTP is None):
            self.mail_SMTP.close()
            self.mail_IMAP = None
        if not (self.mail_IMAP is None):
            self.mail_IMAP.logout()
            self.mail_IMAP = None
        self.alive = False
    def is_alive(self) -> bool:
        return self.alive

