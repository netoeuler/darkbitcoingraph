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
received = 0
sent = 0
addresses_already_requested = []
count_already_requested = []
arr_relayed_ips = []

#ABUSE
for tx in obj['txs']:
	#type_tx = ['inputs', 'out']

	if tx['relayed_by'] not in arr_relayed_ips:
		arr_relayed_ips.append(tx['relayed_by'])

	type_tx = 'inputs'
	for inp in tx['inputs']:
		if bitcoin_address == inp['prev_out']['addr']:
			type_tx = 'out'
			break

	for list_tytx in [type_tx]:
		str_type_tx = '>' if list_tytx == 'inputs' else '<'
		if list_tytx == 'inputs':
			received += 1
		elif list_tytx == 'out':
			sent += 1

		for tytx in tx[list_tytx]:	
			if list_tytx == 'inputs':	
				tx_in_address = tytx['prev_out']['addr']
			elif list_tytx == 'out':
				tx_in_address = tytx['addr']
			else:
				print('Invalid transaction type')
				exit(1)
		
			if tx_in_address in addresses_already_requested:
				pos_count = addresses_already_requested.index(tx_in_address)
				count_already_requested[pos_count] += 1
				continue
			else:
				addresses_already_requested.append(tx_in_address)
				count_already_requested.append(1)
	
			data_abuse = requests.get('https://www.bitcoinabuse.com/api/reports/check?address='+tx_in_address+'&api_token='+API_TOKEN)
			count += 1

			if (count > 1 and count % 30 == 0):
				time.sleep(60)

			try:
				obj_abuse = json.loads(data_abuse.text)
			except:
				print('Error generating JSON from: '+data_abuse.text)

			if (obj_abuse['count'] > 0):
				arr_abuse.append(str_type_tx+' '+obj_abuse['address']+' '+str(obj_abuse['count']))
				#print(str_type_tx,')',obj_abuse['address'],str(obj_abuse['count']))
		#end for tx[list_tytx]
		print('|',sep=" ",end='',flush=True)
	#end for type_tx
#end for obj['txs']

print('\n\nReceived:',received,'/ Sent:',sent)
#print('Relayed IPs:',' '.join(arr_relayed_ips))

sorted_count = (sorted(count_already_requested)[::-1])[0:5]
count = 0
count_top_senders = 0

print('\n======TOP 5 SENDERS======')
for i in addresses_already_requested:
	cc = count_already_requested[count]
	count += 1
	if cc > 1 and cc in sorted_count:
		print(i,str(cc))
		count_top_senders += 1
	if count_top_senders == 5:
		break

print('\n======ABUSE TRANSACTIONS======')
print('\n'.join(arr_abuse))
