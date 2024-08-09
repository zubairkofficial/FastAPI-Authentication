import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_verification_email(email: str, activation_link: str):
    smtp_server = "smtp.hostinger.com"
    smtp_port = 465  # SSL port
    from_address = "info@cyberifyportfolio.com"
    password = "Cyberify@123#"

    # Create MIME message
    message = MIMEMultipart()
    message["From"] = "\"Authentication\" <info@cyberifyportfolio.com>"
    message["To"] = email
    message["Subject"] = "Verify Your Email Address"

    # Create HTML email body
    html = f"""\
    <html>
      <head></head>
      <body>
        <p>Hi,<br>
        Thank you for registering. Please verify your email by clicking the link below:<br>
        <a href="{activation_link}"><b>Verify Email</b></a><br>
        </p>
      </body>
    </html>
    """
    # Attach HTML part to the message
    message.attach(MIMEText(html, "html"))

    # Send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(from_address, password)
            server.send_message(message)
            print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")



def send_reset_password(email: str, random_password):
    smtp_server = "smtp.hostinger.com"
    smtp_port = 465  # SSL port
    from_address = "info@cyberifyportfolio.com"
    password = "Cyberify@123#"

    # Create MIME message
    message = MIMEMultipart()
    message["From"] = "\"Authentication\" <info@cyberifyportfolio.com>"
    message["To"] = email
    message["Subject"] = "Password Reset Request"

    

    # Create HTML email body
    html = f"""\
    <html>
      <head></head>
      <body>
        <p>Hi,<br>
        We received a request to reset your password. Please use that number to reset your password: <b>{random_password}</b><br>
        If you did not request this, please ignore this email.
        </p>
      </body>
    </html>
    """
    # Attach HTML part to the message
    message.attach(MIMEText(html, "html"))

    # Send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(from_address, password)
            server.send_message(message)
            print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
