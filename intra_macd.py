#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import random
import sys
import time
import urllib2
from threading import Thread
from xml.dom.minidom import parseString

import calc
import utl
from utl import COLORS

try:
    from secret import cookie
except ImportError:
    print """Please get a cookie from google and then create a secret.py file like:

    #!/usr/bin/python
    cookie = 'HSID=xxxxxxxxxxxxxxxxx; APISID=xxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxx; SID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx; NID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx; PREF=xxxxxxxxxxxxxxxxxxx:U=xxxxxxxxxxxxxxxx:LD=en:TM=xxxxxxxxxxxxxxxxxxxxxxxx:GM=1:SG=2:S=xxxxxxxxxxxxxxxx'

(or whatever google is expecting the cookie to look like these days...)"""
    sys.exit(1)

class Quote:
    def calc_stats(self, quotes, long_period, short_period, ema_period):
        if self in quotes:
            raise ProgrammingError("Quote cannot be in quotes List")

        if len(quotes) == 0:
            self.long_ema = 0
            self.short_ema = 0
            self.macd = 0
            self.signal = 0

            return

        lquote = quotes[-1]

        prices = [ x.price for x in quotes ]

        self.long_ema = calc.ema(len(prices) - 1, prices, long_period, lquote.long_ema)
        self.short_ema = calc.ema(len(prices) - 1, prices, short_period, lquote.short_ema)

        macds = [ x.get_macd() for x in quotes ]
        self.signal = calc.ema(len(macds) - 1, macds, ema_period, lquote.get_macd())

    def get_macd(self):
        return self.short_ema - self.long_ema

    def get_histogram(self):
        return self.get_macd() - self.signal

    def get_histogram_graph(self, maximum, width):
        if width % 2 != 0:
            raise ValueError("Width must be divisible by two")

        value = self.get_histogram()

        if maximum == 0:
            size = 0
        else:
            size = abs(int((value / maximum) * (width / 2)))

        res = "%s[" % (COLORS['WHITE'])

        if value >= 0:
            res += "·" * (width / 2)
        else:
            res += "·" * (width / 2 - size)
            res += COLORS['RED'] + ("•" * size) + COLORS['WHITE']

        res += "|"

        if value <= 0:
            res += "·" * (width / 2)
        else:
            res += COLORS['GREEN'] + ("•" * size) + COLORS['WHITE']
            res += "·" * (width / 2 - size)

        res += "]%s" % (COLORS['OFF'])

        return res


