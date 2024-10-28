from email.message import EmailMessage


def view_html(path:str) -> str:
    '''
    Returns contents of a file from a selected path as a string
    '''
    with open(path, "r",encoding="UTF-8") as email:
        return email.read()

def email_constructor(to:str,sender_email:str,subject:str,message_content:str, message_content_html:str = ""):
    #Construct a logged in server using login_SMTP function
    
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to
    message["BCC"] = sender_email
    
    message.set_content(message_content)
    message.add_alternative(message_content_html,subtype = "html",)
        

    return message
from email.message import EmailMessage


def replace_text_of_the_message(msg:EmailMessage,old_str:str,new_str:str):
    if msg.is_multipart():
        
        for part in msg.iter_parts():
            content_type = part.get_content_type()  
            
            if content_type == 'text/plain' or content_type == 'text/html':
                
                original_content = part.get_payload(decode=True).decode(part.get_content_charset())

                
                updated_content = original_content.replace(old_str, new_str)

                
                part.set_payload(updated_content.encode(part.get_content_charset()))
    else:
        
        original_content = msg.get_content()
        updated_content = original_content.replace(old_str, new_str)
        msg.set_content(updated_content)
        return msg








