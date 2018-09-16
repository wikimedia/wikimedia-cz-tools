#!/usr/bin/env python
#-*- coding: utf-8 -*-

from apiclient import discovery
from google.oauth2 import service_account
import requests
import json

config = json.loads(open('config.json', 'r').read())

s = requests.Session()
base_url = 'https://wiki.wikimedia.cz'
script_path = '/mw/'
article_path = '/wiki/'
api_url = base_url + script_path + 'api.php'

# Login to wiki
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

SERVICE_ACCOUNT_FILE = '../service_account.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.settings.basic', 'https://www.googleapis.com/auth/gmail.settings.sharing']
APPLICATION_NAME = 'Send Mail As (martin.urbanec@wikimedia.cz)'

IGNORE_GROUPS = []
ONLY_GROUPS = ['test-group@wikimedia.cz', 'hackathon@wikimedia.cz'] # Set to none if you want to go through all group

service_credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

def get_file(f):
	r = s.get(api_url, params={
		"action": "query",
		"format": "json",
		"prop": "revisions",
		"titles": "E-mailové adresy/%s" % f,
		"rvprop": "content"
	})
	return json.loads(r.json()['query']['pages'][r.json()['query']['pages'].keys()[0]]['revisions'][0]['*'])

def group_by_email(groups, email):
	for group in groups:
		if group['email'] == email:
			return group
	return None

def user_by_email(users, email):
	for user in users:
		if user['primaryEmail'] == email:
			return user
	return None

def main():
	proceed = []
	all_groups = get_file('groups.json')
	all_members = get_file('members.json')
	if ONLY_GROUPS:
		for group in ONLY_GROUPS:
			group = group_by_email(all_groups, group)
			members = all_members.get(group['id'])
			if not members: continue
			proceed.append({
				'emails': [m['email'] for m in members['members']],
				'id': group['id'],
				'email': group['email'],
				'name': group['name'],
			})
	else:
		for group in all_groups:
			if group['email'] not in IGNORE_GROUPS:
				members = all_members.get(group['id'])
				if not members: continue
				proceed.append({
					'emails': [m['email'] for m in members['members']],
					'id': group['id'],
					'email': group['email']
				})

	for group in proceed:
		print('Processing %s' % group['email'])
		for user in group['emails']:
			if not user.endswith('wikimedia.cz'): continue
			credentials = service_credentials.with_subject(user)
			service = discovery.build('gmail', 'v1', credentials=credentials)

			sendAs = service.users().settings().sendAs().list(userId='me').execute()['sendAs']
			current_send_ases = []
			for i in sendAs:
				current_send_ases.append(i['sendAsEmail'])
			if group['email'] not in current_send_ases:
				print('Adding %s to %s' % (group['email'], user))
				service.users().settings().sendAs().create(userId='me', body={
					"sendAsEmail": group['email'],
					"treatAsAlias": True,
					"displayName": group['name'],
				}).execute()

if __name__ == '__main__':
	main()
