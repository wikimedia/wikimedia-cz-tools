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

SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Update intranet with teamdrive list'

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
	credential_path = os.path.join(credential_dir, 'update_teamdrive_list.json')

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
	service = discovery.build('drive', 'v2', http=http)

	results = service.teamdrives().list(useDomainAdminAccess=True).execute()
	teamDrives = results.get('items', [])

	if not teamDrives:
		print('No TeamDrives in the domain.')
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
		wikitext = u"""== Seznam týmových disků ==
<!-- Tento seznam je pravidelně aktualizován robotem; prosím, needitujte tuto sekci ručně, v opačném případě budou vaše změny při příští aktualizaci přepsány -->
{| class="wikitable"
|-
! Název !! Popis !! Má přístup
		"""
		for teamDrive in teamDrives:
			permissions = service.permissions().list(useDomainAdminAccess=True, supportsTeamDrives=True, fileId=teamDrive['id']).execute().get('items')
			description = config.get('teamDrives', {}).get(teamDrive['id'], {}).get('description', u'Pro přidání popisku kontaktujte Martina Urbance.')
			if permissions:
				permissions_wikitext = u""
				for permission in permissions:
					permission_type = permission.get('role')
					permission_type_human = "unidentified"
					if permission_type == "reader":
						permission_type_human = u"náhled"
						# TODO: Support commenter
					elif permission_type == "writer":
						permission_type_human = u"úpravy"
					elif permission_type == "organizer":
						permission_type_human = u"plný"
					permissions_wikitext += u"* %s <%s> (%s)\n" % (permission.get('name', 'Beze Jména'), permission.get('emailAddress', 'None'), permission_type_human)
				wikitext += "|-\n| %s || %s || \n%s" % (teamDrive['name'], description, permissions_wikitext)
		wikitext += "|}"
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
			'title': 'G Suite/Týmový disk',
			'section': 1,
			'text': wikitext,
			'bot': 'true',
			'summary': 'Robot: Aktualizovan seznam existujicich tymovych disku',
			'token': token,
		}
		r = s.post(api_url, data=payload)


if __name__ == '__main__':
	main()
