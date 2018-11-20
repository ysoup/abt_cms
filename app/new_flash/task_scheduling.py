# encoding=utf-8
# from app.models import AccountManage, ArticleManage, ArticleUploadManage, InformationPlatform, NewInformationCategory
from selenium import webdriver

CLIENT_ID = "0cc1a088bfb71ae1e02176c11a8af98b"
executable_path = "/home/ywd/.pyenv/versions/3.5.2/bin/geckodriver"


def get_task():
    # 获取需要上传的文章
    rows = ArticleUploadManage.query.filter_by(send_status=0, send_type=0)
    if rows:
        for x in rows:
            # 获取上传的账户信息
            account_rows = AccountManage.query.filter_by(account_type=x.article_type,
                                                         platform_type=x.platform_type,
                                                         category_type=x.category_type)
            # 获取需要上传的文章信息
            article_rows = ArticleManage.query.filter_by(article_type=x.article_type,
                                                         category_type=x.category_type,
                                                         is_send=1)
            if article_rows and account_rows:
                for y in account_rows:
                    # 获取平台授权
                    browser = webdriver.Chrome(executable_path=executable_path)
                    url = "https://auth.om.qq.com/omoauth2/authorize?response_type=code&client_id=0cc1a088bfb71ae1e02176c11a8af98b&redirect_uri=http://houdun.net.cn&state=STATE"
                    browser.get(url)
                    browser.find_element_by_css_selector("[class='account-input']").send_keys(user_name)
                    browser.find_element_by_css_selector("[class='password-input']").send_keys(pass_word)
                    browser.find_element_by_css_selector("[class='btn btnLogin btn-primary']").click()




    print("aaaa")


if __name__ == '__main__':
    browser = webdriver.Firefox(executable_path=executable_path)
    url = "https://auth.om.qq.com/omoauth2/authorize?response_type=code&client_id=78274d6bfded051a82975cb4f4a36b58&redirect_uri=https://www.aibilink.com/&state=STATE"
    browser.get(url)
    browser.find_element_by_css_selector("[class='account-input']").send_keys("tfzij856@yeah.net")
    browser.find_element_by_css_selector("[class='password-input']").send_keys("sb123456")
    browser.find_element_by_css_selector("[class='btn btnLogin btn-primary']").click()
    print(browser.current_url)
    #get_task()
