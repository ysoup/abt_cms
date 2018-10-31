import matplotlib
import matplotlib.pyplot as plt
import mpl_finance as mpf
import requests
import json
import time
from datetime import datetime
import numpy as np
from dateutil.parser import parse
import matplotlib.cbook as cbook
import matplotlib.image as image
from matplotlib.ticker import Formatter
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, DateFormatter, DayLocator, WeekdayLocator
from .get_kline_data import get_kline_data, get_marketcap_total


mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
alldays = DayLocator()              # minor ticks on the days
weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
dayFormatter = DateFormatter('%d')      # e.g., 12

TEXT_SIZE = 14
REAL_DATE_OFFSET = 100


def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    x = np.asarray(x)
    if type == 'simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    a = np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a


def relative_strength(prices, n=14):
    """
    compute the n period relative strength indicator
    http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
    http://www.investopedia.com/terms/r/rsi.asp
    """

    deltas = np.diff(prices)
    seed = deltas[:n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100. / (1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


def moving_average_convergence(x, nslow=26, nfast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and
    slow exponential moving avg

    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = moving_average(x, nslow, type='exponential')
    emafast = moving_average(x, nfast, type='exponential')
    return emaslow, emafast, emafast - emaslow


def show_kline_text(ax, last_date, open, high, low, close, ma_list):
    font_normal = {
        'size': TEXT_SIZE,
    }
    font_red = {
        'color': 'red',
        'weight': 'normal',
        'size': TEXT_SIZE,
    }
    font_green = {
        'color': 'green',
        'weight': 'normal',
        'size': TEXT_SIZE,
    }
    font_ma7 = {
        'color': 'dodgerblue',
        'weight': 'normal',
        'size': TEXT_SIZE,
    }
    font_ma15 = {
        'color': 'lime',
        'weight': 'normal',
        'size': TEXT_SIZE,
    }
    font_ma30 = {
        'color': 'gold',
        'weight': 'normal',
        'size': TEXT_SIZE,
    }
    font_ma45 = {
        'color': 'hotpink',
        'weight': 'normal',
        'size': TEXT_SIZE,
    }

    show_text = '时间:%s' % last_date.strftime("%Y-%m-%d %H:%M")
    show_text_x = 0.025
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_normal)

    show_text = '开:%.2f' % open
    show_text_x = 0.175
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_normal)

    show_text = '高:%.2f' % high
    show_text_x = show_text_x + 0.075  # 0.175
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_normal)

    show_text = '低:%.2f' % low
    show_text_x = show_text_x + 0.075
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_normal)

    show_text = '收:%.2f' % close
    show_text_x = show_text_x + 0.075
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_normal)

    show_text = '涨幅:'
    show_text_x = show_text_x + 0.075
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_normal)

    rise_rate = (float(close) - float(open)) * 100 / float(open)
    show_text = '%.2f%%' % rise_rate
    show_text_x = show_text_x + 0.035
    if rise_rate > 0:
        ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_red)
    else:
        ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_green)

    show_text = 'MA7:%.2f' % ma_list[0]
    show_text_x = show_text_x + 0.049
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_ma7)

    show_text = 'MA15:%.2f' % ma_list[1]
    show_text_x = show_text_x + 0.080
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_ma15)

    show_text = 'MA30:%.2f' % ma_list[2]
    show_text_x = show_text_x + 0.085
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_ma30)

    show_text = 'MA45:%.2f' % ma_list[3]
    show_text_x = show_text_x + 0.085
    ax.text(show_text_x, 0.95, show_text, transform=ax.transAxes, fontdict=font_ma45)


# 将x轴的浮点数格式化成日期小时分钟
# 默认的x轴格式化是日期被dates.date2num之后的浮点数，因为在上面乘以了1440，所以默认是错误的
# 只能自己将浮点数格式化为日期时间分钟
# 参考https://matplotlib.org/examples/pylab_examples/date_index_formatter.html
class MyFormatter(Formatter):
    def __init__(self, real_dates, multi=1440.0, fmt='%m/%d'):
        self.real_dates = real_dates
        self.multi = multi
        self.fmt = fmt

    def __call__(self, x, pos=0):
        """ Return the label for time x at position pos """
        ind = int(np.round(x))
        # ind就是x轴的刻度数值，不是日期的下标
        if ind - REAL_DATE_OFFSET >= len(self.real_dates):
            return ""
        return num2date(self.real_dates[ind-REAL_DATE_OFFSET]).strftime(self.fmt)


