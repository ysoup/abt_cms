# -*- coding: utf-8 -*-
import requests
import json
import time
from datetime import datetime
import numpy as np
from dateutil.parser import parse
from pandas.compat import StringIO
# from flask import current_app
import pandas as pd


# 周期
PERIOD_1MIN = '1min'      # 1分钟
PERIOD_3MIN = '3min'      # 3分钟
PERIOD_5MIN = '5min'      # 5分钟
PERIOD_15MIN = '15min'    # 15分钟
PERIOD_30MIN = '30min'    # 30分钟
PERIOD_1HOUR = '1hour'    # 1小时
PERIOD_2HOUR = '2hour'    # 2小时
PERIOD_4HOUR = '4hour'    # 4小时
PERIOD_6HOUR = '6hour'    # 6小时
PERIOD_12HOUR = '12hour'  # 12小时
PERIOD_1DAY = '1day'      # 1日
PERIOD_3DAY = '3day'      # 3日
PERIOD_1WEEK = '1week'    # 1周
PERIOD_1MONTH = '1month'  # 1月
PERIOD_1YEAR = '1year'    # 1年
PERIOD_10YEAR = '10year'

PERIOD_INTERVAL_MAP = {
    PERIOD_1MIN: 1,
    PERIOD_3MIN: 3,
    PERIOD_5MIN: 5,
    PERIOD_15MIN: 15,
    PERIOD_30MIN: 30,
    PERIOD_1HOUR: 60,
    PERIOD_2HOUR: 120,
    PERIOD_4HOUR: 240,
    PERIOD_6HOUR: 360,
    PERIOD_12HOUR: 720,
    PERIOD_1DAY: 1440,
    PERIOD_3DAY: 4320,
    PERIOD_1WEEK: 10080,
    PERIOD_1MONTH: 43200,
    PERIOD_1YEAR: 518400
}


def get_kline_data_from_aicoin(exchange, symbol, period):
    # url = 'https://www.aicoin.net.cn/chart/api/data/period?symbol=bitfinexethusd&step=14400'
    # url = 'https://www.aicoin.net.cn/chart/api/data/period?symbol=bitfinexbtcusd&step=86400'
    url = 'https://www.aicoin.net.cn/chart/api/data/period?symbol={exchange}{symbol}&step={step}'.format(
        exchange=exchange.lower(), symbol=symbol.replace("_", "").lower(), step=PERIOD_INTERVAL_MAP[period]*60)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.100 Safari/537.36',
        'Host': 'www.aicoin.net.cn',
        'Cookie': 'step=86400; '
                  'acw_tc=7819730615376716393148290ed1478f70cb944ecf173e69e37c5c25b21eb5; '
                  'Hm_lvt_3c606e4c5bc6e9ff490f59ae4106beb4=1537671642; '
                  'Hm_lpvt_3c606e4c5bc6e9ff490f59ae4106beb4=1537671642; '
                  '_ga=GA1.3.1591811312.1537671643; _gid=GA1.3.970230023.1537671643; '
                  'XSRF-TOKEN=eyJpdiI6ImJwWXpiZWhwMVJERGVkYnpIb0RvS3c9PSIsInZhbHVlIjoiNytPYnJcL1hWSlBTNVhKQlVFRW9'
                  'ja0p4UXRxYmgrd3ZaSk02aHRpbFRkZlpGVnZIUW5LYjVRVG81S293OVIwcU5NYzR4b25kMnpSd3lwUGZOXC9vK1NsZz09I'
                  'iwibWFjIjoiNzg4MzI4M2VlNzc4ODdiNTBjNmM4ODc1NTY1MTZkNmI3YzZkNTk2MTY2YzQxYzk3YzBiMmMxNDkxZmQwZDQ'
                  '2ZiJ9; aicoin_session=eyJpdiI6IkE2ckNNRVwvQXhEN0gxczNzUlpVdlZBPT0iLCJ2YWx1ZSI6ImpIWjgreFBvUGpp'
                  'MXRqUldqMEc2eUx4a3Q3TG5icDVuV0xSVlBacm1VZk85em1ncHZVdTNJRFRMN29cL1poY21CdFV3VFN5YmRRWDBUNzh4Sm'
                  'hCNjNFZz09IiwibWFjIjoiMWRlODBkZTUwYzhhZTFmYWJhYmRjYWE5YjAwYzQ2NTI3YTI4YTgzM2JiYTIzM2M1NjI1NWFk'
                  'NWQ2ZDg1ODJlZCJ9',
        'Referer': 'https://www.aicoin.net.cn/chart/D331D4E2',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,fy;q=0.6,ru;q=0.5',
        'Connection': 'keep-alive'
    }
    print("Request: %s" % url)
    rsp_data = requests.get(url, headers=headers)
    rsp_json = json.loads(rsp_data.content)
    kline_list = rsp_json['data']
    return kline_list


