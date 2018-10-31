# -*- coding: utf-8 -*-
from docxtpl import DocxTemplate, InlineImage
# for height and width you have to use millimeters (Mm), inches or points(Pt) class :
from docx.shared import Mm, Inches, Pt
import jinja2
from jinja2.utils import Markup

tpl = DocxTemplate('templates/paper_tpl.docx')

coin_list = [
    {"code": "BTC", "rank": 1, "high": 6386.8604, "total_coins_mined": 17275575.0, "total_market_value": 109647119185.7025, "english_name": "Bitcoin", "open": 6270.968, "id": 1, "chinese_name": "\u6bd4\u7279\u5e01", "low": 6236.6, "spark_chart": "/aibicloud/sparkchart/index/bitcoin.png?ts=1537338460", "highest_7d_increase_rate": 0.0473, "timestamp": 1537335675226, "symbol": "INDEX_BTC", "volume_7d": 1513949.3599999999, "percent_change_24h": 1.21156255302212, "volume": 217139.0518381066, "logo_img": "/aibicloud/coin/logo/btc.png", "low_7d": 6198.2027, "last": 6346.9447, "value": 1378169554.2268958, "open_7d": 6288.014, "website_slug": "bitcoin", "high_7d": 6585.4384},
    {"code": "XRP", "rank": 2, "high": 0.33568, "total_coins_mined": 99991850794, "total_market_value": 33294286558.878178, "english_name": "XRP", "open": 0.27463, "id": 3, "chinese_name": "\u745e\u6ce2\u5e01", "low": 0.2713, "spark_chart": "/aibicloud/sparkchart/index/xrp.png?ts=1537338460", "highest_7d_increase_rate": 0.2946, "timestamp": 1537338649002, "symbol": "INDEX_XRP", "volume_7d": 5714100291.92, "percent_change_24h": 21.243127116484, "volume": 1577004264.9475946, "logo_img": "/aibicloud/coin/logo/xrp.png", "low_7d": 0.25322, "last": 0.33297, "value": 525095110.09960055, "open_7d": 0.2593, "website_slug": "xrp", "high_7d": 0.33568},
    {"code": "ETH", "rank": 3, "high": 214.6392, "total_coins_mined": 102048721.0615, "total_market_value": 21639431301.091076, "english_name": "Ethereum", "open": 197.4132, "id": 2, "chinese_name": "\u4ee5\u592a\u574a", "low": 195.2882, "spark_chart": "/aibicloud/sparkchart/index/ethereum.png?ts=1537338460", "highest_7d_increase_rate": 0.2849, "timestamp": 1537335675226, "symbol": "INDEX_ETH", "volume_7d": 31663121.65, "percent_change_24h": 7.414296511074245, "volume": 4781025.512894916, "logo_img": "/aibicloud/coin/logo/eth.png", "low_7d": 167.6361, "last": 212.05, "value": 1013816460.0093671, "open_7d": 176.7595, "website_slug": "ethereum", "high_7d": 227.12},
    {"code": "XUC", "rank": 4, "high": 3.75, "total_coins_mined": 3000000000.0, "total_market_value": 10200000000.0, "english_name": "Exchange Union", "open": 3.35, "id": 585, "chinese_name": "\u96ea\u5e01", "low": 3.26, "spark_chart": "/aibicloud/sparkchart/index/exchange-union.png?ts=1537338460", "highest_7d_increase_rate": 0.3223, "timestamp": 1537336607102, "symbol": "INDEX_XUC", "volume_7d": 34744953.43, "percent_change_24h": 1.4925373134328306, "volume": 3745361.1965, "logo_img": "/aibicloud/coin/logo/xuc.png", "low_7d": 3.07, "last": 3.4, "value": 12734228.0681, "open_7d": 3.32, "website_slug": "exchange-union", "high_7d": 4.39},
    {"code": "BCH", "rank": 5, "high": 449.557, "total_coins_mined": 17275558.54498061, "total_market_value": 7546482239.20388, "english_name": "Bitcoin Cash", "open": 420.635, "id": 4, "chinese_name": "\u6bd4\u7279\u73b0\u91d1", "low": 412.1291, "spark_chart": "/aibicloud/sparkchart/index/bitcoin-cash.png?ts=1537338460", "highest_7d_increase_rate": 0.1102, "timestamp": 1537335675226, "symbol": "INDEX_BCH", "volume_7d": 4100265.5400000005, "percent_change_24h": 3.850131349031819, "volume": 684222.355255089, "logo_img": "/aibicloud/coin/logo/bch.png", "low_7d": 408.8394, "last": 436.83, "value": 298888851.4460805, "open_7d": 428.4473, "website_slug": "bitcoin-cash", "high_7d": 475.6551},
    {"code": "XLM", "rank": 6, "high": 0.2145, "total_coins_mined": 18784600595.0, "total_market_value": 3894235549.34945, "english_name": "Stellar", "open": 0.19611, "id": 6, "chinese_name": "\u6052\u661f\u5e01", "low": 0.1954, "spark_chart": "/aibicloud/sparkchart/index/stellar.png?ts=1537338460", "highest_7d_increase_rate": 0.1222, "timestamp": 1537335675226, "symbol": "INDEX_XLM", "volume_7d": 1656732141.22, "percent_change_24h": 5.711080516036912, "volume": 280192665.46446115, "logo_img": "/aibicloud/coin/logo/xlm.png", "low_7d": 0.18425, "last": 0.20731, "value": 58086741.47743744, "open_7d": 0.19141, "website_slug": "stellar", "high_7d": 0.2148},
    {"code": "LTC", "rank": 7, "high": 55.4537, "total_coins_mined": 58355406.31524642, "total_market_value": 3162378672.413939, "english_name": "Litecoin", "open": 51.539, "id": 7, "chinese_name": "\u83b1\u7279\u5e01", "low": 51.1659, "spark_chart": "/aibicloud/sparkchart/index/litecoin.png?ts=1537338460", "highest_7d_increase_rate": 0.165, "timestamp": 1537335675226, "symbol": "INDEX_LTC", "volume_7d": 25416356.910000004, "percent_change_24h": 5.146976076369343, "volume": 3650279.1184662553, "logo_img": "/aibicloud/coin/logo/ltc.png", "low_7d": 47.2818, "last": 54.1917, "value": 197814830.90418777, "open_7d": 50.5767, "website_slug": "litecoin", "high_7d": 58.9218},
    {"code": "USDT", "rank": 8, "high": 1.01, "total_coins_mined": 2756421736.0, "total_market_value": 2750633250.3544, "english_name": "Tether", "open": 1.01, "id": 10, "chinese_name": "\u6cf0\u8fbe\u5e01", "low": 0.9971, "spark_chart": "/aibicloud/sparkchart/index/tether.png?ts=1537338460", "highest_7d_increase_rate": 0.0121, "timestamp": 1537336607102, "symbol": "INDEX_USDT", "volume_7d": 45460048.83, "percent_change_24h": -1.198019801980198, "volume": 8897684.613345483, "logo_img": "/aibicloud/coin/logo/usdt.png", "low_7d": 0.9926, "last": 0.9979, "value": 8878999.475657457, "open_7d": 0.9979, "website_slug": "tether", "high_7d": 1.01},
    {"code": "I0C", "rank": 9, "high": 96.0, "total_coins_mined": 20993529.5859375, "total_market_value": 2015378840.25, "english_name": "I0Coin", "open": 0.03264, "id": 1173, "chinese_name": "", "low": 0.03254, "spark_chart": "/aibicloud/sparkchart/index/i0coin.png?ts=1537338460", "highest_7d_increase_rate": 4030.9194, "timestamp": 1537338303524, "symbol": "INDEX_I0C", "volume_7d": 15121.619999999999, "percent_change_24h": -294.64705882355, "volume": 20023.999389819997, "logo_img": "/aibicloud/coin/logo/i0c.png", "low_7d": 0.02239, "last": 96, "value": 0, "open_7d": 0.02381, "website_slug": "i0coin", "high_7d": 96.0},
    {"code": "DCN", "rank": 10, "high": 0.0002549, "total_coins_mined": 8000000000000.0, "total_market_value": 2012800000.0, "english_name": "Dentacoin", "open": 0.0002513, "id": 101, "chinese_name": "", "low": 0.0001877, "spark_chart": "/aibicloud/sparkchart/index/dentacoin.png?ts=1537338460", "highest_7d_increase_rate": 0.2974, "timestamp": 1537336607102, "symbol": "INDEX_DCN", "volume_7d": 2385598183.62, "percent_change_24h": -10.11937922801432842, "volume": 434918611.83592623, "logo_img": "/aibicloud/coin/logo/dcn.png", "low_7d": 0.0001877, "last": 0.0002516, "value": 109425.52273791903, "open_7d": 0.0002441, "website_slug": "dentacoin", "high_7d": 0.0003167}]

