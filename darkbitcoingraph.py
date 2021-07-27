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

#RECEIVED/SENT
data = requests.get(url='https://hashxp.org/'+bitcoin_address)

st = data.text.find('<tr><th>Received TX</th><td>')
end = data.text[st+28:].find(' ')
received = int(data.text[st+28:st+28+end])
rel_data = data.text[end:]
st = rel_data.find('<tr><th>Sent TX</th><td>')
end = rel_data[st+24:].find(' ')
sent = int(rel_data[st+24:st+24+end])
print('Received / Sent: ',str(received),'/',str(sent),'\n')

#TOP 5 SENDERS
st = 0
end = 0
st_st = 0
rel_data = data.text[st_st:]
for i in range(5):
	rel_data = rel_data[st_st:]
	st = rel_data.find('tt class="btcaddr">')
	end = rel_data[st:].find('</tt>')
	obj = rel_data[st+19:st+end]
	obj_count = int(rel_data[st+end+9:st+end+9+2])
	if obj_count < 2:
		break
	st_st = st+end+9+2
	arr_top_senders.append(obj+" "+str(obj_count))
	obj_count = 0

data = urllib.request.urlopen('https://blockchain.info/rawaddr/'+bitcoin_address)
obj = json.loads(data.read())
count = 0
addresses_already_requested = []

#ABUSE
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
		arr_abuse.append(obj_abuse['address']+' '+str(obj_abuse['count']))

print('======TOP 5 SENDERS======')
print('\n'.join(arr_top_senders))

print('\n======ABUSE TRANSACTIONS======')
print('\n'.join(arr_abuse))