def get_kline_data_from_aibilink(exchange, symbol, period):
    # url = 'https://www.aicoin.net.cn/chart/api/data/period?symbol=bitfinexethusd&step=14400'
    # url = 'https://www.aicoin.net.cn/chart/api/data/period?symbol=bitfinexbtcusd&step=86400'
    url = 'https://www.aicoin.net.cn/chart/api/data/period?symbol={exchange}{symbol}&step={step}'.format(
        exchange=exchange.lower(), symbol=symbol.replace("_", "").lower(), step=PERIOD_INTERVAL_MAP[period]*60)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.100 Safari/537.36',
        'Host': 'www.aicoin.net.cn',
        'Cookie': 'step=86400; '
                  'acw_tc=7819730615376716393148290ed1478f70cb944ecf173e69e37c5c25b21eb5; '
                  'Hm_lvt_3c606e4c5bc6e9ff490f59ae4106beb4=1537671642; '
                  'Hm_lpvt_3c606e4c5bc6e9ff490f59ae4106beb4=1537671642; '
                  '_ga=GA1.3.1591811312.1537671643; _gid=GA1.3.970230023.1537671643; '
                  'XSRF-TOKEN=eyJpdiI6ImJwWXpiZWhwMVJERGVkYnpIb0RvS3c9PSIsInZhbHVlIjoiNytPYnJcL1hWSlBTNVhKQlVFRW9'
                  'ja0p4UXRxYmgrd3ZaSk02aHRpbFRkZlpGVnZIUW5LYjVRVG81S293OVIwcU5NYzR4b25kMnpSd3lwUGZOXC9vK1NsZz09I'
                  'iwibWFjIjoiNzg4MzI4M2VlNzc4ODdiNTBjNmM4ODc1NTY1MTZkNmI3YzZkNTk2MTY2YzQxYzk3YzBiMmMxNDkxZmQwZDQ'
                  '2ZiJ9; aicoin_session=eyJpdiI6IkE2ckNNRVwvQXhEN0gxczNzUlpVdlZBPT0iLCJ2YWx1ZSI6ImpIWjgreFBvUGpp'
                  'MXRqUldqMEc2eUx4a3Q3TG5icDVuV0xSVlBacm1VZk85em1ncHZVdTNJRFRMN29cL1poY21CdFV3VFN5YmRRWDBUNzh4Sm'
                  'hCNjNFZz09IiwibWFjIjoiMWRlODBkZTUwYzhhZTFmYWJhYmRjYWE5YjAwYzQ2NTI3YTI4YTgzM2JiYTIzM2M1NjI1NWFk'
                  'NWQ2ZDg1ODJlZCJ9',
        'Referer': 'https://www.aicoin.net.cn/chart/D331D4E2',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,fy;q=0.6,ru;q=0.5',
        'Connection': 'keep-alive'
    }
    print("Request: %s" % url)
    rsp_data = requests.get(url, headers=headers)
    rsp_json = json.loads(rsp_data.content)
    kline_list = rsp_json['data']
    return kline_list


def get_kline_data_future(symbol):
    # COMEX黄金  https://finance.sina.com.cn/futures/quotes/GC.shtml
    # url = 'https://stock2.finance.sina.com.cn/futures/api/jsonp.php/
    # var%20_GC2018_9_27=/GlobalFuturesService.getGlobalFuturesDailyKLine?symbol=GC&_=2018_9_27'
    get_kline_url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/' \
                    'GlobalFuturesService.getGlobalFuturesDailyKLine?symbol={symbol}'.format(symbol=symbol)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.100 Safari/537.36'
    }
    print("Request: %s" % get_kline_url)
    rsp = requests.get(get_kline_url, headers=headers)
    text = rsp.content.decode('utf-8')
    text = text.replace('date', '"date"').replace('open', '"open"').replace(
        'high', '"high"').replace('low', '"low"').replace('close', '"close"').replace('volume', '"volume"')
    data_js = json.loads(text)
    kline_list = []
    for item in data_js:
        dt = parse(item['date'])
        ts = int(time.mktime(dt.timetuple()))
        kline_list.append([ts, float(item['open']), float(item['high']), float(item['low']),
                           float(item['close']), int(item['volume'])])
    return kline_list


