# -*- coding: utf-8 -*-
import re
import time
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import or_
from docxtpl import DocxTemplate, InlineImage, RichText, R
# for height and width you have to use millimeters (Mm), inches or points(Pt) class :
from docx.shared import Mm, Inches, Pt
import jinja2
from jinja2.utils import Markup
from flask import current_app
from .capture_image import capture_aibitou_dai_header, capture_btc_status_image
from .get_kline_data import get_marketcap_total
from .draw_candlestick import draw_candlestick, draw_candlestick_volume, draw_graph
from .. import models


class CoinQuantTechResult(object):
    def __init__(self):
        self.quant_tech_image = ''
        self.quant_tech_desc = ''


class CoinAnalysisInfo(object):
    def __init__(self):
        self.sn = 0
        self.coin = ''
        self.name = ''
        self.period_list = []
        self.quant_tech_result_list = []
        # self.quant_tech_desc_list = []


def get_coin_base_info(coin_id):
    coin_base_info = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == coin_id).first()
    return coin_base_info


def convert_price(price, reserved=5):
    try:
        # price_str = '{:f}'.format(price)  # str(price)
        price_str = str(price)
        if price_str.find('e') > 0:
            return price
        if float(price) < 1:
            i = 2
            for i in range(2, len(price_str)):
                if price_str[i] != '0':
                    break
            return float(price_str[0:i+reserved+1])
        else:
            i = price_str.find('.')
            return float(price_str[0:i+reserved+1])
    except Exception as e:
        current_app.logger.error("Exception to covert price: %s" % str(price))
        return price


def get_top_coins(sort_by, max_count, sort_type, since_id=0):
    market_request_address = current_app.config["KLINE"].split('/market/')[0]
    request_coin_list_url_format = '/market/v1/coin_listing?' \
                                   'sort_by={sort_by}&since_id={since_id}&direction=down' \
                                   '&max_count={max_count}&sort_type={sort_type}'

    top_coins_url = market_request_address + request_coin_list_url_format.format(
        sort_by=sort_by, since_id=since_id, max_count=max_count, sort_type=sort_type)
    current_app.logger.info("request top_coins_url: %s", top_coins_url)
    top_coins_rsp = requests.get(top_coins_url, timeout=30)
    if top_coins_rsp.status_code != 200:
        current_app.logger.error("fail to get top coins, request return %d.", top_coins_rsp.status_code)
    top_coins_json = json.loads(top_coins_rsp.content)
    for top_coin_json in top_coins_json['data']:
        top_coin_json['last'] = convert_price(top_coin_json['last'])
    return top_coins_json['data']


def get_coin_ticker(coin_code):
    market_request_address = current_app.config["KLINE"].split('/market/')[0]
    request_ticker_url = market_request_address + '/market/v1/ticker?exchange=AIBILINK' \
                                                  '&symbol=INDEX_{coin_code}&market_type=INDEX'.format(
                                                   coin_code=coin_code.upper())
    current_app.logger.info("request ticker: %s", request_ticker_url)
    ticker_rsp = requests.get(request_ticker_url, timeout=30)
    if ticker_rsp.status_code != 200:
        current_app.logger.error("fail to get coin ticker, request return %d.", ticker_rsp.status_code)
    ticker_json = json.loads(ticker_rsp.content)
    ticker_json['last'] = convert_price(ticker_json['last'])
    return ticker_json


def add_coin_ticker_chg_percent(ticker):
    ticker['percent_change_24h'] = (float(ticker['last']) - float(ticker['open'])) * 100 / float(ticker['open'])


def get_coin_cash_flow_before_24hour(coin_id):
    before_dt = datetime.fromtimestamp(time.time() - 24 * 3600)
    before_time = before_dt.strftime("%Y-%m-%d %H:%M:%S")
    net_inflow = 0
    coin_cash_flow = models.CoinCashFlow.query.filter(
        models.CoinCashFlow.coin_id == coin_id).filter(
        models.CoinCashFlow.collection_time <= before_time).order_by(
        models.CoinCashFlow.collection_time.desc()).first()
    if coin_cash_flow:
        net_inflow = coin_cash_flow.big_inflow - coin_cash_flow.big_outflow \
                     + coin_cash_flow.mid_inflow - coin_cash_flow.mid_outflow \
                     + coin_cash_flow.lit_inflow - coin_cash_flow.lit_outflow
    return net_inflow


