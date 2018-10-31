import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from flask import current_app

ERROR_DEFAULT_IMAGE = 'app/static/research_paper/templates/error_default.png'
global_browser = None


def get_browser():
    global global_browser
    if global_browser:
        return global_browser
    else:
        global_browser = webdriver.PhantomJS()
        return global_browser


def capture_aibitou_dai_header():
    browser = None
    try:
        current_app.logger.info("start capture_aibitou_dai_header.")
        url = "https://www.aibilink.com/mobile/markets"

        cur_dt = datetime.fromtimestamp(time.time())
        cur_time = cur_dt.strftime("%H%M%S")
        cur_date = cur_dt.strftime("%Y%m%d")

        save_fn = "app/static/research_paper/resources/aibitou_market_index_{}_{}.png".format(cur_date, cur_time)
        save_fn_part = 'app/static/research_paper/resources/aibitou_dai_header_{}_{}.png'.format(cur_date, cur_time)

        # 设置浏览器参数，伪装成浏览器
        dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)  # 设置userAgent
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ")
        # 打开浏览器
        browser = webdriver.PhantomJS(desired_capabilities=dcap)
        # browser = get_browser()
        browser.set_window_size(1200, 900)
        browser.set_page_load_timeout(10)
        browser.set_script_timeout(10)
        ret = browser.get(url)  # Load page
        current_app.logger.info("%s", str(ret))
        browser.execute_script("""
                (function () {
                    $(".new_user_box,.short_term_box").hide();
                })();
            """)
        time.sleep(5)
        browser.execute_script("""
                (function () {
                    var market_banner = document.querySelector('.market-swiper-container').swiper;
                    market_banner.autoplay.stop();
                    $(".swiper-pagination-bullet:eq(0)").trigger("click");
                })();
            """)
        time.sleep(1)

        browser.save_screenshot(save_fn)
        elements = browser.find_elements_by_xpath('/html/body/article/section')
        left = elements[0].location['x']
        top = elements[0].location['y']
        right = elements[1].location['x'] + elements[1].size['width']
        bottom = elements[1].location['y'] + elements[1].size['height']

        im = Image.open(save_fn)
        im = im.crop((left, top, right, bottom))
        im.save(save_fn_part)
        browser.close()
        time.sleep(1)
        current_app.logger.info("end capture_aibitou_dai_header.")
        return save_fn_part
    except Exception as e:
        current_app.logger.error("capture_aibitou_dai_header exception: %s", e)
        browser.execute_script('window.stop()')
        if browser:
            browser.close()
        return ERROR_DEFAULT_IMAGE


def capture_btc_status_image(test=0):
    browser = None
    try:
        current_app.logger.info("start capture_btc_status_image.")
        # raise Exception("Do not capture.")

        url = "https://btc.com/"

        cur_dt = datetime.fromtimestamp(time.time())
        cur_time = cur_dt.strftime("%H%M%S")
        cur_date = cur_dt.strftime("%Y%m%d")

        if test:
            save_fn = "btc_com_{}_{}.png".format(cur_date, cur_time)
            save_fn_part_status = 'btc_network_status_{}_{}.png'.format(cur_date, cur_time)
            save_fn_part_hashrate = 'btc_hash_rate_{}_{}.png'.format(cur_date, cur_time)
        else:
            save_fn = "app/static/research_paper/resources/btc_com_{}_{}.png".format(cur_date, cur_time)
            save_fn_part_status = 'app/static/research_paper/resources/btc_network_status_{}_{}.png'.format(cur_date,
                                                                                                            cur_time)
            save_fn_part_hashrate = 'app/static/research_paper/resources/btc_hash_rate_{}_{}.png'.format(cur_date,
                                                                                                         cur_time)

        # 设置浏览器参数，伪装成浏览器
        dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)  # 设置userAgent
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ")
        # 打开浏览器
        browser = webdriver.PhantomJS()
        chrome_options = Options()
        # 无头模式启动
        chrome_options.add_argument('--headless')
        # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--lang=zh-CN')
        # 初始化实例
        browser = webdriver.Chrome(chrome_options=chrome_options)
        # browser = get_browser()
        browser.set_window_size(1200, 1800)
        browser.set_page_load_timeout(15)
        browser.set_script_timeout(15)
        ret = browser.get(url)  # Load page
        current_app.logger.info("%s", str(ret))
        time.sleep(5)
        browser.save_screenshot(save_fn)
        elements = browser.find_elements_by_css_selector('div.col-xs-6')
        # save part 1
        left = elements[0].location['x']
        top = elements[0].location['y']
        right = elements[0].location['x'] + elements[0].size['width']
        bottom = elements[0].location['y'] + elements[0].size['height']
        im = Image.open(save_fn)
        im = im.crop((left, top, right, bottom))
        im.save(save_fn_part_hashrate)
        # save part 2
        left = elements[1].location['x']
        top = elements[1].location['y']
        right = elements[1].location['x'] + elements[1].size['width']
        bottom = elements[1].location['y'] + elements[1].size['height']
        im = Image.open(save_fn)
        im = im.crop((left, top, right, bottom))
        im.save(save_fn_part_status)
        browser.close()
        current_app.logger.info("end capture_btc_status_image.")
        return save_fn_part_hashrate, save_fn_part_status
    except Exception as e:
        current_app.logger.error("capture_btc_status_image exception: %s, %s", type(e), e)
        # browser.execute_script('window.stop()')
        if browser:
            browser.close()
        return ERROR_DEFAULT_IMAGE, ERROR_DEFAULT_IMAGE


if __name__ == "__main__":
    # capture_aibitou_dai_header()
    # capture_total_market_capitalization_image(test=1)
    print(capture_btc_status_image(test=1))

