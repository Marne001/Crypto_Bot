import websocket, json, pprint, talib, numpy
from binance.client import Client
from binance.enums import *
import config

SOCKET = "wss://stream.binance.com:9443/ws/zilusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ZILUSDT'
TRADE_QUANTITY = 10

closes = []

in_position = False

client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        return False
    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes
    print('recieved message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print('candle closed at {}'. format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsi's calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the currrent rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("OVERBOUGHT! Sell! Sell! Sell!")
                    #BINANCE SELL LOGIC
                    order_succeeded =  order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("Is overbought, but we don't own any. Cant sell!")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but already own. Can't Buy!")
                else:
                    print('OVERSOLD Buy! Buy! Buy!')
                    #BINANCE BUY ORDER LOGIC
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True
                    


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()