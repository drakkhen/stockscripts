#!/usr/bin/python

def sma(seq, periods):
    x = 0
    period = periods

    while period > 0:
        x += seq[-period]
        period -= 1

    return float(x) / periods


def cumulative_sma(bar, series, prevma):
    """
    Returns the cumulative or unweighted simple moving average.
    Avoids averaging the entire series on each call.
 
    Keyword arguments:
    bar     --  current index or location of the value in the series
    series  --  list or tuple of data to average
    prevma  --  previous average (n - 1) of the series.
    """
 
    if bar <= 0:
        return series[0]
 
    else:
        return prevma + ((series[bar] - prevma) / (bar + 1.0))


def ema(bar, series, period, prevma, smoothing=None):
    '''Returns the Exponential Moving Average of a series.
 
    Keyword arguments:
    bar         -- currrent index or location of the series
    series      -- series of values to be averaged
    period      -- number of values in the series to average
    prevma      -- previous exponential moving average
    smoothing   -- smoothing factor to use in the series.
        valid values: between 0 & 1.
        default: None - which then uses formula = 2.0 / (period + 1.0)
        closer to 1 to gives greater weight to recent values - less smooth
        closer to 0 gives greater weight to older values -- more smooth
    '''
    if period < 1:
        raise ValueError("period must be 1 or greater")
 
    if smoothing:
        if (smoothing < 0) or (smoothing > 1.0):
            raise ValueError("smoothing must be between 0 and 1")
 
    else:
         smoothing = 2.0 / (period + 1.0)
 
    if bar <= 0:
        return series[0]
 
    elif bar < period:
        return cumulative_sma(bar, series, prevma)
 
    return prevma + smoothing * (series[bar] - prevma)
 