class MyTssFormatter(Formatter):
    def __init__(self, fmt='%m/%d'):
        self.fmt = fmt

    def __call__(self, x, pos=0):
        """ Return the label for time x at position pos """
        ind = float(x) / 1000.0
        dt = datetime.fromtimestamp(ind)
        # ind就是x轴的刻度数值，不是日期的下标
        return dt.strftime(self.fmt)


def find_kline_peaks_troughs(kline_list):
    # 查找K线的波峰和波谷：
    #   1. https://github.com/MonsieurV/py-findpeaks
    #   2. https://blog.csdn.net/freewebsys/article/details/78559737?locationNum=9&fps=1
    """
    import heapq
    numbers = [1, 3, 5, 2, 4, 1.1, 3.5, 4.8, 0.5, 2.4, -1.5]
    # 输出元祖第一个元素是index，第二元素是比较的数值
    print(heapq.nsmallest(5, enumerate(numbers), key=lambda x: x[1]))
    # [(10, -1.5), (8, 0.5), (0, 1), (5, 1.1), (3, 2)]

    print(heapq.nlargest(5, enumerate(numbers), key=lambda x: x[1]))
    # [(2, 5), (7, 4.8), (4, 4), (6, 3.5), (1, 3)]
    """
    pass


def draw_sistance_and_support_level(ax, kline_list, dates):
    # calc the lowest and highest
    highest_date = kline_list[-1][0]
    highest_price = kline_list[-1][2]
    lowest_date = kline_list[-1][0]
    lowest_price = kline_list[-1][3]
    for kline in kline_list[-45:]:
        if kline[2] > highest_price:
            highest_price = kline[2]
            highest_date = kline[0]
        if kline[3] < lowest_price:
            lowest_price = kline[3]
            lowest_date = kline[0]
    ax.plot([dates[-1] + 2, highest_date - 10], [highest_price, highest_price], label='highest', color='blue')
    ax.plot([dates[-1] + 2, lowest_date - 10], [lowest_price, lowest_price], label='lowest', color='darkorange')
    # 2nd lowest and highest <= 算法优化：寻找拱形和凹形
    highest_date2 = kline_list[-1][0]
    highest_price2 = kline_list[-1][2]
    lowest_date2 = kline_list[-1][0]
    lowest_price2 = kline_list[-1][3]
    for kline in kline_list:
        if kline[2] > highest_price2:
            highest_price2 = kline[2]
            highest_date2 = kline[0]
        if kline[3] < lowest_price2:
            lowest_price2 = kline[3]
            lowest_date2 = kline[0]
    if highest_date2 != highest_date:
        highest_last_date = kline_list[-1][0]
        highest_last_price = ((highest_price2 - highest_price) / (highest_date2 - highest_date)) * (
                highest_last_date - highest_date2) + highest_price2
        if (highest_date2 < highest_date) and (highest_date2 != kline_list[0][0]):
            ax.plot([highest_date2, highest_last_date], [highest_price2, highest_last_price],
                    label='highest', color='black')
        elif (highest_date2 > highest_date) and (highest_date != kline_list[0][0]):
            ax.plot([highest_date, highest_last_date], [highest_price, highest_last_price],
                    label='highest', color='black')