def get_coin_cash_flow_detail(sn, coin_id, net_inflow):
    coin_cash_flow_detail = {'sn': sn, 'id': coin_id, 'net_inflow': net_inflow}
    coin_base_info = get_coin_base_info(coin_id)
    coin_cash_flow_detail['code'] = coin_base_info.code
    coin_ticker = get_coin_ticker(coin_base_info.code)
    coin_cash_flow_detail['last'] = coin_ticker['last']
    net_inflow_before_24hour = get_coin_cash_flow_before_24hour(coin_id)
    coin_cash_flow_detail['net_inflow_before_24hour'] = net_inflow_before_24hour
    coin_cash_flow_detail['net_inflow_chg'] = net_inflow - net_inflow_before_24hour
    if net_inflow_before_24hour != 0:
        coin_cash_flow_detail['net_inflow_chg_percent'] = (net_inflow - net_inflow_before_24hour) * 100 / net_inflow_before_24hour
    else:
        coin_cash_flow_detail['net_inflow_chg_percent'] = '--'
    return coin_cash_flow_detail


def get_cme_btc_price():
    try:
        ts = int(time.time() * 1000)
        url = 'http://hq.sinajs.cn/?_={ts}/&list=hf_BTC'.format(ts=ts)
        current_app.logger.info("request cme btc price: %s", url)
        price_rsp = requests.get(url, timeout=30)
        if price_rsp.status_code != 200:
            current_app.logger.error("fail to get cme btc price, request return %d.", price_rsp.status_code)
        data_list = price_rsp.text.split('"')[1].split(',')
        return float(data_list[0])  # last price
    except Exception as e:
        current_app.logger.error("Exception to get CME BTC price. %s", e)
        return '--'


def get_cboe_btc_price():
    try:
        ts = int(time.time() * 1000)
        url = 'https://hq.sinajs.cn/?_={ts}/&list=hf_XBT'.format(ts=ts)
        current_app.logger.info("request cboe btc price: %s", url)
        price_rsp = requests.get(url, timeout=30)
        if price_rsp.status_code != 200:
            current_app.logger.error("fail to get cboe btc price, request return %d.", price_rsp.status_code)
        data_list = price_rsp.text.split('"')[1].split(',')
        return float(data_list[0])  # last price
    except Exception as e:
        current_app.logger.error("Exception to get CBOE BTC price. %s", e)
        return 0


class HTMLHelper(object):
    """ Translates some html into word runs. """

    def __init__(self):
        self.get_tags = re.compile("(<[a-z,A-Z]+>)(.*?)(</[a-z,A-Z]+>)")

    def html_to_run_map(self, html_fragment):
        """ breakes an html fragment into a run map """
        ptr = 0
        run_map = []
        for match in self.get_tags.finditer(html_fragment):
            if match.start() > ptr:
                text = html_fragment[ptr:match.start()]
                if len(text) > 0:
                    run_map.append((text, "plain_text"))
            run_map.append((match.group(2), match.group(1)))
            ptr = match.end()
        if ptr < len(html_fragment) - 1:
            run_map.append((html_fragment[ptr:], "plain_text"))
        return run_map

    def insert_runs_from_html_map(self, paragraph, run_map):
        """ inserts some runs into a paragraph object. """
        for run_item in run_map:
            run = paragraph.add_run(run_item[0])
            if run_item[1] == "<i>":
                run.italic = True


