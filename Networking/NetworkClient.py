from config import config
import Networking.TCPClient as TCPClient
import Networking.AutoBahnClient as AutoBahnClient
import Networking.FileClient as FileClient

NetClient = TCPClient
if config.netProtocol == 'AUTOBAHN' or config.netProtocol == 'AUTOBAHN_V2':
	NetClient = AutoBahnClient
elif config.netProtocol == 'FILE':
    NetClient = FileClient