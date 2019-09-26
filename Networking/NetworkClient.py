from config import config
import Networking.TCPClient as TCPClient
import Networking.AutoBahnClient as AutoBahnClient

NetClient = TCPClient
if config.netProtocol == 'AUTOBAHN':
	NetClient = AutoBahnClient
