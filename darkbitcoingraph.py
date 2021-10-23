import requests
import urllib
import json
import time
import sys
import re
import os.path

if (len(sys.argv) != 2):
	print('Just one argument required: Bitcoin or Wallet address.')
	exit(1)

res = re.compile("^[a-zA-Z|0-9]+$")
if res.match(sys.argv[1]):
	if len(sys.argv[1]) == 16:
		wallet_address = sys.argv[1]
	else:
		bitcoin_address = sys.argv[1]
else:
	print('Please enter a valid Bitcoin or Wallet address!')
	exit(1)

API_ABUSE_TOKEN = ''
API_WALLET_ADDR_LOOKUP = ''
API_WALLET_WAL_ADDR = ''

file_apis = open('.config','r')
for f in file_apis.readlines():
	if f.startswith('API_ABUSE_TOKEN'):
		API_ABUSE_TOKEN = f[18:].replace('\n','')
	if f.startswith('API_WALLET_ADDR_LOOKUP'):
		API_WALLET_ADDR_LOOKUP = f[25:].replace('\n','')
	if f.startswith('API_WALLET_WAL_ADDR'):
		API_WALLET_WAL_ADDR = f[23:].replace('\n','')

abuse_types = {'1':'ransomware','2':'darknet market','3':'bitcoin tumbler','4':'blackmail scam','5':'sexortation','99':'other'}

if bitcoin_address:
	try:
		data = urllib.request.urlopen('https://blockchain.info/rawaddr/'+bitcoin_address)	
	except Exception as e:
		print('[Bitcoin address]',e)
		exit(1)
	obj = json.loads(data.read())

	bitcoin_address_wallet = ''
	if API_WALLET_ADDR_LOOKUP:
		API_WALLET_ADDR_LOOKUP = API_WALLET_ADDR_LOOKUP.replace('<bitcoin_address>',bitcoin_address)
		data = urllib.request.urlopen(API_WALLET_ADDR_LOOKUP)
		obj = json.loads(data.read())
		if "label" in obj:
			bitcoin_address_wallet = obj['label']
		else:
			bitcoin_address_wallet = "["+obj['wallet_id']+"]"

	arr_top_senders = {}
	arr_top_receivers = {}
	arr_abuse = []
	arr_abuse_types = {}
	arr_tx_abuse_types = {}
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

	#Abuses of this address
	bitcoin_address_abuse = requests.get('https://www.bitcoinabuse.com/api/reports/check?address='+bitcoin_address+'&api_token='+API_ABUSE_TOKEN)
	obj_btc_addr_abuse = json.loads(bitcoin_address_abuse.text)
	for recent_abuse in obj_btc_addr_abuse['recent']:
		abuse_type = str(recent_abuse['abuse_type_id'])
		if abuse_type in arr_tx_abuse_types.keys():
			arr_abuse_types[abuse_type] += 1
		else:
			arr_abuse_types[abuse_type] = 1
	count_abuse += 1

	file_addr = open('output/'+bitcoin_address,'a')

	for tx in obj['txs']:	
		if count_count > 0:
			count_count -= 1
			continue
		
		file_addr_count = open('output/count/'+bitcoin_address,'w')
		file_addr_count.write(str(count))
		file_addr_count.close()

		type_tx = 'inputs'
		for inp in tx['inputs']:
			if bitcoin_address == inp['prev_out']['addr']:
				type_tx = 'out'
				break

		str_type_tx = '>' if type_tx == 'inputs' else '<'
		if type_tx == 'inputs':
			received += 1
		elif type_tx == 'out':
			sent += 1

		for tytx in tx[type_tx]:	
			if type_tx == 'inputs':	
				tx_in_address = tytx['prev_out']['addr']
			elif type_tx == 'out':
				tx_in_address = tytx['addr']
			else:
				print('Invalid transaction type')
				exit(1)

			if tx_in_address == bitcoin_address:
			  continue
		
			count += 1

			if tx_in_address in addresses_already_requested:
				if type_tx == 'inputs':
					arr_top_senders[tx_in_address] += 1
				else:					
					arr_top_receivers[tx_in_address] += 1
				pos_count = addresses_already_requested.index(tx_in_address)
				count_already_requested[pos_count] += 1
				continue
			else:
				if type_tx == 'inputs':
					arr_top_senders[tx_in_address] = 1
				else:
					arr_top_receivers[tx_in_address] = 1
				addresses_already_requested.append(tx_in_address)
				count_already_requested.append(1)

			data_abuse = requests.get('https://www.bitcoinabuse.com/api/reports/check?address='+tx_in_address+'&api_token='+API_ABUSE_TOKEN)
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
				for recent_abuse in obj_abuse['recent']:
				  abuse_type = str(recent_abuse['abuse_type_id'])
				  if abuse_type in arr_tx_abuse_types.keys():
				    arr_tx_abuse_types[abuse_type] += 1
				  else:
				    arr_tx_abuse_types[abuse_type] = 1
		#end for tx[list_tytx]
		print('|',sep=" ",end='',flush=True)
	#end for obj['txs']
	file_addr.close()

	print('\n\nWallet:',bitcoin_address_wallet) 
	print('Received:',received,'/ Sent:',sent)

	print('\n======TOP 5 SENDERS/RECEIVERS======')
	top5_sen = (sorted(arr_top_senders.items(),key= lambda x:x[1]))[::-1][:5]
	top5_rec = (sorted(arr_top_receivers.items(),key= lambda x:x[1]))[::-1][:5]
	top5_sen_bt_1 = 0 if top5_sen[0][1] > 1 else 1
	top5_rec_bt_1 = 0 if top5_rec[0][1] > 1 else 1
	for i in range(5):
		if top5_sen_bt_1 == 0:
			if top5_sen[i][1] > 1:
				sender = top5_sen[i][0]+' '+str(top5_sen[i][1]) if i < len(top5_sen) else '-'
			else:
				sender = '-'
		else:
			sender = top5_sen[i][0]+' '+str(top5_send[i][1]) if i < len(top5_sen) else '-'

		if top5_rec_bt_1 == 0:
			if top5_rec[i][1] > 1:
				receiver = top5_rec[i][0]+' '+str(top5_rec[i][1]) if i < len(top5_rec) else '-'
			else:
				receiver = '-'
		else:
			receiver = top5_rec[i][0]+' '+str(top5_rec[i][1]) if i < len(top5_rec) else '-'

		if not (sender == '-' and receiver == '-'):
			print('{0:20}  {1}'.format(sender, receiver))

	print('\nAbuse count:',str(obj_btc_addr_abuse['count']))
	print('Abuse period:',str(obj_btc_addr_abuse['first_seen']),'/',str(obj_btc_addr_abuse['last_seen']))

	print('\n======ABUSE TRANSACTIONS======')
	print('\n'.join(arr_abuse))

	print('\n==============ABUSE TYPES=============')
	print('========(ADDRESS/TRANSACTIONS)========')
	for i in ['1','2','3','4','5','99']:
	  abuse_value = arr_abuse_types[i] if i in arr_abuse_types.keys() else '-'
	  abuse_tx_value = arr_tx_abuse_types[i] if i in arr_tx_abuse_types.keys() else '-'
	  print('{0:20}  {1}'.format(abuse_types[i]+' '+str(abuse_value), abuse_types[i]+' '+str(abuse_tx_value)))

