# -*- coding: utf-8 -*-
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import json
import pymysql

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

SCOPES = 'https://www.googleapis.com/auth/admin.directory.group.member'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Update tracker users Google group'

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
	credential_path = os.path.join(credential_dir, 'update_tracker_users.json')

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

def connect():
	return pymysql.connect(
		database=config['database']["DB_NAME"],
		host=config['database']['DB_HOST'],
		user=config['database']['DB_USER'],
		password=config['database']['DB_PASS']
	)

def main():
	"""
	Updates list of existing e-mail addresses at all domains at wiki.wikimedia.cz.
	"""
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('admin', 'directory_v1', http=http)

	tracker_mails = []
	conn = connect()
	with conn.cursor() as cur:
		cur.execute('select email from auth_user where email!="";')
		data = cur.fetchall()
	for row in data: tracker_mails.append(row[0])

	members = service.members().list(groupKey=config["groupId"]).execute().get('members', [])

	for member in members:
		if member['email'] not in tracker_mails and member['role'] not in ("OWNER", "MANAGER"):
			print("Removing %s" % member['email'])
			service.members().delete(groupKey=config["groupId"], memberKey=member["id"]).execute()
		elif member['email'] in tracker_mails:
			tracker_mails.remove(member["email"])
	for mail in tracker_mails:
		print("Adding %s" % mail)
		service.members().insert(groupKey=config["groupId"], body={"email": mail}).execute()


if __name__ == '__main__':
	main()
