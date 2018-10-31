from hdfs.client import Client
import json
import urllib.request
import os, uuid
import urllib3
from retrying import retry
from flask import render_template, current_app
import sys


# 读取配置文件
with open("./crawler.json", "r") as fi:
    load_dict = json.load(fi)


def retry_if_io_error(exception):
    print(exception)
    return isinstance(exception, urllib3.exceptions.NewConnectionError)

# banner图片地址获取
# '/data/abt_cms/app/new_flash/images/banner_6.jpg'
# 传值的时候，img_name为banner_id相关
@retry(retry_on_exception=retry_if_io_error)
def upload_images_hdfs(img_name, img_url):
    try:
        if load_dict.__contains__('hadoop'):
            host = load_dict["hadoop"]["host"]
            port = load_dict["hadoop"]["port"]
            client = Client('{host}:{port}'.format(host=host, port=port), timeout=600)
            client.upload("/images", img_url, overwrite=True)
            new_img_url = "/aibicloud/images/" + img_name
            return new_img_url
    except Exception as e:
        current_app.logger.error(e)



# get information img url - hadoop
@retry(retry_on_exception=retry_if_io_error)
def upload_info_images_hdfs(img_name,img_url):
    try:
        if load_dict.__contains__('hadoop'):
            host = load_dict["hadoop"]["host"]
            port = load_dict["hadoop"]["port"]
            client = Client('{host}:{port}'.format(host=host, port=port), timeout=600)
            client.upload("/images", img_url, overwrite=True)
            new_img_url = "/aibicloud/images/" + img_name
            return new_img_url
    except Exception as e:
        current_app.logger.error(e)

# get coin_logo - hadoop
@retry(retry_on_exception=retry_if_io_error)
def upload_coin_logo_hdfs(img_name,img_url):
    try:
        if load_dict.__contains__('hadoop'):
            host = load_dict["hadoop"]["host"]
            port = load_dict["hadoop"]["port"]
            client = Client('{host}:{port}'.format(host=host, port=port), timeout=600)
            client.upload("/coin/logo", img_url, overwrite=True)
            new_img_url = "/aibicloud/coin/logo/" + img_name
            return new_img_url
    except Exception as e:
        current_app.logger.error(e)

