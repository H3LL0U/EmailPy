import threading

import smtplib
import time
from email.message import EmailMessage
from imap_tools import MailBox, NOT
import imaplib


class Session():
    def __init__(self, sender_email: str, sender_password: str, mode: str, server_email_SMTP: str | None = None, server_port_SMTP: int | None = 587, server_email_IMAP: str | None = None, server_port_IMAP: str | None = None) -> None:
        '''
        This is a Session for IMAP and SMTP protocols it combines both of them to create a universal session

        sender_email: A email that you are logging into

        sender_password: A password for your email 

        mode: Solidifies which protocols you are going to be using  

        Set mode to "r" if you are only using IMAP protocol (read)
        Set mode to "w" if you are only using SMTP  prtotcol (write)
        Set mode to "rw" or "wr" if you are using both protocols (read write)

        server_email_SMTP: An SMTP server for your email provider
        server_email_IMAP: A IMAP servr for your email provider

        server_port_SMTP:A port for the SMTP server default 587
        server_port_IMAP:A port for IMAP server defaults to 993
        '''
        self.alive = True
        self.sender_email = sender_email
        self.sender_password = sender_password
        # imap params
        self.server_email_IMAP = server_email_IMAP
        self.server_port_IMAP = server_port_IMAP
        # smtp params
        self.server_port_SMTP = server_port_SMTP
        self.server_email_SMTP = server_email_SMTP

        self.mail_SMTP = None
        self.mail_IMAP = None

        if "w" in mode:
            self.connect_SMTP()

        if "r" in mode:

            self.connect_IMAP()

    def read_unseen_emails(self, mark_seen=False):

        for msg in self.mail_IMAP.fetch(reverse=True, mark_seen=mark_seen, criteria=NOT(seen=True)):
            yield msg
        self.mail_IMAP.folder.set("Spam")
        for msg in self.mail_IMAP.fetch(reverse=True, mark_seen=mark_seen, criteria=NOT(seen=True)):
            yield msg
        self.mail_IMAP.folder.set("Inbox")

    def read_all_emails(self, mark_seen=False):

        for msg in self.mail_IMAP.fetch(reverse=True, mark_seen=mark_seen):
            yield msg
        self.mail_IMAP.folder.set("Spam")
        for msg in self.mail_IMAP.fetch(reverse=True, mark_seen=mark_seen):
            yield msg
        self.mail_IMAP.folder.set("Inbox")

    def read_all_emails_from_user(self, user_email, mark_seen, check_spam=True, criteria=NOT(seen=True)):
        for msg in self.mail_IMAP.fetch(reverse=True, mark_seen=mark_seen, criteria=criteria):
            if msg.from_ == user_email:

                yield msg
        self.mail_IMAP.folder.set("Spam")
        if check_spam == True:
            for msg in self.mail_IMAP.fetch(reverse=True, mark_seen=mark_seen, criteria=criteria):
                if msg.from_ == user_email:

                    yield msg

        self.mail_IMAP.folder.set("Inbox")

    def find_first_mentioned_email_in_emails(self, user_email, mark_seen=False, criteria=NOT(seen=True)):
        '''
        yields the first mention of an email from some user's emails
        '''

        for msg in self.read_all_emails_from_user(user_email=user_email, mark_seen=mark_seen, criteria=criteria):
            text = msg.text
            words = text.split(" ")
            for word in words:
                if "@" in word:
                    yield word.strip().strip(":")
                    break

    def send_email(self, message: EmailMessage, reciever: str):
        '''
        message should be of type email.message.EmailMessage
        '''
        self.reconnect_if_needed()
        # if not(self.mail_SMTP is None):
        del message["To"]
        message["To"] = reciever
        del message["From"]
        message["From"] = self.sender_email

        return self.mail_SMTP.send_message(msg=message, from_addr=self.sender_email, to_addrs=reciever,)

    def update_IMAP(self, message: EmailMessage, reciever: str, folder_name="Sent SMTP"):
        del message["To"]
        message["To"] = reciever
        del message["From"]
        message["From"] = self.sender_email
        try:

            imap_client = self.mail_IMAP

            imap_client.append(message=message.as_bytes(),
                               folder=folder_name,
                               dt=imaplib.Time2Internaldate(time.time()),
                               flag_set='\\Seen'
                               )
        except Exception as e:
            print(f"Failed to update '{folder_name}' folder: {e}")

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

    def connect_IMAP(self):
        self.mail_IMAP = MailBox(self.server_email_IMAP, self.server_port_IMAP,).login(
            self.sender_email, self.sender_password)

    def connect_SMTP(self):
        try:
            self.mail_SMTP = smtplib.SMTP(
                self.server_email_SMTP, self.server_port_SMTP)
            self.mail_SMTP.ehlo()
            self.mail_SMTP.starttls()
            self.mail_SMTP.login(
                self.sender_email, password=self.sender_password)
        except Exception as e:
            self.mail_SMTP = None
            raise Exception("Connection to SMTP failed" + str(e))
            # print("Connection to SMTP failed" , e)

    def reconnect_if_needed(self):
        '''
        returns True if connection established
        else returns False
        '''
        try:

            status = self.mail_SMTP.noop()

            if status[0] == 250:
                return True
            else:
                self.connect_SMTP()
                return True
        except KeyboardInterrupt:
            self.terminate()
        except Exception:
            self.mail_SMTP = None
            self.connect_SMTP()