class Ticker:

    def __init__(self, symbol, short_period=12, long_period=26, ema_period=9):
        self.symbol = symbol
        self.short_period=short_period
        self.long_period=long_period
        self.ema_period=ema_period

        self.quotes = []

        self.flash = False

    def start(self):
        try:
            ticker_t = Thread(target=self.ticker_loop)
            ticker_t.daemon = True
            ticker_t.start()

            time.sleep(1.0)
            self.display_loop()

        except (KeyboardInterrupt, SystemExit):
            pass


    def display_loop(self):
        while True:
            rows, cols = utl.get_console_size()

            num_quotes = rows - 4 - 1 # 1 for last newline - 1 # 1 for last newline
            if num_quotes > len(self.quotes):
                num_quotes = len(self.quotes)

            prev_quote = None

            histogram_width = 26
            max_histogram = 0.0

            for quote in self.quotes[-num_quotes:]:
                if abs(quote.get_histogram()) > max_histogram:
                    max_histogram = abs(quote.get_histogram())

            # output starts here
            utl.clear_screen()
            self.print_header(self.quotes[-1], abs(max_histogram) / histogram_width * histogram_width / 2)

            for quote in self.quotes[-num_quotes:]:
                price_color = ""
                if prev_quote:
                    if prev_quote.price < quote.price:
                        price_color = COLORS['GREEN']
                    elif prev_quote.price > quote.price:
                        price_color = COLORS['RED']

                change_color = ""
                if quote.change > 0:
                    change_color = COLORS['GREEN']
                elif quote.change < 0:
                    change_color = COLORS['RED']

                at = quote.trade_datetime.timetuple()
                timestamp = "%02d:%02d:%02d" % (at[3], at[4], at[5])

                price = "%.3f" % quote.price
                change = "%.3f" % quote.change
                perc_change = "%0.3f" % quote.perc_change
                volume = str(quote.volume)

                graph = quote.get_histogram_graph(maximum=max_histogram, width=histogram_width)

                print "%s  %s%s%s  %s%s  %s%%%s  %s  %s" % (timestamp, price_color, price.rjust(8), COLORS['OFF'], change_color, change.rjust(8), perc_change.rjust(8), COLORS['OFF'], volume.rjust(8), graph)

                prev_quote = quote

            time.sleep(1.0)


    def ticker_loop(self):
        prev_quote = None

        while True:
            quote = self.get_quote()

            if prev_quote and quote.trade_datetime == prev_quote.trade_datetime:
                time.sleep(15.0)
                continue

            quote.calc_stats(self.quotes, self.long_period, self.short_period, self.ema_period)

            self.quotes.append(quote)

            time.sleep(15.0)

            prev_quote = quote

            self.cleanup()


    def get_quote(self):
        url = 'http://www.google.com/ig/api?stock=%s' % self.symbol

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
            'Cookie': 'Cookie:%s' % cookie
        }

        req = urllib2.Request(url, None, headers)
        res = urllib2.urlopen(req)
        res = res.read()

        #print res

        dom = parseString(res)
        xml = dom.getElementsByTagName('finance')[0]

        def get_data(node_name):
            return xml.getElementsByTagName(node_name)[0].attributes['data'].value

        def get_int(node_name):
            return int(get_data(node_name) or 0)

        def get_float(node_name):
            return float(get_data(node_name) or 0)


        quote = Quote()

        # as-is
        quote.symbol = get_data('symbol')
        #quote.pretty_symbol = get_data('pretty_symbol')
        #quote.symbol_lookup_url = get_data('symbol_lookup_url')
        quote.company = get_data('company')
        quote.exchange = get_data('exchange')
        quote.exchange_timezone = get_data('exchange_timezone')
        quote.exchange_utc_offset = get_data('exchange_utc_offset')
        #quote.currency = get_data('currency')
        quote.trade_timestamp = get_data('trade_timestamp')
        #quote.symbol_url = get_data('symbol_url')
        #quote.chart_url = get_data('chart_url')
        #quote.disclaimer_url = get_data('disclaimer_url')
        #quote.ecn_url = get_data('ecn_url')
        #quote.isld_last = get_data('isld_last')
        #quote.isld_trade_date_utc = get_data('isld_trade_date_utc')
        #quote.isld_trade_time_utc = get_data('isld_trade_time_utc')
        #quote.brut_last = get_data('brut_last')
        #quote.brut_trade_date_utc = get_data('brut_trade_date_utc')
        #quote.brut_trade_time_utc = get_data('brut_trade_time_utc')

        # int
        #quote.exchange_closing = get_int('exchange_closing')
        #quote.divisor = get_int('divisor')
        quote.volume = get_int('volume')
        #quote.avg_volume = get_int('avg_volume')
        quote.delay = get_int('delay')
        quote.trade_date_utc = get_int('trade_date_utc')
        quote.trade_time_utc = get_int('trade_time_utc')
        #quote.current_date_utc = get_int('current_date_utc')
        #quote.current_time_utc = get_int('current_time_utc')

        # float
        quote.price = get_float('last')
        #quote.high = get_float('high')
        #quote.low = get_float('low')
        #quote.market_cap = get_float('market_cap')
        #quote.open = get_float('open')
        #quote.y_close = get_float('y_close')
        quote.change = get_float('change')
        quote.perc_change = get_float('perc_change')

        # bool
        #quote.daylight_savings = 'true' == get_data('daylight_savings')

        # datetime (derived)
        quote.trade_datetime = datetime.datetime.strptime(
            "%s%s" % (quote.trade_date_utc, quote.trade_time_utc), "%Y%m%d%H%M%S")

        return quote

    def print_header(self, quote, histogram_scale):
        #print datetime.datetime.now()

        line = "%s%s%s" % (COLORS['WHITE'], "=" * 80, COLORS['OFF'])
        print line

        symbol = "%s%s%s" % (COLORS['YELLOW'], quote.symbol.upper(), COLORS['OFF'])
        company_name = "%s%s%s" % (COLORS['YELLOW'], quote.company, COLORS['OFF'])
        exchange = "%s%s%s" % (COLORS['BLUE'], quote.exchange, COLORS['OFF'])

        padding = 84 - len(quote.symbol) - len(quote.exchange)

        histogram_scale = ("%8f" % histogram_scale).rstrip('0').rstrip('.')

        print "  %s  %s  %s  " % (symbol, company_name.center(padding), exchange)
        print "             PRICE    CHANGE    PERCENT    VOLUME   %s%-9s%s   MACD   %s%8s%s" % (COLORS['CYAN'], "-%s" % histogram_scale, COLORS['OFF'], COLORS['CYAN'], histogram_scale, COLORS['OFF'])
        print line


    def cleanup(self):
        # trim the lists to only keep track of what's needed
        if len(self.quotes) > 1000:
            del self.quotes[:-1000]

if __name__ == "__main__":
    ticker = Ticker(sys.argv[1])
    ticker.start()

