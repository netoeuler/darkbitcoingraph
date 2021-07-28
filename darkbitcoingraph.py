import requests
import urllib
import json
import time
import sys
import re

API_TOKEN = ''

if (len(sys.argv) != 2):
	print('Just one argument required: Bitcoin address.')
	exit(1)

res = re.compile("^[a-zA-Z|0-9]+$")
if res.match(sys.argv[1]):
	bitcoin_address = sys.argv[1]
else:
	print('Please enter a valid Bitcoin address!')
	exit(1)

arr_top_senders = []
arr_abuse = []

data = urllib.request.urlopen('https://blockchain.info/rawaddr/'+bitcoin_address)
obj = json.loads(data.read())
count = 0
addresses_already_requested = []

#ABUSE
for tx in obj['txs']:
	type_tx = ['inputs', 'out']

	for list_tytx in type_tx:
		str_type_tx = 'inp' if list_tytx == 'inputs' else 'out'
		for tytx in tx[list_tytx]:	
			if list_tytx == 'inputs':
				tx_in_address = tytx['prev_out']['addr']
			elif list_tytx == 'out':
				tx_in_address = tytx['addr']
			else:
				print('Invalid type transaction')
				exit(1)
	
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
				#arr_abuse.append(obj_abuse['address']+' '+str(obj_abuse['count']))
				print(str_type_tx,')',obj_abuse['address'],str(obj_abuse['count']))
		print(list_tytx,'done')
	break

#print('======TOP 5 SENDERS======')
#print('\n'.join(arr_top_senders))

#print('\n======ABUSE TRANSACTIONS======')
#print('\n'.join(arr_abuse))
