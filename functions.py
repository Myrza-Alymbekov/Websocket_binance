import numpy as np


def calculate_rsi(data, period=14):
    """
    Рассчитывает индекс относительной силы (RSI) на основе данных о ценах закрытия.

    Args:
        data (list): Список цен закрытия.
        period (int, optional): Период для вычисления RSI. По умолчанию 14.
    Returns:
        float: Значение RSI.
    """
    close_prices = np.array(data)
    delta = np.diff(close_prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])
    rs = avg_gain / (avg_loss + 1e-5)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_vwap(data):
    """
    Рассчитывает средневзвешенную цену по объему (VWAP) на основе данных свечей.

    Args:
        data (list): Список свечей, каждая из которых представлена списком данных.
    Returns:
        float: Значение VWAP.
    """
    total_volume = 0
    sum_price_volume = 0
    for candle in data:
        volume = float(candle[5])
        close_price = float(candle[2])
        total_volume += volume
        sum_price_volume += close_price * volume
    return sum_price_volume / total_volume
