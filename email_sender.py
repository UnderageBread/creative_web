import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
import os


class EmailSender:

    def __init__(self, sender_email, password):
        self.sender_email = sender_email
        self.password = password
        self.smtp_server = "smtp.163.com"
        self.smtp_port = 465

    def send_email(self, receiver_email, subject, content, attachments=None):
        try:
            message = MIMEMultipart()
            message['From'] = Header(self.sender_email, 'utf-8')

            if isinstance(receiver_email, list):
                message['To'] = Header(','.join(receiver_email), 'utf-8')
            else:
                message['To'] = Header(receiver_email, 'utf-8')
                receiver_email = [receiver_email]

            message['Subject'] = Header(subject, 'utf-8')
            message.attach(MIMEText(content, 'plain', 'utf-8'))

            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            attachment = MIMEApplication(f.read())
                            attachment.add_header(
                                'Content-Disposition',
                                'attachment',
                                filename=('utf-8', '', os.path.basename(file_path))
                            )
                            message.attach(attachment)

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, receiver_email, message.as_string())

            return True

        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False


def send_result_email(exp_code, excel_path):
    sender = EmailSender("ylrunning@163.com", "YGg7kCuRJBYmCVZT")
    subject = f"问卷结果 - 实验码 {exp_code}"
    content = "见附件"
    return sender.send_email(
        "2443874694@qq.com",
        subject,
        content,
        [excel_path]
    )
