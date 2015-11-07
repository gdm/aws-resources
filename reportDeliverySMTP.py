#!/usr/bin/env python2.7
# This script sends mail with report.html/report.txt content and with attached report.yaml file.
import smtplib,sys
from datetime import datetime

from email import Encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase

me = 'email-from'
you = 'email-to'
smtpServer = 'your smtp server'

msg = MIMEMultipart('alternative')

msg['Subject'] = "AWS Usage report " + str(datetime.now())
msg['From'] = me
msg['To'] = you

attachment = "report.yaml"
part = MIMEBase('application', "octet-stream")
part.set_payload(open(attachment, "rb").read())
Encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="' + attachment + '"')

msg.attach(part)

reportHTML = open("report.html", "r")
reportTXT = open("report.txt", "r")

html = """\
<html>
  <head></head>
  <body>
""" + reportHTML.read() + """\
  </body>
</html>
"""
text = reportTXT.read()

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')


msg.attach(part1)
msg.attach(part2)


s = smtplib.SMTP(smtpServer)

s.sendmail(me, [you], msg.as_string())
s.quit()
