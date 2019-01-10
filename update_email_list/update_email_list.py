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

SCOPES = 'https://www.googleapis.com/auth/admin.directory.user.readonly https://www.googleapis.com/auth/admin.directory.group.readonly https://www.googleapis.com/auth/admin.directory.rolemanagement.readonly'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Update intranet with email list'

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
	credential_dir = '../credentials'
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir, 'update_email_list.json')

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

def main():
	"""
	Updates list of existing e-mail addresses at all domains at wiki.wikimedia.cz.
	"""
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('admin', 'directory_v1', http=http)

	results = service.users().list(customer='my_customer', orderBy='givenName', projection="full").execute()
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
		# Fetch data from wiki
		r = s.get(api_url, params={
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"titles": "E-mailové adresy/extra.json",
			"rvprop": "content"
		})
		data = r.json()["query"]["pages"]
		data = json.loads(data[list(data.keys())[0]]["revisions"][0]['*'])
		extra_users = data["users"]
		extra_groups = data["groups"]
		overrides = data["overrides"]
		# Fetch all existing roles and roles assignments
		results = service.roles().list(customer='my_customer').execute()
		roles = results.get('items', [])
		rolesHuman = {}
		for role in roles:
			role_name = role['roleName']
			if role_name == "_SEED_ADMIN_ROLE":
				role_name = u"Google Apps Administrator Seed Role"
			elif role_name == "_GROUPS_ADMIN_ROLE":
				role_name = u"Administrátor skupin"
			elif role_name == u"_USER_MANAGEMENT_ADMIN_ROLE":
				role_name = u"Administrátor uživatelů"
			elif role_name == "_HELP_DESK_ADMIN_ROLE":
				role_name = u"Administrátor technické podpory"
			elif role_name == "_SERVICE_ADMIN_ROLE":
				role_name = u"Administrátor služeb"
			elif role_name == "_PLAY_FOR_WORK_ADMIN_ROLE":
				role_name = u"Administrátor služby Play for Work"
			rolesHuman[role['roleId']] = role_name
		results = service.roleAssignments().list(customer='my_customer').execute()
		rolesAssignments = results.get('items', [])
		# Translate it into rozumejsi format
		tmp = {}
		for roleAssignment in rolesAssignments:
			if roleAssignment['assignedTo'] not in tmp:
				tmp[roleAssignment['assignedTo']] = []
			tmp[roleAssignment['assignedTo']].append(rolesHuman[roleAssignment['roleId']])
		roles = tmp
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
!Organizační jednotka
!Poznámka
"""
		for user in users:
			admin = "Ne"
			if user['isAdmin']:
				admin = u"\n* Superadministrátor\n"
			elif user['isDelegatedAdmin']:
				admin = u"\n"
				for role in roles[user['id']]:
					admin += u"* " + role + u'\n'
			suspended = "Ne"
			if user['suspended']:
				suspended = "Ano"
			aliasy = "\n"
			for email in user['emails']:
				if 'primary' not in email and 'type' not in email:
					aliasy += '* ' + email['address'] + '\n'
			try:
				note = user['customSchemas']['Ostatn']['Poznmka']
			except:
				note = ""
			data = (u"|-", user['name']['givenName'], user['name']['familyName'], user['primaryEmail'], aliasy, admin, suspended, user['orgUnitPath'], note)
			wikicode += '\n|'.join(data) + "\n"
		for extra_user in extra_users:
			aliases = "\n"
			for alias in extra_user['aliases']:
				aliases += "* " + alias + "\n"
			wikicode += '\n|'.join((extra_user["givenName"], extra_user["familyName"], extra_user["email"], aliases, "Ne", "Ne", "/Extra", extra_user["note"])) + "\n"
		wikicode += u"|}\n\n=== Distribuční seznamy ===\n"
		wikicode += u"""{| class="wikitable sortable"
|+
!Jméno
!E-mailová adresa
!Aliasy
!Členové
"""
		groups = service.groups().list(customer="my_customer").execute()['groups']
		all_members = {}
		for group in groups:
			if group['name'].startswith('[secret] '):
				continue
			id = group['id']
			email = group['email']
			if email == u"ucitele_ucebna@wikimedia.cz":
				continue
			members = "\n"
			aliases = "\n"
			if 'aliases' in group:
				for alias in group['aliases']:
					aliases += "* " + alias + "\n"
			if overrides.get(email, {}).get('members') is not None:
				members += overrides.get(email, {}).get('members')
			else:
				membersIterate = service.members().list(groupKey=id).execute()
				all_members[group['id']] = membersIterate
				if 'members' in membersIterate:
					membersIterate = membersIterate['members']
					for member in membersIterate:
						role = member['role']
						if role == "MEMBER":
							role = u"člen"
						elif role == "OWNER":
							role = u"vlastník"
						elif role == "MANAGER":
							role = u"správce"
						if 'email' in member:
							members += "* " + member['email'] + " (" + role + ")\n"
			wikicode += "\n|".join(('|-', group['name'], email, aliases, members)) + "\n"
		for extra_group in extra_groups:
			aliases = "\n"
			for alias in extra_group['aliases']:
				aliases += "* " + alias + "\n"
			wikicode += "\n|".join(('|-', extra_group['name'], extra_group['email'], aliases, extra_group['members'])) + "\n"
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
			'bot': 'true',
			'minor': 'true',
			'summary': 'Robot: Aktualizovan seznam existujicich e-mailovych uctu',
			'token': token,
		}
		r = s.post(api_url, data=payload)
		payload = {
			"action": "purge",
			"format": "json",
			"titles": "E-mailové adresy"
		}
		r = s.post(api_url, data=payload)

if __name__ == '__main__':
	main()
