import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email details
def send_email():
    sender_email = "logarithmus.team@gmail.com"
    receiver_email = "carlosalbertopaez2002@gmail.com"
    password = "vfmh wzxd mgoz qqvt"

    # Create the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Testing Email"

    # Body of the email
    body = "This is the body of the email."
    message.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
        raise e