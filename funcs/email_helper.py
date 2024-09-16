import os
import uuid
import smtplib, ssl
import mysql.connector
from mysql.connector import Error
from email.mime.text import MIMEText
from funcs.sql_helper import sql_connect, sql_close, sql_get, sql_insert, sql_update
from flask import flash


# Create Email
def email_create(confirm_url):
    # Create HTML of Message
    html = f"""\
    <html>
    <head>
        <link rel="stylesheet" href="/static/css/base.css">
    </head>
    <body>
        <div style="background-color: #387d41;">
            <h1 style="text-align: center; color: #ffffff; padding: 30px;">OSAthletics Account Verification</h1> 
        </div>
        <div style="margin: 5% 30%; width: 40%; background-color: #EEEEEE; padding: 20px;">
            <h3 style="text-align: center; color: #387d41;">Click the button below to verify your OSAthletics Account</h3> 
            <div style="display: flex; flex-wrap: wrap; align-content: center; align-items: center; width: 100%;">
                <a href="{confirm_url}" style="margin: 0 auto; border: 1px solid rgb(218,220,224); background-color: rgb(255, 255, 255); padding: 10px; border-radius: 10px; text-decoration: none; color: #387d41;">Verify Account</a>
            </div>
            <i><p style="text-align: center; color: #387d41;">This verification email is only valid for 10 minutes.</p> </i>
            <hr>
            <p style="text-align: center; color: #387d41; font-size: small;">If this email does not belong to you, please disregard this email.</p> 

        </div>
    </body>
    </html>
    """

    # Turn HTML Message into MIMEText objects
    return MIMEText(html, "html")

# Send Email
def email_send(mail, message, sender_email, password, receiver_email):
    # Attach Message
    message.attach(mail)

    context = ssl.create_default_context()
    
    # Connect to SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    
# Verify Email
def email_verify(email):
    try:
        connection = sql_connect(os.environ.get('SQL_SERVER'))
        cursor = connection.cursor()

        test_case = ""
        conf = email

        # Check if there are multiple emails
        if isinstance(email, list):
            test_case = (email[0].strip(),)
            conf = email[0]

        else:
            test_case = (email.strip(),)

        # Get account Information
        account = sql_get("*", "accounts", "email = %s", test_case, cursor)

        # Check if account has already been verified
        if account[0][4] == 1:
            flash('error Account already confirmed. Please login.', 'success')
        else:
            # Verify Account
            test_case = (True, conf)
            sql_update(connection, "accounts", "confirmed = %s", "email = %s", test_case, cursor)
            # Create Account Profile
            if account[0][3] == "student":
                test_case = (uuid.uuid4().hex, account[0][0])
                sql_insert(connection, "students", "(studentId, accountId)", "(%s, %s)", test_case, cursor)

            elif account[0][3] == "coach":
                test_case = (uuid.uuid4().hex, account[0][0])
                sql_insert(connection, "coaches", "(coachId, accountId)", "(%s, %s)", test_case, cursor)
            elif account[0][3] == "parent":
                parentId = uuid.uuid4().hex
                test_case = (email[1].strip(),)
                studentId = sql_get("studentId", "students", "accountId = %s", (sql_get("accountId", "accounts", "email = %s", test_case, cursor)[0][0],), cursor)
                test_case = (parentId, account[0][0], studentId[0][0])
                sql_insert(connection, "parents", "(parentId, accountId, studentId)", "(%s, %s, %s)", test_case, cursor)

                sql_update(connection, "students", "parentId = %s", "studentId = %s", (parentId, studentId[0][0]), cursor)

            flash('success Your account has been successfully confirmed. Thanks!')
    except mysql.connector.Error as error:
            flash('error An error occured while trying to verify your account. Please try again.')
    finally:
        sql_close(connection, cursor)