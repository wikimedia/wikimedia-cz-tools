# -*- coding: utf-8 -*-
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import json
import requests

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

SCOPES = 'https://www.googleapis.com/auth/admin.directory.user.readonly https://www.googleapis.com/auth/admin.directory.group.member.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Directory API Python Quickstart'

s = requests.Session()
base_url = 'https://wiki.wikimedia.cz'
script_path = '/mw/'
article_path = '/wiki/'
api_url = base_url + script_path + 'api.php'

config = json.loads(open('config.json', 'r').read())

def get_credentials():
	"""Gets valid user credentials from storage.

	If nothing has been stored, or if the stored credentials are invalid,
	the OAuth2 flow is completed to obtain the new credentials.

	Returns:
		Credentials, the obtained credential.
	"""
	credential_dir = 'credentials'
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,
								   'admin-directory_v1-python-quickstart.json')

	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials

def getNoteFromTable(table, mail):
	table = table.replace('\n', '').replace('| ', '|').replace('|}', '')
	rows = table.split('|-')
	rows.pop(0)
	for row in rows:
		row = row.replace('| ', '|').split('|')
		row.pop(0)
		if row[2] == mail:
			return row[-1]
	return ''

def main():
	"""
	Updates list of existing e-mail addresses at all domains at wiki.wikimedia.cz.
	"""
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('admin', 'directory_v1', http=http)

	results = service.users().list(customer='my_customer', orderBy='familyName').execute()
	users = results.get('users', [])

	if not users:
		print('No users in the domain.')
	else:
		r = s.get(api_url, params={
			'action': 'query',
			'meta': 'tokens',
			'type': 'login',
			'format': 'json',
		})
		token = r.json()['query']['tokens']['logintoken']
		r = s.post(api_url, data={
			'action': 'login',
			'format': 'json',
			'lgname': config['username'],
			'lgpassword': config['password'],
			'lgtoken': token
		})
		# Generate list of accounts
		wikicode = u"""=== Schránky ===
{| class="wikitable sortable"
|+
!Jméno
!Příjmení
!Primární e-mail
!Aliasy
!Administrátor?
!Pozastaven?
"""
		for user in users:
			admin = "Ne"
			if user['isAdmin']:
				admin = u"Superadministrátor"
			elif user['isDelegatedAdmin']:
				admin = u"Administrátor"
			suspended = "Ne"
			if user['suspended']:
				suspended = "Ano"
			aliasy = ""
			for email in user['emails']:
				aliasy += email['address'] + '\n'
			data = (u"|-", user['name']['givenName'], user['name']['familyName'], user['primaryEmail'], "", admin, suspended)
			wikicode += '\n|'.join(data) + "\n"
		wikicode += "|}"
		r = s.get(api_url, params={
			'action': 'query',
			'format': 'json',
			'meta': 'tokens',
			'type': 'csrf'
		})
		token = r.json()['query']['tokens']['csrftoken']
		payload = {
			'action': 'edit',
			'format': 'json',
			'title': 'E-mailové adresy/seznam',
			'text': wikicode,
			'summary': 'Robot: Aktualizovan seznam existujicich e-mailovych uctu',
			'token': token,
		}
		r = s.post(api_url, data=payload)
		data = r.json()

if __name__ == '__main__':
	main()
