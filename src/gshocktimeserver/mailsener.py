import smtplib
from datetime import date


def send_mail_notification(to_address):
    # Import the email modules we'll need
    from email.mime.text import MIMEText

    msg = MIMEText(f"Time set at {date.today()}")
    me = "gshockSmartSync@avmedia.org"
    you = to_address
    msg['Subject'] = "Casio G-Shock Smart Sync Time Set"
    msg['From'] = me
    msg['To'] = you

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()
