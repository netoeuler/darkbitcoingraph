import requests
import urllib
import json
import time
import sys
import re
import os.path

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
arr_relayed_ips = []

data = urllib.request.urlopen('https://blockchain.info/rawaddr/'+bitcoin_address)
obj = json.loads(data.read())

count = 0

if os.path.exists('output/count/'+bitcoin_address):
	file_addr_count = open('output/count/'+bitcoin_address,'r')
	file_addr_line = file_addr_count.readline()
	if len(file_addr_line) > 0:
		try:
			count = int(file_addr_line.replace('\n',''))
			#print('Starting with count',str(count))
		except:
			print('Error with count')
			exit(1)
		finally:
			file_addr_count.close()

count_abuse = 0
count_count = 0
received = 0
sent = 0
addresses_already_requested = []
count_already_requested = []

num_obj = len(obj['txs'])
compl_text_obj = '.'
if count > 0:
	num_obj = num_obj - count
	compl_text_obj = 'still missing.'
	count_count = count

resp = 0
while resp not in ['Y','N']:
	print('There are',num_obj,'transactions',compl_text_obj,'Do you wanna proceed? [y/n]',end=' ')
	resp = input().upper()

if resp == 'N':
	exit(0)

file_addr = open('output/'+bitcoin_address,'a')

for tx in obj['txs']:
	if count_count > 0:
		count_count -= 1
		continue
	
	#type_tx = ['inputs', 'out']
	file_addr_count = open('output/count/'+bitcoin_address,'w')
	file_addr_count.write(str(count))
	file_addr_count.close()

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
		
			count += 1

			if tx_in_address in addresses_already_requested:
				pos_count = addresses_already_requested.index(tx_in_address)
				count_already_requested[pos_count] += 1
				continue
			else:
				addresses_already_requested.append(tx_in_address)
				count_already_requested.append(1)
	
			data_abuse = requests.get('https://www.bitcoinabuse.com/api/reports/check?address='+tx_in_address+'&api_token='+API_TOKEN)
			count_abuse += 1

			if (count_abuse > 1 and count_abuse % 30 == 0):
				time.sleep(60)

			try:
				obj_abuse = json.loads(data_abuse.text)
			except:
				print('Error generating JSON from: '+data_abuse.text)

			if (obj_abuse['count'] > 0):
				arr_abuse.append(str_type_tx+' '+obj_abuse['address']+' '+str(obj_abuse['count']))
				file_addr.write(obj_abuse['address']+'\n')
				#print(str(count),str_type_tx,')',obj_abuse['address'],str(obj_abuse['count']))
		#end for tx[list_tytx]
		print('|',sep=" ",end='',flush=True)
	#end for type_tx
#end for obj['txs']
file_addr.close()

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
