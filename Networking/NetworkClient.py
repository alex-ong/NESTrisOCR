from config import config
import Networking.TCPClient as TCPClient
import Networking.AutoBahnClient as AutoBahnClient
import Networking.FileClient as FileClient

NetClient = TCPClient
if (
    config["network.protocol"] == "AUTOBAHN"
    or config["network.protocol"] == "AUTOBAHN_V2"
):
    NetClient = AutoBahnClient
elif config["network.protocol"] == "FILE":
    NetClient = FileClient