def draw_candlestick_volume(exchange, symbol, name, period, test=0):
    kline_list = get_kline_data(exchange, symbol, period)
    print("The length of kline list is %d." % len(kline_list))
    multi = 1.0
    real_dates = []
    dates = []
    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    kline_index = REAL_DATE_OFFSET - 1
    for kline in kline_list:
        kline_index = kline_index + 1
        opens.append(kline[1])
        highs.append(kline[2])
        lows.append(kline[3])
        closes.append(kline[4])
        volumes.append(kline[5])
        dt = datetime.fromtimestamp(kline[0])
        kline[0] = date2num(dt)
        # print("%d: %s %s" % (kline_index, dt, kline[0]))
        real_dates.append(kline[0])

        kline[0] = kline_index
        dates.append(kline[0])  # kline[0] or dates[kline_index] -> real_dates

    ma7 = moving_average(closes, 7, type='simple')
    ma15 = moving_average(closes, 15, type='simple')
    ma30 = moving_average(closes, 30, type='simple')
    ma45 = moving_average(closes, 45, type='simple')

    # plot data
    plot_limit = 120
    kline_list = kline_list[-plot_limit:]
    dates = dates[-plot_limit:]
    volumes = volumes[-plot_limit:]
    ma7 = ma7[-plot_limit:]
    ma15 = ma15[-plot_limit:]
    ma30 = ma30[-plot_limit:]
    ma45 = ma45[-plot_limit:]

    rise_dates = []
    rise_volumes = []
    fall_dates = []
    fall_volumes = []
    for kline in kline_list:
        if kline[4] > kline[1]:
            rise_dates.append(kline[0])
            rise_volumes.append(kline[5])
        else:
            fall_dates.append(kline[0])
            fall_volumes.append(kline[5])

    # 指定默认字体
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['examples.directory'] = '.'
    # 解决负号'-'显示为方块的问题
    matplotlib.rcParams['axes.unicode_minus'] = False
    plt.rc('axes', grid=True)
    plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
    left, width = 0.05, 0.92
    # left, bottom, width, height
    rect1 = [left, 0.25, width, 0.65]
    rect2 = [left, 0.1, width, 0.15]
    fig = plt.figure(facecolor='white', figsize=(16, 11.5))

    # datafile = cbook.get_sample_data('background.png', asfileobj=False)
    # im = image.imread(datafile)
    # # im[:, :, -1] = 0.5  # set the alpha channel
    # plt.figimage(im, 0.7, 1.2, zorder=3)

    axes_color = 'white'  # '#f6f6f6'  # the axes background color
    ax = fig.add_axes(rect1, facecolor=axes_color)
    ax2 = fig.add_axes(rect2, facecolor=axes_color, sharex=ax)

    ax.xaxis.set_major_formatter(weekFormatter)

    # 设置X轴刻度为日期时间
    ax.xaxis_date()
    ax.autoscale_view()
    ax.set_title('{name}（{period}）'.format(
        name=name, period=period), fontsize=20)
    mpf.candlestick_ohlc(ax, kline_list, width=0.4, colorup='r', colordown='green')
    plt.grid(True)

    formatter = MyFormatter(real_dates, multi=multi)
    ax.xaxis.set_major_formatter(formatter)

    line_ma7, = ax.plot(dates, ma7, color='dodgerblue', lw=1, label='MA (7)')
    line_ma15, = ax.plot(dates, ma15, color='lime', lw=1, label='MA (15)')
    line_ma30, = ax.plot(dates, ma30, color='gold', lw=1, label='MA (30)')
    line_ma45, = ax.plot(dates, ma45, color='hotpink', lw=1, label='MA (45)')

    # ax.legend(handles=[line_ma7, line_ma15, line_ma30, line_ma45], loc='best')  # 图例
    if 'BTC_USD' == symbol and '1day' == period:
        temp_kline_list = []
        for kline in kline_list:
            num = real_dates[kline[0]-REAL_DATE_OFFSET]
            dt = num2date(num).strftime('%Y-%m-%d')
            if dt not in ['2018-10-15']:
                temp_kline_list.append(kline)
        draw_sistance_and_support_level(ax, temp_kline_list, dates)

    last_date = num2date(real_dates[dates[-1] - REAL_DATE_OFFSET])
    show_kline_text(ax, last_date, kline_list[-1][1], kline_list[-1][2], kline_list[-1][3], kline_list[-1][4],
                    [ma7[-1], ma15[-1], ma30[-1], ma45[-1]])

    ax2.bar(rise_dates, rise_volumes, label="Volume", color="red")
    ax2.bar(fall_dates, fall_volumes, label="Volume", color="green")
    ax2.text(0.025, 0.95, 'Volume (%d)' % (volumes[-1]), va='top',
             transform=ax2.transAxes, fontsize=TEXT_SIZE)

    font_watermark = {'color': 'gray',  # gray, purple
                      'weight': 'normal',
                      'size': 108,
                      }
    ax.text(0.182, 0.618, 'AIBILINK.COM', va='top',
             transform=ax.transAxes, fontdict=font_watermark, alpha=0.4)

    cur_dt = datetime.fromtimestamp(time.time())
    cur_time = cur_dt.strftime("%H%M%S")
    cur_date = cur_dt.strftime("%Y%m%d")
    if test:
        kline_image = "" \
                      "kline_{exchange}_{symbol}_{period}_{cur_date}_{cur_time}.png".format(
                        exchange=exchange, symbol=symbol, period=period, cur_date=cur_date, cur_time=cur_time)
    else:
        kline_image = "app/static/research_paper/resources/" \
                      "kline_{exchange}_{symbol}_{period}_{cur_date}_{cur_time}.png".format(
                       exchange=exchange, symbol=symbol, period=period, cur_date=cur_date, cur_time=cur_time)
    plt.savefig(kline_image)
    plt.close('all')
    return kline_image


