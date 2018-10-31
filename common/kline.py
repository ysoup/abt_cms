import requests, json
from flask import current_app

#
def get_top_kline(exchange, symbol, period, size, since_data, since_time):
    try:
        url = current_app.config["KLINE"] +'kline'
        params = {'exchange':exchange, "symbol":symbol, "period":period, "size":size, "since_date":since_data, "since_time":since_time}
        res = requests.get(url, params=params)
        # current_app.logger.info("get_top_kline=== %s"%(json.loads(res.text)))
        return json.loads(res.text)
    except Exception as e :
        current_app.logger.error(e)

def get_index_data(symbol_list):
    try:
        data_list = []
        url = current_app.config['KLINE'] + 'ticker'
        for symbol in symbol_list:
            symbol = "INDEX_" +symbol
            params = {"exchange":"AIBILINK", "symbol":symbol, "market_type" : "INDEX"}
            res = requests.get(url, params=params)
            data_list.append(json.loads(res.text))
        # current_app.logger.info("get_index_data=== %s"%(data_list))
        return data_list
    except Exception as e :
        current_app.logger.error(e)


"""
 [
{'volume': 0.0, 'market_type': 0, 'close': 489.62, 'exchange': 'AIBILINK', 'timestamp': 1528974900000, 'symbol': 'INDEX_ETH', 'value': 0.0, 'mark': 0, 'high': 490.06, 'pre_close': 489.73, 'low': 489.55, 'time': '19:
15:00.000000', 'date': '20180614', 'market_subinfo': 0, 'open': 489.73}, 

{'volume': 0.0, 'market_type': 0, 'close': 489.05, 'exchange': 'AIBILINK', 'timestamp': 1528974000000, 'symbol': 'INDEX_ETH', 'value': 0.0, 'mark': 0, 
'high': 489.66, 'pre_close': 489.44, 'low': 488.95, 'time': '19:00:00.000000', 'date': '20180614', 'market_subinfo': 0, 'open': 489.44},

{'volume': 0.0, 'market_type': 0, 'close': 488.92, 'exchange': 'AIBILINK', 'timestamp': 1528973100000, 'symbol': 'INDEX_ETH', 'value': 0.0, 'mark': 0, 
'high': 489.13, 'pre_close': 488.82, 'low': 487.64, 'time': '18:45:00.000000', 'date': '20180614', 'market_subinfo': 0, 'open': 488.82}, 

{'volume': 0.0, 'market_type': 0, 'close': 489.67, 'exchange': 'AIBILINK', 'timestamp': 1528972200000, 'symbol': 'INDEX_ETH', 'value': 0.0, 'mark': 0, 
'high': 489.67, 'pre_close': 489.06, 'low': 488.89, 'time': '18:30:00.000000', 'date': '20180614', 'market_subinfo': 0, 'open': 489.06}, 

{'volume': 0.0, 'market_type': 0, 'close': 490.03, 'exchange': 'AIBILINK', 'timestamp': 1528971300000, 'symbol': 'INDEX_ETH', 'value': 0.0, 'mark': 0, 
'high': 490.18, 'pre_close': 489.69, 'low': 489.65,'time': '18:15:00.000000', 'date': '20180614', 'market_subinfo': 0, 'open': 489.7}
]

['19:15', '19:00', '18:45', '18:30', '18:15']

"""

"""
data_list = 
[
{'market_type': 'INDEX', 'high': 6281.45, 'total_coins_mined': 17117875.0, 'total_market_value': 103731754818.75, 
'open': 6279.16, 'value_7d': 22913184556.927498, 'mark': 0, 'low': 6043.44, 'market_subinfo': 0, 'channel': 'ticker', 
'highest_7d_increase_rate': 0.0278, 'exchange': 'AIBILINK', 'timestamp': 1530078468610, 'symbol': 'INDEX_BTC', 
'volume_7d': 3781147.1499999994, 'volume': 436179.1167723424, 'date': '20180627', 'low_7d': 5838.65, 'last': 6059.85, 
'value': 2643180020.772879, 'open_7d': 6717.48, 'time': '13:47:48.610000', 'high_7d': 6904.42}, 

{'market_type': 'INDEX', 'high': 457.3, 'total_coins_mined': 100329844.71779999, 'total_market_value': 43713713343.545456, 
'open': 456.72, 'value_7d': 5036101500.147, 'mark': 0, 'low': 432.39, 'market_subinfo': 0, 'channel': 'ticker', 
'highest_7d_increase_rate': 0.0388, 'exchange': 'AIBILINK', 'timestamp': 1530078468610, 'symbol': 'INDEX_ETH',
'volume_7d': 11558644.71, 'volume': 1704860.9426151442, 'date': '20180627', 'low_7d': 430.44, 'last': 435.7, 
'value': 742807912.6974183, 'open_7d': 529.11, 'time': '13:47:48.610000', 'high_7d': 549.62}
]

"""