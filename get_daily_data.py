#!/usr/bin/python

import os
import sqlite3
import sys
import urllib2

class Datasource:

    def __init__(self, filepath="_daily.db"):

        self.conn = sqlite3.connect(filepath)

        c = self.conn.cursor()
        c.execute("create table if not exists daily_numbers (symbol varchar(6) not null, date datetime, open float, high float, low float, close float, volume integer, adj_close float, constraint daily_idx primary key (symbol, date))")
        c.close()

    def load(self, symbol):
        url = 'http://ichart.finance.yahoo.com/table.csv?s=%s&ignore=.csv' % symbol

        headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19'
        }

        req = urllib2.Request(url, None, headers)
        res = urllib2.urlopen(req)

        # first line is just a header
        data = res.readline()
        data = res.readline()

        c = self.conn.cursor()

        while data:
            vals = [symbol] + data.strip().split(',')

            try:
                c.execute("insert into daily_numbers values (?,?,?,?,?,?,?,?)", vals)

            except sqlite3.IntegrityError:
                vals.append(vals.pop(0))
                vals.append(vals.pop(0))

                c.execute("update daily_numbers set open=?, high=?, low=?, close=?, volume=?, adj_close=? where symbol=? and date=?", vals)

            data = res.readline()

        c.close()

        self.conn.commit()

class Grapher:

    def __init__(self, datasource, symbol):
        self.datasource = datasource
        self.symbol = symbol

    def start(self):
        self.datasource.load(self.symbol)


if __name__ == "__main__":
    ds = Datasource()

    g = Grapher(ds, sys.argv[1].upper())
    g.start()