def draw_candlestick(exchange, symbol, name, period, test=0):
    kline_list = get_kline_data(exchange, symbol, period)
    print("The length of kline list is %d." % len(kline_list))
    multi = 1.0
    real_dates = []
    dates = []
    opens = []
    closes = []
    highs = []
    lows = []
    kline_index = REAL_DATE_OFFSET - 1
    for kline in kline_list:
        kline_index = kline_index + 1
        opens.append(kline[1])
        highs.append(kline[2])
        lows.append(kline[3])
        closes.append(kline[4])
        dt = datetime.fromtimestamp(kline[0])
        kline[0] = date2num(dt)
        # print("%d: %s %s" % (kline_index, dt, kline[0]))
        real_dates.append(kline[0])

        kline[0] = kline_index
        dates.append(kline[0])  # kline[0] or dates[kline_index] -> real_dates

    ma7 = moving_average(closes, 7, type='simple')
    ma15 = moving_average(closes, 15, type='simple')
    ma30 = moving_average(closes, 30, type='simple')
    ma45 = moving_average(closes, 45, type='simple')

    # plot data
    plot_limit = 120
    kline_list = kline_list[-plot_limit:]
    dates = dates[-plot_limit:]
    ma7 = ma7[-plot_limit:]
    ma15 = ma15[-plot_limit:]
    ma30 = ma30[-plot_limit:]
    ma45 = ma45[-plot_limit:]

    # 指定默认字体
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['examples.directory'] = '.'
    # 解决负号'-'显示为方块的问题
    matplotlib.rcParams['axes.unicode_minus'] = False
    plt.rc('axes', grid=True)
    plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
    left, width = 0.05, 0.92
    # left, bottom, width, height
    rect1 = [left, 0.1, width, 0.8]
    fig = plt.figure(facecolor='white', figsize=(16, 11.5))

    # datafile = cbook.get_sample_data('background.png', asfileobj=False)
    # im = image.imread(datafile)
    # # im[:, :, -1] = 0.5  # set the alpha channel
    # plt.figimage(im, 0.7, 1.2, zorder=3)

    axes_color = 'white'  # the axes background color
    ax = fig.add_axes(rect1, facecolor=axes_color)

    ax.xaxis.set_major_formatter(weekFormatter)

    # 设置X轴刻度为日期时间
    ax.xaxis_date()
    ax.autoscale_view()
    ax.set_title('{name}（{period}）'.format(
        name=name, period=period), fontsize=20)
    mpf.candlestick_ohlc(ax, kline_list, width=0.4, colorup='r', colordown='green')
    plt.grid(True)

    formatter = MyFormatter(real_dates, multi=multi)
    ax.xaxis.set_major_formatter(formatter)

    line_ma7, = ax.plot(dates, ma7, color='dodgerblue', lw=1, label='MA (7)')
    line_ma15, = ax.plot(dates, ma15, color='lime', lw=1, label='MA (15)')
    line_ma30, = ax.plot(dates, ma30, color='gold', lw=1, label='MA (30)')
    line_ma45, = ax.plot(dates, ma45, color='hotpink', lw=1, label='MA (45)')

    # ax.legend(handles=[line_ma7, line_ma15, line_ma30, line_ma45], loc='best')  # 图例

    last_date = num2date(real_dates[dates[-1] - REAL_DATE_OFFSET])
    show_kline_text(ax, last_date, kline_list[-1][1], kline_list[-1][2], kline_list[-1][3], kline_list[-1][4],
                    [ma7[-1], ma15[-1], ma30[-1], ma45[-1]])

    font_watermark = {'color': 'gray',  # gray, purple, red
                      'weight': 'normal',
                      'size': 108,
                      }
    ax.text(0.182, 0.618, 'AIBILINK.COM', va='top',
            transform=ax.transAxes, fontdict=font_watermark, alpha=0.4)

    cur_dt = datetime.fromtimestamp(time.time())
    cur_time = cur_dt.strftime("%H%M%S")
    cur_date = cur_dt.strftime("%Y%m%d")
    if test:
        kline_image = "" \
                      "kline_{exchange}_{symbol}_{period}_{cur_date}_{cur_time}.png".format(
                        exchange=exchange, symbol=symbol, period=period, cur_date=cur_date, cur_time=cur_time)
    else:
        kline_image = "app/static/research_paper/resources/" \
                      "kline_{exchange}_{symbol}_{period}_{cur_date}_{cur_time}.png".format(
                       exchange=exchange, symbol=symbol, period=period, cur_date=cur_date, cur_time=cur_time)
    plt.savefig(kline_image)
    plt.close('all')
    return kline_image


