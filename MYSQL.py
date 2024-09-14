import mysql.connector
import mysql.connector
from mysql.connector import Error, MySQLConnection
import sqlite3
from Session import Session
from email.message import EmailMessage
def connect_to_database(host,user,password,database,port):
    try:
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port  
        )
        return connection

    except Exception as e:
        print(e)



def send_query(connection:MySQLConnection,query:str,fetch = False):
    cursor = connection.cursor()
    cursor.execute(query)
    
    if fetch:
        return cursor.fetchall()
    else:
        connection.commit()
def get_all_tables_sqlite(path_to_db="leerling_emails_db\leerling_emails.db"):
    connection = sqlite3.connect(path_to_db)
    cur = connection.cursor()
    cur.execute("SELECT * FROM users")
    return cur.fetchall()
def transfer_old_to_new(connection:MySQLConnection,path_to_db="leerling_emails_db\leerling_emails.db"):
    previous_tables = get_all_tables_sqlite(path_to_db=path_to_db)
    for colums in previous_tables:
        id_,email,subscribed = colums
        query = f'''
        INSERT INTO users ( email, subscribed)
        VALUES ("{email}", {int(subscribed)});
        '''
        send_query(connection=connection,query=query)
def add_new_user(connection:MySQLConnection,email,subscribed = True):
    query = f'''
        INSERT IGNORE INTO users ( email, subscribed)
        VALUES ("{email}", {int(subscribed)})
        
        '''
    
    send_query(connection=connection,query=query)


def create_table(connection:MySQLConnection):
    query=\
'''
CREATE TABLE IF NOT EXISTS users (
    ID INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    subscribed BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (ID)
);
'''


    send_query(connection=connection,query=query)

    
    print("success!")
def check_unsubscribed(session:Session):
    for msg in session.read_unseen_emails(mark_seen=False):
        from_ = str(msg.from_)
        from_ = from_[:from_.rfind("@")]+"@leerling.o2g2.nl"


        text = msg.text.lower()
        subj = msg.subject.lower()
        if "unsubscribe" in text or "unsubscribe" in subj:
            yield from_
def get_all_subscribed_emails(connection:MySQLConnection):
    query = \
    '''
SELECT email
FROM users
WHERE subscribed = 1;
'''

    emails = send_query(connection=connection,
        query=query,
        fetch=True
    )
    return [str(email[0]).strip("\n") for email in emails]
def send_messages_to_users(user_list:list,session:Session,msg:EmailMessage, limit:int=-1):
    for user in user_list:
        if limit>0:
            session.send_email(msg,user)
            limit-=1