elif wallet_address:
	if not API_WALLET_WAL_ADDR:
		print('Please set the API_WALLET_WAL_ADDR value.')
		exti(1)

	API_WALLET_WAL_ADDR = API_WALLET_WAL_ADDR.replace('<wallet_address>',wallet_address)
	data = urllib.request.urlopen(API_WALLET_WAL_ADDR)
	obj = json.loads(data.read())

	if "label" in obj:
		bitcoin_address_wallet = obj['label']
	else:
		bitcoin_address_wallet = "["+obj['wallet_id']+"]"
	print(bitcoin_address_wallet)

	arr_abuse_types = {}
	count_abuse = 0

	for bitcoin_address in obj['addresses']:
		data_abuse = requests.get('https://www.bitcoinabuse.com/api/reports/check?address='+bitcoin_address+'&api_token='+API_ABUSE_TOKEN)
		obj_abuse = json.loads(data_abuse.text)
		count_abuse += 1

		if (count_abuse > 1 and count_abuse % 30 == 0):
		time.sleep(60)

		if obj_abuse['count'] == 0:
			continue
		print(obj_abuse['address']+' '+str(obj_abuse['count']))

		for recent_abuse in obj_abuse['recent']:
			abuse_type = str(recent_abuse['abuse_type_id'])
			if abuse_type in arr_abuse_types.keys():
			    arr_abuse_types[abuse_type] += 1
			else:
			    arr_abuse_types[abuse_type] = 1

	print("")
	for i in ['1','2','3','4','5','99']:
	  abuse_value = arr_abuse_types[i] if i in arr_abuse_types.keys() else '-'
	  print(abuse_types[i],abuse_value)

else:
	print('Something went wrong.')
	exit(1)