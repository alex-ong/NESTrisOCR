from config import config
import Networking.TCPClient as TCPClient
import Networking.AutoBahnClient as AutoBahnClient
import Networking.FileClient as FileClient

NetClient = TCPClient
if (
    config.get("network.protocol") == "AUTOBAHN"
    or config.get("network.protocol") == "AUTOBAHN_V2"
):
    NetClient = AutoBahnClient
elif config.get("network.protocol") == "FILE":
    NetClient = FileClient
