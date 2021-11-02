
# darkbitcoingraph
Find Bitcoin addresses with abuse reports that made transaction with a specific Bitcoin address to be used to generate a graph in http://osintcombine.tools/

Output example:
 - Address:<p>
![sample_output_address](https://user-images.githubusercontent.com/3870633/138574311-9cdde52e-1487-4311-be37-1723e3e6e94b.png)

 - Wallet:<p>
![sample_output_wallet](https://user-images.githubusercontent.com/3870633/138574322-ddba24f0-d720-46b5-a16e-132e3e31ea6e.png)

Simple generated graph:

![sample_graph](https://user-images.githubusercontent.com/3870633/138574330-514d80b4-f007-456f-9f6c-ec3c5cd3ff54.png)
  

To use this tool you need to have access to the [BitcoinAbuseDatabase](https://www.bitcoinabuse.com/) API. After that you need to put the token in API_ABUSE_TOKEN variable or create the '.config' file with this format:<p>
  API_ABUSE_TOKEN = _token_<p>
Where _token_ is your token to use the BitcoinAbuse API.
