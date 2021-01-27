import websocket, json, pprint

SOCKET = "wss://stream.binance.com:9443/ws/zilusdt@kline_1d"

def on_open(ws):
    print("open")
    
def on_close(ws):
    print("close")

def on_message(ws, message):
    print("message")
    print(message)
    json_message = json.loads(message)
    pprint.pprint(json_message)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()