def draw_graph(data, name, display_name, test=0):
    # data: [[ts, price, volume], ...]
    tss = []
    prices = []
    for item in data:
        tss.append(item[0])
        prices.append(item[1])
    # 指定默认字体
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['examples.directory'] = '.'
    # 解决负号'-'显示为方块的问题
    matplotlib.rcParams['axes.unicode_minus'] = False
    plt.rc('axes', grid=True)
    plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
    left, width = 0.05, 0.92
    # left, bottom, width, height
    rect1 = [left, 0.1, width, 0.8]
    fig = plt.figure(facecolor='white', figsize=(16, 14.37269624573379))  # => width=Mm(146.5), height=Mm(131.6)

    # datafile = cbook.get_sample_data('background.png', asfileobj=False)
    # im = image.imread(datafile)
    # # im[:, :, -1] = 0.5  # set the alpha channel
    # plt.figimage(im, 0.7, 1.2, zorder=3)

    axes_color = 'white'  # '#f6f6f6'  # the axes background color
    ax = fig.add_axes(rect1, facecolor=axes_color)

    # ax.xaxis.set_major_formatter(weekFormatter)

    # # 设置X轴刻度为日期时间
    # ax.xaxis_date()
    formatter = MyTssFormatter()
    ax.xaxis.set_major_formatter(formatter)
    ax.autoscale_view()
    ax.set_title('{name}'.format(name=display_name), fontsize=20)
    ax.plot(tss, prices)
    plt.grid(True)

    font_watermark = {'color': 'gray',  # gray, purple
                      'weight': 'normal',
                      'size': 108,
                      }
    ax.text(0.182, 0.618, 'AIBILINK.COM', va='top',
            transform=ax.transAxes, fontdict=font_watermark, alpha=0.4)

    cur_dt = datetime.fromtimestamp(time.time())
    cur_time = cur_dt.strftime("%H%M%S")
    cur_date = cur_dt.strftime("%Y%m%d")
    if test:
        graph_image = "" \
                      "graph_{name}_{cur_date}_{cur_time}.png".format(
                        name=name, cur_date=cur_date, cur_time=cur_time)
    else:
        graph_image = "app/static/research_paper/resources/" \
                      "graph_{name}_{cur_date}_{cur_time}.png".format(
                        name=name, cur_date=cur_date, cur_time=cur_time)
    plt.savefig(graph_image)
    plt.close('all')
    return graph_image


if __name__ == "__main__":
    # draw_candlestick_volume("BITFINEX", "BTC_USD", "BTC/USD", "1day", test=1)
    # draw_candlestick_volume("BITFINEX", "BTC_USD", "BTC/USD", "4hour")
    # draw_candlestick_volume("BITFINEX", "BTC_USD", "BTC/USD", "15min")
    # draw_candlestick("COMEX", "GC", "COMEX黄金", "1day", test=1)
    # draw_candlestick("CCM", "fx_susdcnh", "离岸美元人民币", "1day", test=1)
    to_ts = int(time.time() * 1000)
    from_ts = to_ts - 365 * 24 * 3600 * 1000
    total_market_capitalization_data = get_marketcap_total(from_ts, to_ts)
    data_dict = {}
    marketcap_data = total_market_capitalization_data['market_cap_by_available_supply']
    for item in marketcap_data:
        data_dict[item[0]] = [item[1]]
    volumes_data = total_market_capitalization_data['volume_usd']
    for item in volumes_data:
        if item[0] in data_dict:
            data_dict[item[0]].append(item[1])
    data_list = []
    for ts, data in data_dict.items():
        data_list.append([ts, data[0], data[1]])
    data_list.sort(key=lambda k: k[0], reverse=False)
    draw_graph(data_list, 'marketcap_total', '总市值变化曲线图', test=1)



