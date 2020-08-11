from nestris_ocr.config import config
import nestris_ocr.network.tcp_client as TCPClient
import nestris_ocr.network.autobahn_client as AutoBahnClient
import nestris_ocr.network.autobahn_server as AutoBahnServer
import nestris_ocr.network.file_client as FileClient
import nestris_ocr.network.websocket_server as WebSocketServer

NetClient = TCPClient
if (
    config["network.protocol"] == "AUTOBAHN"
    or config["network.protocol"] == "AUTOBAHN_V2"
):
    NetClient = AutoBahnClient
elif config["network.protocol"] == "AUTOBAHN_SERVER":
    NetClient = AutoBahnServer
elif config["network.protocol"] == "FILE":
    NetClient = FileClient
elif config["network.protocol"] == "WEBSOCKET_SERVER":
    NetClient = WebSocketServer
