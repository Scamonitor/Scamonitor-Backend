import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email details
def send_email(asset_url):
    sender_email = "logarithmus.team@gmail.com"
    receiver_email = "carlosalbertopaez2002@gmail.com"
    password = "vfmh wzxd mgoz qqvt"

    # Create the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Scam Detection Report Submitted"

    # Body of the email
    body = f"""
        <html>
            <body>
                <h2>Hello,</h2>
                <p>You are receiving this email because you are the trusted contact of <strong>USER</strong>.</p>
                <p>They submitted a scam analysis report, with the given asset:</p>
                <p><a href="{asset_url}">Link to file</a></p>
                <br>
                <p>Thank you,<br>Logarithmus Team</p>
            </body>
        </html>
        """
    message.attach(MIMEText(body, "html"))

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