def get_kline_data_forex(symbol):
    # 1. 美元兑人民币 https://finance.sina.com.cn/money/forex/hq/USDCNY.shtml
    # https://vip.stock.finance.sina.com.cn/forex/api/jsonp.php/
    # var%20_fx_susdcny2018_9_27=/NewForexService.getDayKLine?symbol=fx_susdcny&_=2018_9_27
    # 2. 美元指数 https://finance.sina.com.cn/money/forex/hq/DINIW.shtml
    # https://vip.stock.finance.sina.com.cn/forex/api/jsonp.php/
    # var%20_DINIW2018_9_28=/NewForexService.getDayKLine?symbol=DINIW&_=2018_9_28
    today = datetime.now()
    today_str = today.strftime('%Y_%m_%d')
    # get_kline_url = 'http://vip.stock.finance.sina.com.cn/forex/api/jsonp.php/' \
    #                 'var%%20_{symbol}{date_str}=/NewForexService.getDayKLine?' \
    #                 'symbol={symbol}&_={date_str}'.format(symbol=symbol, date_str=today_str)
    get_kline_url = 'http://vip.stock.finance.sina.com.cn/forex/api/jsonp.php/' \
                    'var%25%2520_{symbol}{date_str}=/NewForexService.getDayKLine?' \
                    'symbol={symbol}&_={date_str}'.format(symbol=symbol, date_str=today_str)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.100 Safari/537.36'
    }
    print("Request: %s" % get_kline_url)
    rsp = requests.get(get_kline_url, headers=headers)
    if rsp.status_code != 200:
        print(rsp.text)
        return None
    text = rsp.content.decode('utf-8')
    text = text.split('("')[1].split('")')[0]
    text = text.replace(',|', '\n')
    df = pd.read_csv(StringIO(text), sep=',', header=None, names=['date', 'open', 'low', 'high', 'close'],
                     parse_dates=['date'])
    df = df.sort_values('date')
    kline_list = []
    for i in range(0, len(df)):
        ts = int(time.mktime(df['date'][i].timetuple()))
        kline_list.append([ts, float(df['open'][i]), float(df['high'][i]), float(df['low'][i]),
                           float(df['close'][i])])
    return kline_list


def get_kline_data(exchange, symbol, period=PERIOD_1DAY):
    # Return kline list: [[timestamp, open, high, low, last, volume], ..., [...]], timestamp从小到大
    #  <class 'list'>: [1451779200, 432.66, 433.07, 421.74, 428.39, 16295.81303537]
    #  <class 'list'>: [1451865600, 428.63, 435.67, 426.97, 432.9, 12602.32265027]
    if symbol in ['GC', 'CL']:  # (u'COMEX黄金', 'GC'), (u'NYMEX原油', 'CL')
        return get_kline_data_future(symbol)
    elif symbol in ['fx_susdcnh', 'DINIW']:  # (u'离岸美元人民币', 'fx_susdcnh'), (u'美元指数', 'DINIW'),
        return get_kline_data_forex(symbol)
    else:
        return get_kline_data_from_aicoin(exchange, symbol, period)


def get_marketcap_total(from_ts, to_ts):
    try:
        url = 'https://graphs2.coinmarketcap.com/global/marketcap-total/{from_ts}/{to_ts}/'.format(
            from_ts=from_ts, to_ts=to_ts)
        print("request marketcap-total url: %s" % url)
        marketcap_total_rsp = requests.get(url, timeout=30)
        if marketcap_total_rsp.status_code != 200:
            print("fail to get marketcap total, request return %d.", marketcap_total_rsp.status_code)
        marketcap_total_json = json.loads(marketcap_total_rsp.content)
        return marketcap_total_json
    except Exception as e:
        print("Exception to get_marketcap_total: %s" % e)
        return {}


if __name__ == "__main__":
    # ret_kline_list = get_kline_data('COMEX', 'GC')
    ret_kline_list = get_kline_data('CCM', 'fx_susdcnh')
    print("The length of kline list is %d." % len(ret_kline_list))
