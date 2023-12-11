import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

def sendmail(subject,contents,receiver):

    current_path = Path.cwd()/'config/private'
    with open(current_path/"yagmail.csv") as f:
        credentials = f.read().replace("\n", "").split(",")
    usrname = credentials[0]
    pswd = credentials[1]
    to = receiver


    # Create the email message
    message = MIMEMultipart()
    message['From'] = usrname
    message['To'] = to
    message['Subject'] = "mySocialWatcher Notification:"+subject

    message.attach(MIMEText(contents, 'plain'))

    # Connect to the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(usrname, pswd)

    # Send the email
    server.sendmail(usrname, to, message.as_string())

    # Close the server connection
    server.quit()