def generate_paper(tpl_doc):
    try:
        current_app.logger.info("start to generate research paper using template %s.", tpl_doc)
        tpl = DocxTemplate(tpl_doc)
        cur_dt = datetime.fromtimestamp(time.time())
        cur_time = cur_dt.strftime("%H%M%S")
        cur_date = cur_dt.strftime("%Y%m%d")
        cur_month = datetime.now().month

        since_id = 0
        top_market_value_coins = []
        for i in range(0, 5):
            top_coins = get_top_coins(sort_by=1, max_count=20, sort_type=1, since_id=since_id)
            top_market_value_coins = top_market_value_coins + top_coins
            since_id = top_coins[-1]['id']
        top_market_value_coins.sort(key=lambda k: k['percent_change_24h'], reverse=True)  # True：从大到小
        top_rise_coins = top_market_value_coins[0:5]
        top_fall_coins = top_market_value_coins[-5:]
        top_fall_coins.reverse()

        # 资金流向
        coin_cash_flow_list = models.CoinCashFlow.query.filter(models.CoinCashFlow.collection_time > cur_date).order_by(
            models.CoinCashFlow.coin_id.asc()).order_by(
            models.CoinCashFlow.collection_time.desc())
        coin_cash_flow_dict = {}
        for coin_cash_flow in coin_cash_flow_list:
            if coin_cash_flow.coin_id not in coin_cash_flow_dict:
                net_inflow = coin_cash_flow.big_inflow - coin_cash_flow.big_outflow \
                             + coin_cash_flow.mid_inflow - coin_cash_flow.mid_outflow \
                             + coin_cash_flow.lit_inflow - coin_cash_flow.lit_outflow
                coin_cash_flow_dict[coin_cash_flow.coin_id] = net_inflow
                current_app.logger.debug("%s: %f", coin_cash_flow.coin_id, net_inflow)
        # get top inflow coins
        top_inflow_coins = []
        sn = 0
        top_inflow_tuple_coins = sorted(coin_cash_flow_dict.items(), key=lambda d: d[1], reverse=True)[:5]
        for top_inflow_tuple_coin in top_inflow_tuple_coins:
            sn = sn + 1
            top_inflow_coins.append(get_coin_cash_flow_detail(sn, top_inflow_tuple_coin[0], top_inflow_tuple_coin[1]))
        # get top outflow coins
        top_outflow_coins = []
        sn = 0
        top_outflow_tuple_coins = sorted(coin_cash_flow_dict.items(), key=lambda d: d[1], reverse=False)[:5]
        for top_outflow_tuple_coin in top_outflow_tuple_coins:
            sn = sn + 1
            top_outflow_coins.append(get_coin_cash_flow_detail(sn, top_outflow_tuple_coin[0], top_outflow_tuple_coin[1]))

        # get top coins of social_data
        # get today and before 7day
        coin_social_data_dict = {}
        cur_date_sql = cur_dt.strftime("%Y-%m-%d%%")
        before_7day_dt = datetime.fromtimestamp(time.time() - 7 * 24 * 3600)  # 7 days ago
        before_7day_date = before_7day_dt.strftime("%Y%m%d")
        before_7day_date_sql = before_7day_dt.strftime("%Y-%m-%d%%")
        coin_social_data_list = models.CoinSocialData.query.filter(
            or_(models.CoinSocialData.collection_time.like(cur_date_sql),
                models.CoinSocialData.collection_time.like(before_7day_date_sql))).order_by(
            models.CoinSocialData.coin_id.asc()).order_by(
            models.CoinSocialData.collection_time.desc())
        current_app.logger.info("coin_social_data_list, select (%s ~ %s): %d" % (before_7day_date_sql[0:10], cur_date_sql[0:10],
                                                                                 coin_social_data_list.count()))
        cur_date_index = 0
        reddit_index = 0
        twitter_index = 1
        facebook_index = 2
        for coin_social_data in coin_social_data_list.all():
            if coin_social_data.coin_id not in coin_social_data_dict:
                coin_social_data_dict[coin_social_data.coin_id] = [[-1, -1], [-1, -1], [-1, -1]]  # cur -> 7day
            cache_coin_social_data = coin_social_data_dict[coin_social_data.coin_id]
            if coin_social_data.collection_time.strftime("%Y%m%d") == cur_date:
                if cache_coin_social_data[reddit_index][cur_date_index] <= 0:
                    cache_coin_social_data[reddit_index][cur_date_index] = coin_social_data.reddit_subscribers
                if cache_coin_social_data[twitter_index][cur_date_index] <= 0:
                    cache_coin_social_data[twitter_index][cur_date_index] = coin_social_data.twitter_watchers
                if cache_coin_social_data[facebook_index][cur_date_index] <= 0:
                    cache_coin_social_data[facebook_index][cur_date_index] = coin_social_data.facebook_likes
            elif coin_social_data.collection_time.strftime("%Y%m%d") == before_7day_date:
                if cache_coin_social_data[reddit_index][cur_date_index+1] <= 0:
                    cache_coin_social_data[reddit_index][cur_date_index+1] = coin_social_data.reddit_subscribers
                if cache_coin_social_data[twitter_index][cur_date_index+1] <= 0:
                    cache_coin_social_data[twitter_index][cur_date_index+1] = coin_social_data.twitter_watchers
                if cache_coin_social_data[facebook_index][cur_date_index+1] <= 0:
                    cache_coin_social_data[facebook_index][cur_date_index+1] = coin_social_data.facebook_likes
        social_data_added_coins = [[], [], []]
        for coin_id, social_data in coin_social_data_dict.items():
            for social_type in range(0, 3):
                # calc added value
                if social_data[social_type][cur_date_index] > 0 and social_data[social_type][cur_date_index+1] > 0:
                    added = social_data[social_type][cur_date_index] - social_data[social_type][cur_date_index+1]
                    social_data_added_coins[social_type].append((coin_id, added,
                                                                 social_data[social_type][cur_date_index],
                                                                 social_data[social_type][cur_date_index+1]))
        top_social_data_added_coins = [[], [], []]
        for social_type in range(0, 3):
            # 取前5
            social_data_added_coins[social_type].sort(key=lambda k: k[1], reverse=True)
            sn = 0
            for added_coin in social_data_added_coins[social_type]:
                coin_base_info = get_coin_base_info(added_coin[0])
                if 0 == coin_base_info.is_available:
                    continue
                sn = sn + 1
                coin_ticker = get_coin_ticker(coin_base_info.code)
                if 0 == float(coin_ticker['open']):
                    percent_change_24h = '--'
                else:
                    percent_change_24h = (float(coin_ticker['last']) - float(coin_ticker['open'])) * \
                                         100.0 / float(coin_ticker['open'])
                top_social_data_added_coins[social_type].append({'sn': sn,
                                                                 'code': coin_base_info.code,
                                                                 'social_value_last': added_coin[2],
                                                                 'social_value_before_7day': added_coin[3],
                                                                 'social_value_chg_7day': added_coin[1],
                                                                 'last': coin_ticker['last'],
                                                                 'percent_change_24h': percent_change_24h})
                if 5 == sn:
                    break

        # DAI
        aibitou_dai_ticker = get_coin_ticker('DA')
        add_coin_ticker_chg_percent(aibitou_dai_ticker)
        aibitou_btc_ticker = get_coin_ticker('BTC')
        add_coin_ticker_chg_percent(aibitou_btc_ticker)

        # get aibitou_dai_header.png
        aibitou_dai_header_image = capture_aibitou_dai_header()
        aibitou_dai_header_desc = ''

        # total_market_capitalization_data
        to_ts = int(time.time() * 1000)
        from_ts = to_ts - 365 * 24 * 3600 * 1000
        marketcap_total_origin_data = get_marketcap_total(from_ts, to_ts)
        total_market_capitalization_data = {'timestamp': 0, 'total': 0, 'volume': 0, 'prev_total': 0, 'prev_volume': 0, }
        if 0 == len(marketcap_total_origin_data):
            total_market_capitalization_image = 'app/static/research_paper/templates/error_default.png'
        else:
            data_dict = {}
            marketcap_data = marketcap_total_origin_data['market_cap_by_available_supply']
            for item in marketcap_data:
                data_dict[item[0]] = [item[1]]
            volumes_data = marketcap_total_origin_data['volume_usd']
            for item in volumes_data:
                if item[0] in data_dict:
                    data_dict[item[0]].append(item[1])
            data_list = []
            for ts, data in data_dict.items():
                data_list.append([ts, data[0], data[1]])
            data_list.sort(key=lambda k: k[0], reverse=False)
            total_market_capitalization_data['timestamp'] = data_list[-1][0]
            total_market_capitalization_data['total'] = data_list[-1][1]
            total_market_capitalization_data['volume'] = data_list[-1][2]
            total_market_capitalization_data['prev_total'] = data_list[-2][1]
            total_market_capitalization_data['prev_volume'] = data_list[-2][2]
            total_market_capitalization_image = draw_graph(data_list, 'marketcap_total', '总市值变化曲线图')

        # get fear_and_greed_index_image
        fear_and_greed_index_image = ''
        fear_and_greed_index_last_desc = ''

        # get btc network status
        btc_network_status_image, btc_mineral_pool_hash_rate_image = capture_btc_status_image()

        # get hot_events
        hot_events_content = ''
        pagination = models.Report.query.filter(models.Report.is_delete == 0).order_by(
            models.Report.update_time.desc()).paginate(1, per_page=1, error_out=False)
        if len(pagination.items) > 0:
            # hot_events_content = pagination.items[0].content.split('】')[1]
            hot_events_content = pagination.items[0].content

        soup = BeautifulSoup(hot_events_content, 'html.parser').find_all()
        hot_events_block = RichText()
        for tag in soup:
            if (tag.name == 'p' and tag.parent.name != 'p') or (tag.name == 'br' and tag.parent.name != 'br'):
                current_app.logger.debug(tag.text)
                if '' == tag.text:
                    continue
                hot_events_block.add(tag.text + "\n\n")
            elif tag.name == 'li' and tag.parent.name != 'li':
                hot_events_block.add(tag.text + "\n", style='Subtle Reference')
        # html_helper = HTMLHelper()
        # run_map = html_helper.html_to_run_map(hot_events_content)

        # get cme btc future price info
        cme_btc_future_price = get_cme_btc_price()
        cme_btc_future_price_info = {'last': cme_btc_future_price, 'month': cur_month}
        # get cboe btc future price info
        cboe_btc_future_price = get_cboe_btc_price()
        cboe_btc_future_price_info = {'last': cboe_btc_future_price, 'month': cur_month}

        comex_gc_kline_image = draw_candlestick("COMEX", "GC", "COMEX黄金", "1day")
        usd_cnh_kline_image = draw_candlestick("CCM", "fx_susdcnh", "离岸美元人民币", "1day")
        usd_index_image = draw_candlestick("CCM", "DINIW", "美元指数", "1day")

        # coin_analysis_list
        analysis_coin_list = []
        coin_analysis_config = CoinAnalysisInfo()
        coin_analysis_config.sn = 1
        coin_analysis_config.coin = 'BTC'
        coin_analysis_config.name = '大哥BTC'
        coin_analysis_config.period_list = ['1day', '4hour']
        analysis_coin_list.append(coin_analysis_config)
        coin_analysis_config = CoinAnalysisInfo()
        coin_analysis_config.sn = 2
        coin_analysis_config.coin = 'ETH'
        coin_analysis_config.name = '大姨太ETH'
        coin_analysis_config.period_list = ['4hour']
        analysis_coin_list.append(coin_analysis_config)
        coin_analysis_config = CoinAnalysisInfo()
        coin_analysis_config.sn = 3
        coin_analysis_config.coin = 'XRP'
        coin_analysis_config.name = '瑞波XRP'
        coin_analysis_config.period_list = ['4hour']
        analysis_coin_list.append(coin_analysis_config)
        coin_analysis_config = CoinAnalysisInfo()
        coin_analysis_config.sn = 4
        coin_analysis_config.coin = 'EOS'
        coin_analysis_config.name = '柚子EOS'
        coin_analysis_config.period_list = ['4hour']
        analysis_coin_list.append(coin_analysis_config)
        coin_analysis_config = CoinAnalysisInfo()
        coin_analysis_config.sn = 5
        coin_analysis_config.coin = 'BCH'
        coin_analysis_config.name = '比特现金BCH'
        coin_analysis_config.period_list = ['4hour']
        analysis_coin_list.append(coin_analysis_config)
        coin_analysis_config = CoinAnalysisInfo()
        coin_analysis_config.sn = 6
        coin_analysis_config.coin = 'LTC'
        coin_analysis_config.name = '莱特币LTC'
        coin_analysis_config.period_list = ['4hour']
        analysis_coin_list.append(coin_analysis_config)

        coin_analysis_result_list = []
        for coin_analysis_config in analysis_coin_list:
            coin_analysis_result = {'sn': coin_analysis_config.sn, 'name': coin_analysis_config.name,
                                    'quant_tech_result_list': [],
                                    }
            symbol = "{coin}_USD".format(coin=coin_analysis_config.coin)
            for period in coin_analysis_config.period_list:
                kline_image = ''
                try:
                    kline_image = draw_candlestick_volume("BITFINEX", symbol, symbol.replace("_", "/"), period)
                except Exception as e:
                    current_app.logger.error("Exception to draw candlestick of %s %s. %s", symbol, period, e)
                kline_desc = ''
                inline_kline_image = InlineImage(tpl, kline_image,
                                                 width=Mm(202.8), height=Mm(141.7))
                coin_analysis_config.quant_tech_result_list.append((kline_image, kline_desc))
                coin_analysis_result['quant_tech_result_list'].append((inline_kline_image, kline_desc))
            coin_analysis_result_list.append(coin_analysis_result)

        context = {
            'aibitou_dai_ticker': aibitou_dai_ticker,
            'aibitou_btc_ticker': aibitou_btc_ticker,

            'aibitou_dai_header_image': InlineImage(tpl, aibitou_dai_header_image,
                                                    width=Mm(146.5), height=Mm(43.5)),
            'aibitou_dai_header_desc': aibitou_dai_header_desc,

            'total_market_capitalization_image': InlineImage(tpl, total_market_capitalization_image,
                                                             width=Mm(146.5), height=Mm(119.4)),
            'total_market_capitalization_data': total_market_capitalization_data,
            # 'fear_and_greed_index_image': InlineImage(tpl, fear_and_greed_index_image,
            #                                                  width=Mm(146.5), height=Mm(42)),
            'fear_and_greed_index_last_desc': fear_and_greed_index_last_desc,

            'btc_network_status_image': InlineImage(tpl, btc_network_status_image,
                                                    width=Mm(146.5), height=Mm(131.6)),
            'btc_mineral_pool_hash_rate_image': InlineImage(tpl, btc_mineral_pool_hash_rate_image,
                                                    width=Mm(146.5), height=Mm(131.6)),

            'hot_events_block': hot_events_block,

            # 'hot_events': [
            #     {'id': 1, 'content': '今晨，高盛首席财务官公开表示加密货币交易柜台相关消息不实。'
            #                            '在消息面刺激下市场做多热情有所回暖，BTC一度反弹至6500美元以上，'
            #                            '但技术破位，需要修复，投资者需注意短线市场风险，请密切关注盘面。'},
            #     {'id': 2, 'content': '俄罗斯央行副主席：对于数字货币的态度仍然保持克制，更多的是帮助政府制定法案。'},
            #     {'id': 3, 'content': 'V神拟对区块生产者和DApps强制征收ETH作为费用。'},
            # ],

            'top_rise_coins': top_rise_coins,
            'top_fall_coins': top_fall_coins,
            'top_inflow_coins': top_inflow_coins,
            'top_outflow_coins': top_outflow_coins,
            'top_reddit_subscribers_added_coins': top_social_data_added_coins[reddit_index],
            'top_twitter_watchers_added_coins': top_social_data_added_coins[twitter_index],
            'top_facebook_likes_added_coins': top_social_data_added_coins[facebook_index],

            'cme_btc_future_price_info': cme_btc_future_price_info,
            'cboe_btc_future_price_info': cboe_btc_future_price_info,

            'comex_gc_kline_image': InlineImage(tpl, comex_gc_kline_image,
                                                width=Mm(172.7), height=Mm(158)),
            'usd_cnh_kline_image': InlineImage(tpl, usd_cnh_kline_image,
                                               width=Mm(172.7), height=Mm(158)),
            'usd_index_image': InlineImage(tpl, usd_index_image,
                                           width=Mm(172.7), height=Mm(158)),

            'coin_analysis_list': coin_analysis_result_list
        }

        # tpl.render(context)
        jinja_env = jinja2.Environment(autoescape=True)
        tpl.render(context, jinja_env)

        # cur_dt = datetime.fromtimestamp(time.time())
        # cur_time = cur_dt.strftime("%H%M%S")
        # cur_date = cur_dt.strftime("%Y%m%d")
        output_paper = 'app/static/research_paper/outputs/research_paper_{cur_date}_{cur_time}.docx'.format(
            cur_date=cur_date, cur_time=cur_time)
        tpl.save(output_paper)
        current_app.logger.info("generate paper: %s", output_paper)
        return output_paper
    except Exception as e:
        current_app.logger.error("generate_paper exception: %s", e)
        raise


if __name__ == "__main__":
    generate_paper('templates/paper_tpl.docx')