for coin in coin_list:
    coin['percent_change_24h'] = float("%.2f" % coin['percent_change_24h'])
    coin['volume'] = float("%.2f" % coin['volume'])

context = {
    'aibitou_dai_header_image': InlineImage(tpl, 'resources/aibitou_dai_header.png',
                                            width=Mm(146.5), height=Mm(43.5)),
    'aibitou_dai_header_desc': '今日上午BTC继续大幅跳水，带领整个市场大幅下跌，市场赚钱效应极差，'
                               '当前加密货币总市值为2092美元，较昨日大幅缩水300美元，24小时成交量为132美元，较昨日增加20美元。',

    'total_market_capitalization_image': InlineImage(tpl, 'resources/total_market_capitalization.png',
                                                     width=Mm(146.5), height=Mm(62.4)),
    'fear_and_greed_index_image': InlineImage(tpl, 'resources/fear_and_greed_index.png',
                                                     width=Mm(146.5), height=Mm(42)),
    'fear_and_greed_index_last_desc': '市场恐惧&贪婪指数为13，市场情绪再度进入极度恐慌状态，创下月内新低，投资者谨慎参与。',

    'hot_events': [
        {'id': 1, 'content': '今晨，高盛首席财务官公开表示加密货币交易柜台相关消息不实。'
                               '在消息面刺激下市场做多热情有所回暖，BTC一度反弹至6500美元以上，'
                               '但技术破位，需要修复，投资者需注意短线市场风险，请密切关注盘面。'},
        {'id': 2, 'content': '俄罗斯央行副主席：对于数字货币的态度仍然保持克制，更多的是帮助政府制定法案。'},
        {'id': 3, 'content': 'V神拟对区块生产者和DApps强制征收ETH作为费用。'},
    ],

    # 'top_rise_coins': [
    #     # {{ coin.code }}{{ coin.last }}{{ coin.percent_change_24h }}{{ coin.volume }}{{ coin.total_market_value }}
    #     {'code': 'XRP', 'last': 0.33297, 'percent_change_24h': 21.243127116484,
    #      'volume': 1577004264.9475946, 'total_market_value': 33294286558.878178},
    #
    #     {'code': 'XUC', 'last': 3.4, 'percent_change_24h': 1.4925373134328306,
    #      'volume': 3745361.1965, 'total_market_value': 10200000000},
    # ],
    'top_rise_coins': [coin_list[1], coin_list[0]],

    'top_fall_coins': coin_list[-2:],

    'coin_analysis_list': [
        {'sn': 1, 'name': '大哥BTC',
         'quant_tech_image': InlineImage(tpl, 'resources/coin_analysis_quant_tech_bitcoin_20180919_162200.png',
                                         width=Mm(146.5), height=Mm(65.4)),
         'quant_tech_desc': '今日BTC高位窄幅震荡，昨日创了新高后，横盘走势。均线指标多都排列，继续走高。'
                            '日线级别的布林带持续发散走势，币价沿着布林带上轨走高。MACD双线穿越零轴继续向上，'
                            '绿注昨天出现小幅背离，币价新高，绿注并未放大，今日有望小幅回调修复指标。ka ka\r\n'
                            'BTC上方阻力7500美元，也是斐波那契0.618分位，也是下降三角形的上边沿，'
                            '所以随着币价的上涨，风险也在集聚。如果盘中出现了瞬间打穿动作，可先减掉一部分仓位，'
                            '观察能否有效站稳，有效站稳后再加回仓位。'
         },
        {'sn': 2, 'name': '大姨太ETH',
         'quant_tech_image': InlineImage(tpl, 'resources/coin_analysis_quant_tech_ethereum_20180919_162200.png',
                                         width=Mm(146.5), height=Mm(65.4)),
         'quant_tech_desc': '小姨太走势绵软无力，量能萎缩。均线指标呈多头排列，币价有望回踩7天线后继续攀升。'
                            'MACD双线均在0轴以下，但趋势是向上，一两天内快速平滑曲线将会翻上0轴，绿注有所减弱，'
                            '明天是关键，如果不能拉出，可能前天的阳线作用失效了。关注7天线支撑，跌破后减仓，当前继续持币为主。'
         },
        {'sn': 3, 'name': '柚子EOS',
         'quant_tech_image': InlineImage(tpl, 'resources/coin_analysis_quant_tech_eos_20180919_162200.png',
                                         width=Mm(146.5), height=Mm(65.4)),
         'quant_tech_desc': '柚子维持高位横盘，今日波动幅度非常小，成交量还可以。币价还在7天线附近波动，'
                            '均线多头排列，但有走弱迹象。MACD快速线走平，慢速线即将翻上零轴。柚子也在等待大哥的信号，'
                            '即将变盘。下方支撑6.35美元，跌破后止盈出来。'
        },
    ]
}

# tpl.render(context)
jinja_env = jinja2.Environment(autoescape=True)
tpl.render(context, jinja_env)
tpl.save('outputs/paper.docx')
