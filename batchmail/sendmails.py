#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText

mails = open('mails.txt').readlines()

subject = open('subject.txt').read().replace('\n', '')
mailtext = open('mail.txt').read()

s = smtplib.SMTP('smtp-relay.gmail.com', 587)
s.ehlo()
s.starttls()
for mail in mails:
	mail = mail.replace('\n', '')
	msg = MIMEText(mailtext)
	msg['Subject'] = subject
	msg['From'] = 'Martin Urbanec <martin.urbanec@wikimedia.cz>'
	msg['To'] = mail
	s.sendmail('martin.urbanec@wikimedia.cz', mail, msg.as_string())
	print(mail)
s.quit()
