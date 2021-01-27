import websocket, json, pprint, talib, numpy
from binance.client import Client
from binance.enums import *
import config
import requests
import math

#Telagram Bot
def telegram_bot_sendtext(bot_message):
    bot_token = config.BOT_API
    bot_chatID = config.CHAT_ID #Group
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

#Get Bought value:
def get_last_buy():
    with open('buy_value.txt') as f:
        for value in f:
            pass
        get_last_buy.last_buy_value = float(value) #last value = value crypto was bought at
    f.close()
    print("ZIL LAST BOUGHT VALUE: {}".format(get_last_buy.last_buy_value))


        


def get_last_sell():
    with open('sell_value.txt') as f:
        for value in f:
            pass
        get_last_sell.last_sell_value = float(value) #last value = value crypto was bought at
    f.close()
    print("ZIL LAST SELL VALUE: {}".format(get_last_sell.last_sell_value))



SOCKET = "wss://stream.binance.com:9443/ws/zilusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 45
TRADE_SYMBOL = 'ZILUSDT'


closes = []

in_position = True

client = Client(config.API_KEY, config.API_SECRET)

#Total tradable zill
def get_tradeable_zill():
    tot_zill = client.get_asset_balance(asset='ZIL')
    tradable_zill = tot_zill.get('free')
    get_tradeable_zill.TRADE_QUANTITY = float(tradable_zill)

get_tradeable_zill()
print("TRADEABLE ZILL: " + str(get_tradeable_zill.TRADE_QUANTITY))

#TOTAL Tradable USDT
def get_tradeable_usdt():
    tot_usdt = client.get_asset_balance(asset='USDT')
    tradable_usdt = tot_usdt.get('free')
    get_tradeable_usdt.TRADE_QUANTITY = float(tradable_usdt)

get_tradeable_usdt()
print("TRADEABLE USDT: " + str(get_tradeable_usdt.TRADE_QUANTITY))



def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occurd - {}".format(e))
        return False
    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, in_position
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
        print("USDT-ZILL: " + str(get_tradeable_usdt.TRADE_QUANTITY / float(close)))
        get_last_buy()
        get_last_sell()
        get_tradeable_usdt()
        get_tradeable_zill()
        

        if (float(close) >= (get_last_buy.last_buy_value * 1.02)):
            if in_position:
                print("OVERBOUGHT! Sell! Sell! Sell!")
                #BINANCE SELL LOGIC
                order_succeeded =  order(SIDE_SELL, math.floor(get_tradeable_zill.TRADE_QUANTITY), TRADE_SYMBOL)
                if order_succeeded:
                    in_position = False

                    ##Write sell value to text file
                    with open("sell_value.txt", "a") as f:
                        f.write("\n")
                        f.write(str(close))
                        f.close()

                    #Bot Message to telegram
                    telegram_bot_sendtext("Sold Zil At: " + str(close))
            else:
                print("Is overbought, but we don't own any. Cant sell!")
        
        if (float(close) <= (get_last_sell.last_sell_value * (1 / 1.02))): #0.85
            if in_position:
                print("It is oversold, but already own. Can't Buy!")
            else:
                print('OVERSOLD Buy! Buy! Buy!')
                #BINANCE BUY ORDER LOGIC
                order_succeeded = order(SIDE_BUY, math.floor((get_tradeable_usdt.TRADE_QUANTITY / float(close))), TRADE_SYMBOL)
                if order_succeeded:
                    in_position = True

                    #Write value to text file
                    with open("buy_value.txt", "a") as f:
                        f.write("\n")
                        f.write(str(close))
                        f.close()
                    
                    #Bot Message to telegram
                    telegram_bot_sendtext("Bought Zil At: " + str(close))
                    


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()