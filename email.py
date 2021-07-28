import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email():
    def __init__(self, username, password, host='smtp.office365.com', port=587):
        self.username = username
        self.password = password
        self.connection = smtplib.SMTP(host, port)
        self.mimemsg = MIMEMultipart()
        self.mimemsg['From'] = username

    def sendMessage(self, to, subject, body, cc=''):
        self.mimemsg['To'] = to
        self.mimemsg['Cc'] = cc
        self.mimemsg['Subject'] = subject
        self.mimemsg.attach(MIMEText(body, 'HTML'))

        self.connection.starttls()
        self.connection.login(self.username, self.password)
        self.connection.send_message(self.mimemsg)
        self.connection.quit()

if __name__ == '__main__':
    from credentials import o365, debug_email
    email = Email(o365['username'], o365['password'])
    email.sendMessage(debug_email, 'This is just a test', 'Hello world!')
