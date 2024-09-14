import threading

import smtplib
import time
from email.message import EmailMessage
from imap_tools import MailBox, NOT
import imaplib
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
            
            self.mail_IMAP = MailBox(server_email_IMAP,server_email_IMAP).login(sender_email,sender_password)
            
            
            
            

            
    def read_unseen_emails(self,mark_seen = False):
        
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

