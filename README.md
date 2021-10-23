
# darkbitcoingraph
Find Bitcoin addresses with abuse reports that made transaction with a specific Bitcoin address to be used to generate a graph in http://osintcombine.tools/

Output example:
 - Address:<p>
![sample_output_address](https://user-images.githubusercontent.com/3870633/138574311-9cdde52e-1487-4311-be37-1723e3e6e94b.png)

 - Wallet:<p>
![sample_output_wallet](https://user-images.githubusercontent.com/3870633/138574322-ddba24f0-d720-46b5-a16e-132e3e31ea6e.png)

Simple generated graph:

![sample_graph](https://user-images.githubusercontent.com/3870633/138574330-514d80b4-f007-456f-9f6c-ec3c5cd3ff54.png)
  

To use this tool you need to have access to the [BitcoinAbuseDatabase](https://www.bitcoinabuse.com/) and [WalletExplorer](https://www.walletexplorer.com/) APIs. After that you need to create the '.config' file with this format:<p>
  API_ABUSE_TOKEN = _api1_<p>
  API_WALLET_ADDR_LOOKUP = _api2_<p>
  API_WALLET_WAL_ADDR = _api3_<p>
Where _api1_, _api2_ and _api3_ are the respective values of each API.
