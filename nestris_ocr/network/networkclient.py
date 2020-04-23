from nestris_ocr.config import config
import nestris_ocr.network.tcpclient as TCPClient
import nestris_ocr.network.autobahnclient as AutoBahnClient
import nestris_ocr.network.fileclient as FileClient

NetClient = TCPClient
if (
    config["network.protocol"] == "AUTOBAHN"
    or config["network.protocol"] == "AUTOBAHN_V2"
):
    NetClient = AutoBahnClient
elif config["network.protocol"] == "FILE":
    NetClient = FileClient
