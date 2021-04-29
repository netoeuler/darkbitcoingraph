import requests
import urllib
import json
import time

API_TOKEN = ''

bitcoin_address = ''

data = urllib.request.urlopen('https://blockchain.info/rawaddr/'+bitcoin_address)
obj = json.loads(data.read())
count = 0
addresses_already_requested = []

for tx in obj['txs']:
	tx_in_address = tx['inputs'][0]['prev_out']['addr']
	
	if tx_in_address in addresses_already_requested:
		continue
	else:
		addresses_already_requested.append(tx_in_address)

	data_abuse = requests.get('https://www.bitcoinabuse.com/api/reports/check?address='+tx_in_address+'&api_token='+API_TOKEN)
	count += 1

	if (count > 1 and count % 30 == 0):
		time.sleep(60)

	try:
		obj_abuse = json.loads(data_abuse.text)
	except:
		print('Error generating JSON from: '+data_abuse.text)

	if (obj_abuse['count'] > 0):
		print(obj_abuse['address']+' '+str(obj_abuse['count']))