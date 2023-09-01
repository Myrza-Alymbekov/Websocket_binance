import threading
import time
import json

import websocket

from functions import calculate_rsi, calculate_vwap

binance_thread_stop = threading.Event()
bitfinex_thread_stop = threading.Event()


class SocketConnection(websocket.WebSocketApp):
    """
    Базовый класс для установления WebSocket-соединения и обработки сообщений.

    Args:
        url (str): URL для подключения к WebSocket.

    Attributes:
        on_open (func): Callback-функция, вызываемая при успешном открытии соединения.
        on_message (func): Callback-функция, вызываемая при получении сообщения.
        on_error (func): Callback-функция, вызываемая при возникновении ошибки.
        on_close (func): Callback-функция, вызываемая при закрытии соединения.
    """
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open)

        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: print('Error', e)
        self.on_close = lambda ws: print('Closing')

        self.run_forever()

    def on_open(self, ws):
        pass

    def message(self, msg):
        pass


class BinanceConnection(SocketConnection):
    """
    Класс для подключения к Binance WebSocket API и обработки данных.

    Attributes:
        closed_prices (list): Список цен закрытия для вычисления RSI.
    """
    closed_prices = []

    def on_open(self, ws):
        print('Binance websocket was opened')

    def message(self, message):
        data = json.loads(message)
        candle = data['k']
        close_price = float(candle['c'])
        self.closed_prices.append(close_price)
        if candle['x'] and len(self.closed_prices) > 14:
            rsi = round(calculate_rsi(self.closed_prices[-14:]), 2)
            self.closed_prices.clear()
            print(f'Binance - Close Price: {close_price}, RSI: {rsi}')


class BitfinexConnection(SocketConnection):
    """
    Класс для подключения к Bitfinex WebSocket API и обработки данных.

    Attributes:
        closed_candles (list): Список свечей для вычисления VWAP.
    """
    closed_candles = []

    def on_open(self, ws):
        print('Bitfinex websocket was opened')
        return self.send('{ "event": "subscribe",  "channel": "candles",  "key": "trade:1m:tBTCUSD" }')

    def message(self, message):
        data = json.loads(message)
        if isinstance(data, list) and len(data[1]) == 6:
            candle = data[1]
            self.closed_candles.append(candle)
            if len(self.closed_candles) == 10:
                close_price = candle[2]
                vwap = round(calculate_vwap(self.closed_candles), 2)
                self.closed_candles.clear()
                print(f'Bitfinex - Close Price: {close_price}, VWAP: {vwap}')


binance_thread = threading.Thread(
    target=BinanceConnection,
    args=('wss://stream.binance.com:9443/ws/btcusdt@kline_5m',))

bitfinex_thread = threading.Thread(
    target=BitfinexConnection,
    args=('wss://api-pub.bitfinex.com/ws/2/candles:1m:tBTCUSD/trade',))


if __name__ == '__main__':
    binance_thread.start()
    bitfinex_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        binance_thread_stop.set()
        bitfinex_thread_stop.set()
        binance_thread.join()
        bitfinex_thread.join()
