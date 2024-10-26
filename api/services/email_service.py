import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

# Email details
def send_email(receiver_name, asset_url, receiver_email):
    sender_email = "logarithmus.team@gmail.com"
    password = current_app.config["SENDER_EMAIL_PASSWORD"]

    # Create the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Scam Detection Report Submitted"

    # Body of the email
    body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #333;">
                    <h2 style="color: #0056b3;">To whom it may concern,</h2>
                    <p>You are receiving this email as a trusted contact for <strong>{receiver_name}</strong>.</p>
                    <p>They have submitted a scam analysis report related to the following asset:</p>
                    <p>
                        <a href="{asset_url}" style="color: #0056b3; text-decoration: none;">Access the report</a>
                    </p>
                    <p>If you believe that something concerning may have occurred, please do not hesitate to reach out to them directly.</p>
                    <br>
                    <p>Thank you for your attention to this important matter.</p>
                    <p>Best regards,<br>The Scamonitor Team</p>
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
    except Exception as e:
        print(f"Error: {e}")
        raise e