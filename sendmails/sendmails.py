#!/usr/bin/env python
#-*- coding: utf-8 -*-

import click
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@click.command()
@click.option('--subject', default='(bez předmětu)')
@click.option('--addresses', required=True)
@click.option('--from', 'from_mail', default='martin.urbanec@wikimedia.cz')
@click.option('--from-name', 'from_name', default='Martin Urbanec')
@click.option('--mail', 'mail_file', required=True)
@click.option('--smtp-server', default='smtp-relay.gmail.com')
def mails(subject, addresses, mail_file, from_mail, from_name, smtp_server):
	mails = open(addresses).readlines()

	orig_mailtext = open(mail_file).read()
	mailtext = []
	for paragraph in orig_mailtext.split('\n\n'):
		mailtext.append("<p>%s</p>" % paragraph)
	mailtext = "\n\n".join(mailtext)

	s = smtplib.SMTP(smtp_server)
	s.ehlo()
	s.starttls()
	for mail in mails:
		mail = mail.replace('\n', '')
		msg = MIMEMultipart('alternative')
		msg['Subject'] = subject
		msg['From'] = '%s <%s>' % (from_name, from_mail)
		msg['To'] = mail

		html = MIMEText(mailtext, 'html')
		msg.attach(html)
		s.sendmail(from_mail, mail, msg.as_string())
	s.quit()

if __name__ == "__main__":
	mails()
