#!/usr/bin/env python
#-*- coding: utf-8 -*-

import click
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@click.command()
@click.option('--subject', default='(bez předmětu)')
@click.option('--data', required=True)
@click.option('--from', 'from_mail', default='martin.urbanec@wikimedia.cz')
@click.option('--from-name', 'from_name', default='Martin Urbanec')
@click.option('--mail', 'mail_file', required=True)
@click.option('--smtp-server', default='smtp-relay.gmail.com')
def mails(subject, data, mail_file, from_mail, from_name, smtp_server):
	data = open(data).readlines()
	if len(data[0].split('\t')) > 1:
		header = data.pop(0).replace('\n', '').split('\t')
	else:
		header = None

	orig_mailtext = open(mail_file).read()
	mailtext = []
	for paragraph in orig_mailtext.split('\n\n'):
		mailtext.append("<p>%s</p>" % paragraph)
	mailtext = "\n\n".join(mailtext)

	s = smtplib.SMTP(smtp_server)
	s.ehlo()
	s.starttls()
	data2 = {}
	for line in data:
		row = line.replace('\n', '').split('\t')
		data2[row[header.index('mail')]] = {}
		for var in header:
			if var == 'mail':
				continue
			data2[row[header.index('mail')]][var] = row[header.index(var)]
	data = data2

	for mail in data:
		msg = MIMEMultipart('alternative')
		msg['Subject'] = subject
		msg['From'] = '%s <%s>' % (from_name, from_mail)
		msg['To'] = mail

		text = mailtext
		for var in data[mail]:
			text = text.replace('@@%s@@' % var, data[mail][var])
		html = MIMEText(text, 'html')
		msg.attach(html)
		s.sendmail(from_mail, mail, msg.as_string())
	s.quit()

if __name__ == "__main__":
	mails()
