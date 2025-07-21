import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    sender = "baha.jamel32@gmail.com"
    receiver = "bahaeddine.jamel@ensi-uma.tn"
    password = "fvsh ztsv fgbp qwtn"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("✅ Email envoyé")
    except Exception as e:
        print("❌ Erreur d'envoi email :", e)

