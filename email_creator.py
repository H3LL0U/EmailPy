from email.message import EmailMessage


def view_html(path:str) -> str:
    '''
    Returns contents of a file from a selected path as a string
    '''
    with open(path, "r",encoding="UTF-8") as email:
        return email.read()

def email_constructor(to:str,sender_email:str,subject:str,message_content:str, message_content_html:str = "") -> bool:
    #Construct a logged in server using login_SMTP function
    
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to
    message["BCC"] = sender_email

    message.set_content(message_content)
    message.add_alternative(message_content_html,subtype = "html",)

    return message

    







