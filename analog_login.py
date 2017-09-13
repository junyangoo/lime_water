# coding:utf-8

import requests
import re

Username = ''
Password = ''
login_url = 'https://github.com/login'  # 登录页面
post_url = 'https://github.com/session'  # 表单提交

'''请求头'''
user_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'zh-CN,zh;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}

session = requests.Session()
login_html = session.get(login_url, headers=user_headers)
result = re.compile(r'<input name="authenticity_token" type="hidden" value="(.*)" />')
authenticity_token = result.findall(login_html.content)[0]  # 获取authenticity_token

'''表单信息'''
post_data = {
    'commit': 'Sign in',
    'utf8': '%E2%9C%93',
    'authenticity_token': authenticity_token,
    'login': Username,
    'password': Password
}


def get_session(url, headers, data):  # 保存登录信息,以登录身份获取信息
    opener = requests.Session()
    opener.post(url, headers=headers, data=data)  # post表单
    return opener

html = get_session(post_url, user_headers, post_data)
page = html.get("https://github.com/pricing")  # 以登录身份获取登陆后页面
print page.content


