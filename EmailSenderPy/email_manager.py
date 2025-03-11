import dotenv
from .email_creator import *
from .Session import Session

from email.message import EmailMessage
# from MYSQL import *
import pymongo
from .Mongo_db import *
import time

import datetime


def clear_inactive_emails(database_connection: MongoClient, reader_session: Session, mark_seen=True):
    '''
    Removes all emails that are inactive by checking the reply from mailer-daemon@gmx.net and removing the mentioned email
    '''
    for inactive_email in reader_session.find_first_mentioned_email_in_emails("mailer-daemon@gmx.net", mark_seen=mark_seen):
        # delete_document_by_email(connection=database_connection,email=inactive_email)
        add_property_to_documents(database_connection, "exists", False, filter_query={
                                  "email": inactive_email})


def send_emails_to_users(mongo_client: pymongo.MongoClient, email_session_reader: Session, email_session: Session, msg_location: str, email_type: str, subject: str, message_location_html: str = "", limit=955, start_from=0, timeout_between_emails_seconds=60, update_IMAP=True, replace_text=True, base_url=""):
    '''
    Sends the messages to users from the database

    mongo_client: connection to the mongodatabase

    email_session_reader: an object of type Session.Session that has mode="r" enabled and is correctly configured (will be used to read emails)

    email_session: an object of type Session.Session that has "w" enabled and is correctly configured (can be the same as email_session_reader)

    limit: sets a limit on how many emails should be sent

    start_from:speciefies after how many iterations you can start sending emails

    limit:speciefies how many emails should be sent

    msg_location: path to the email that you want to send

    subject: the subject of the email

    message_location_html: path to the email written using html (optional)

    timeout_between_emails_seconds: delay between each sent email

    update_IMAP: updates the "sent IMAP" inbox to include the sent e-mail for the email_session_reader
    '''
    try:

        emails_to_send_to = get_subscribed_emails(mongo_client)[start_from:]

        limit -= start_from
        for idx, reciever in enumerate(emails_to_send_to):
            if idx < limit:

                print(f"reciever number: {idx}")

                send_email_to_user(email_session=email_session,
                                   email=reciever,
                                   msg_location=msg_location,
                                   message_location_html=message_location_html,
                                   email_type=email_type,
                                   database_connection=mongo_client,
                                   replace_text=replace_text,
                                   base_url=base_url,
                                   subject=subject,
                                   update_IMAP=update_IMAP,
                                   email_session_reader=email_session_reader)

                print(f"email sent to: {reciever}")
                time.sleep(timeout_between_emails_seconds)
    except KeyboardInterrupt:
        print("Stopping...")
        return


def send_email_to_user(email_session: Session, email: str, msg_location: str, subject: str, message_location_html="", email_type=None, database_connection=None, update_IMAP=True, email_session_reader: Session = None, base_url="", replace_text=True) -> None:
    '''
    Sends an email to user based on provided parameters

    if email_type and database_connection are set it will also update the date_of_email parameter in the database
    for that user
    '''
    try:
        msg_text_content = view_html(msg_location)
        msg_html_content = view_html(message_location_html)
    except FileNotFoundError:
        print("One of the provided file locations does not exist")
        return
    msg = email_constructor(email,
                            email_session.sender_email,
                            subject,
                            msg_text_content,
                            msg_html_content)

    if replace_text:
        replacement_mapping = {r"{{email}}": email,
                               r"{{sender}}": email_session.sender_email,
                               r"{{email_type}}": str(email_type),
                               r"{{site}}": f"{base_url}/{email_type}/{encrypt_value(email)}",
                               r"{{subject}}": subject,
                               r"{{time}}": str(datetime.datetime.now())}
        for text_to_replace in replacement_mapping:
            replace_text_of_the_message(
                msg, text_to_replace, replacement_mapping[text_to_replace])

    if email_session is None:
        print("No database session sender was provided. Check configuration")
        return

    # Updating the database if needed based on email_type and database connection parameters
    if email_type and database_connection:
        # validating the email type

        redirect_type_doc = get_documents_by_query(database_connection, {
                                                   "allowed_type": email_type}, collection_name="redirect_types")
        if not redirect_type_doc:
            print("This Email type is not allowed")
            return
        else:
            try:
                date_of_visit_value = get_email_properties(
                    database_connection, email, auto_decrypt=False)["date_of_email"]
            except KeyError:

                date_of_visit_value = "None"

            if date_of_visit_value == "None":
                new_date_of_visit_value = {email_type: datetime.datetime.fromtimestamp(
                    time.time()).strftime('%Y-%m-%d %H:%M:%S')}
            elif email_type in date_of_visit_value:
                new_date_of_visit_value = date_of_visit_value
            else:
                new_date_of_visit_value = date_of_visit_value
                new_date_of_visit_value[email_type] = datetime.datetime.fromtimestamp(
                    time.time()).strftime('%Y-%m-%d %H:%M:%S')
            email_id = get_id_of_an_email(
                database_connection, encrypt_value(email), auto_decrypt=False)
            print(email_id)

            add_property_to_documents(database_connection, "date_of_email",
                                      new_date_of_visit_value, filter_query={"_id": email_id})

    print(f"Sending an email to {email}")
    try:
        email_session.send_email(msg, email)
        if email_session_reader and update_IMAP:
            email_session_reader.update_IMAP(msg, email)
    except KeyboardInterrupt:
        print("Stopping...")
    except Exception as e:
        print("Something went wrong when sending an e-email check the configuration")
        print(e)
