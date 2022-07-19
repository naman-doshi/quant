import smtplib
import ssl

ctx = ssl.create_default_context()
password = "dkcstcaqkulghzxa"    # Your app password goes here
sender = "adelicafunk@gmail.com"    # Your e-mail address
receiver = "naman.doshi@education.nsw.gov.au" # Recipient's address

def email(message):
  with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
      server.login(sender, password)
      server.sendmail(sender, receiver, message)