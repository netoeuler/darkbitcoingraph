import sys
import re
import os

if (len(sys.argv) != 2):
	print('Pass the Bitcoin address as parameter.')
	exit(1)

res = re.compile("^[a-zA-Z|0-9]+$")
if res.match(sys.argv[1]):
	address = sys.argv[1]
else:
	print('Please enter a valid Bitcoin address!')
	exit(1)

output_file = open('output/'+address+'_tograph','w')

for addr in sorted(os.listdir('output')):
	if addr == "count":
		continue

	addr_file = open('output/'+addr,'r')
	for f in addr_file.readlines():
		output_file.write(addr+","+f)
	addr_file.close()

output_file.close()