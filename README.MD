# EmailPy

## What is this repository for?
This repository is a part of Phishing awareness website project (https://github.com/users/H3LL0U/projects/8).
It is used as a tool to send e-mails and to interact with the database containing data collected from the users visiting the website.
(https://github.com/H3LL0U/Phishing_awareness_website)
## What are the features?
This repository can be used as a python package or the functionality can also be accessed through the CLI tool. (EmailSenderPy/CLI/main.py to run the CLI)
You can create e-mail sessions with the help of which you can send e-mails using SMTP protocol or read them using IMAP protocol.
Also you can access/change data in the MongoDB database using the functions from Mongo_db.py  
Eveything is documented in the doc strings of the classes and in the files.
Keep in mind that you need to set everything up in the enviorment variables or in the .env file

### Example
```
            SENDER_EMAIL= <email from which you are planning to send the emails>
            SENDER_EMAIL_PORT= <an SMTP port for the server email (mostly 587)>
            SENDER_EMAIL_PASSWORD = <password of your email>
            SERVER_SENDER_EMAIL <SMTP server email of your email provider>

            READER_EMAIL = <email to which you recieve the unsubscribe requests (can be the same as the sender email)>
            SENDER_EMAIL_PASSWORD = <password for this email>
            READER_EMAIL_PORT = <IMAP port (mostly 993)>
            SERVER_READER_EMAIL = <IMAP server email of your email provider>

            SUBJECT = <subject of your email>
            EMAIL_CONTENTS_PATH_TXT = <Path/to/your/email.txt>
            EMAIL_CONTENTS_PATH_HTML = <Path/to/your/email.html>
```

### How to install as a package?
It is easy! Just run:
```
pip install git+https://github.com/H3LL0U/EmailPy.git
```
### Contribution
If you feel the need to contribute please create an issue.

