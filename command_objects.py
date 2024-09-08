# Initialize the following commands and put them inside of a 
# Command array in the main.py
# To execute them
from email.message import EmailMessage
class _GeneralCommand():
    pass
class DoNothingCommand(_GeneralCommand):
    def __init__(self) -> None:
        pass

class SendMessageCommand(_GeneralCommand):
    def __init__(self,message:EmailMessage,reciever:str):
        self.message = message
        self.reciever = reciever

class TerminateCommand(_GeneralCommand):
    def __init__(self, terminate:bool) -> None:
        self.terminate = terminate