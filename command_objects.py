# Initialize the following commands and put them inside of a 
# Command array in the main.py
# To execute them
from email.message import EmailMessage
class _GeneralCommand():
    def __init__(self,protocol:str) -> None:
        '''
        Set protocol to "SMTP" if the command uses SMTP
        Set protocol to "IMAP" if the command uses IMAP
        Set protocol to None if no protocol is used 
        '''
        self.protocol = protocol
class DoNothingCommand(_GeneralCommand):
    def __init__(self) -> None:
        super().__init__(None)

class SendMessageCommand(_GeneralCommand):
    def __init__(self,message:EmailMessage,reciever:str):
        super().__init__("SMTP")
        self.message = message
        self.reciever = reciever

class TerminateCommand(_GeneralCommand):
    def __init__(self, terminate:bool) -> None:
        super().__init__(None)
        self.terminate = terminate