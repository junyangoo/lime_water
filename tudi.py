#! usr/bin/python
#coding:utf-8

import requests
import urllib2
import httplib
import re
import threading
import datetime
from  hbasemag import HbaseClient
from selenium import webdriver
class Spider:
      def __init__(self):       
          self.headers={
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6"
}
          # self.client=HbaseClient()
          # self.client.create_table("tudiurl", "name", "spider")
          # self.client.create_table("tudixinxi", "name", "spider")
          self.i = 0
          self.j = 0
          self.num = 0
          self.year = 2000
          self.month = 1
          self.day = 1
          self.url = 'http://www.landchina.com/default.aspx?tabid=263'
          self.postData = {'TAB_QueryConditionItem': '9f2c3acd-0256-4da2-a659-6949c4671a2a',
                           'TAB_QuerySortItemList': '282:False',
                           # 日期
                           'TAB_QuerySubmitConditionData': '9f2c3acd-0256-4da2-a659-6949c4671a2a:',
                           'TAB_QuerySubmitOrderData': '282:False',
                           # 第几页
                           'TAB_QuerySubmitPagerData': ''}
      def get_safety_dog(self):
          driver = webdriver.PhantomJS(executable_path='/root/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
          driver.get(
              "http://www.landchina.com/default.aspx?tabid=263&wmguid=75c72564-ffd9-426a-954b-8ac2df0903b7&p=")

          driver.find_element_by_css_selector(
              'body > div > div:nth-child(2) > input[type = "button"]').click()

      def handledate(self, year, month, day):
          # 返回日期数据
          'return date format %Y-%m-%d'
          date = datetime.date(year, month, day)
          #        print date.datetime.datetime.strftime('%Y-%m-%d')
          return date  # 日期对象

      def timedelta(self, year, month):
          # 计算一个月有多少天
          date = datetime.date(year, month, 1)
          try:
              date2 = datetime.date(date.year, date.month + 1, date.day)
          except:
              date2 = datetime.date(date.year + 1, 1, date.day)
          dateDelta = (date2 - date).days
          return dateDelta

      def get_pagecode(self, pageNum, date):
           try:
               # 指定日期和页数，打开对应网页，获取内容
               postData = self.postData.copy()
               # 设置搜索日期
               queryDate = date.strftime('%Y-%m-%d') + '~' + date.strftime('%Y-%m-%d')
               postData['TAB_QuerySubmitConditionData'] += queryDate
               # 设置页数
               postData['TAB_QuerySubmitPagerData'] = str(pageNum)
               # 请求网页
               r = requests.post(self.url, data=postData, timeout=30)
               r.encoding = 'gbk'
               pageCode = r.text
               return pageCode
           except urllib2.URLError, e:
               if hasattr(e,"reason"):
                   print u"连接土地市场网失败,失败原因为:",e.reason
                   return None
           except urllib2.HTTPError, Arguments:
               print Arguments
        
           except httplib.BadStatusLine, Arguments:
               print Arguments
        
           except IOError, Arguments:
               print Arguments
     
           except Exception, Arguments:
               print Arguments

      def get_allnum(self, date):
          # 1无内容  2只有1页  3 1—200页  4 200页以上
          pageCode = self.get_pagecode(1, date)
          if not pageCode:
              print u"页面加载失败"
              return None
          if len(pageCode) < 1000:
              self.get_safety_dog()
              pageCode = self.get_pagecode(1, date)
          if u'没有检索到相关数据' in pageCode:
              print date, 'have', '0 page'
              return 0
          pattern = re.compile(u'<td.*?class="pager".*?>共(.*?)页.*?</td>')
          result = re.search(pattern, pageCode)
          if result == None:
              print date, 'have', '1 page'
              return 1
          if int(result.group(1)) <= 200:
              print date, 'have', int(result.group(1)), 'page'
              return int(result.group(1))
          else:
              print date, 'have', '200 page'
              return 200
              # 第三步
      def get_link(self, pageNum, date):
           pageCode = self.get_pagecode(pageNum, date)
           if not pageCode:
                print u"页面加载失败"
                return None
           if len(pageCode) <1000:
               self.get_safety_dog()
               pageCode = self.get_pagecode(pageNum, date)
           pattern = re.compile('<td class="queryCellBordy">.*?<a href="(.*?tabid=386.*?)" target="_blank">(.*?)</a>.*?</td>',re.S)
           items = re.findall(pattern, pageCode)
           for item in items:
                  itemurl=str('http://www.landchina.com/')+item[0]
                  print itemurl
                  self.client.enqueueUrl("tudiurl",str(self.i),{ "spider:url": itemurl,"spider:state":"New","spider:mingzi":str(item[1])})
                  self.i=self.i+1
           return len(items)

      def getall_links(self, allNum, date):
          pageNum = 1
          allLinks = []
          while pageNum <= allNum:
              self.num = self.num + self.get_link(pageNum, date)
              print 'scrapy link from page', pageNum, '/', allNum
              pageNum += 1
          print date, 'have', self.num, 'link'
          self.num = 0

      def get_information(self,url):
           url=url
           pageCode=self.get_pagecode(url)
           print u"正在爬取网页", url
           if not pageCode:
                print u"页面加载失败"
                return None
           if len(pageCode) <1000:
               self.get_safety_dog()
               pageCode = self.get_pagecode(url)
           pattern=re.compile('<span id=".*?_r.*?_c.*?_ctrl">(.*?)</span>',re.S)
           items=re.findall(pattern, pageCode)
           self.client.put("tudixinxi",str(self.j),
                                      { "spider:行政区":str(items[1]),
                                        "spider:电子监管号":str(items[3]),
                                        "spider:项目名称":str(items[5]),
                                        "spider:项目位置":str(items[7]),
                                        "spider:面积(公顷)":str(items[9]),
                                        "spider:土地用途":str(items[13]),
                                        "spider:供地方式":str(items[15]),
                                        "spider:项目位置":str(items[7]),
                                        "spider:面积(公顷)":str(items[9]),
                                        "spider:土地用途":str(items[13]),
                                        "spider:供地方式":str(items[15]),
                                        "spider:土地使用年限":str(items[17]),
                                        "spider:行业分类":str(items[19]),
                                        "spider:土地级别":str(items[21]),
                                        "spider:成交价格(万元)":str(items[23]),
                                        "spider:项支付期号":str(items[29]),
                                        "spider:约定支付日期":str(items[30]),
                                        "spider:约定支付金额(万元)":str(items[31]),
                                        "spider:备注":str(items[32]),
                                        "spider:土地使用权人":str(items[38]),
                                        "spider:下限":str(items[42]),
                                        "spider:上限":str(items[44]),
                                        "spider:约定交地时间":str(items[46]),
                                        "spider:约定开工时间":str(items[48]),
                                        "spider:约定竣工时间":str(items[50]),
                                        "spider:实际开工时间":str(items[52]),
                                        "spider:实际竣工时间":str(items[52]),
                                        "spider:批准单位":str(items[56]),
                                        "spider:合同签订日期":str(items[58])}
                         )
           self.j=self.j+1
      def starturl(self):
          if self.year < datetime.date.today().year:
              if self.month <= 12:
                  delta = self.timedelta(self.year, self.month)
                  print delta
                  # 一个月一个月的抓取
                  if self.day <= delta:
                      # 日期
                      date = self.handledate(self.year, self.month, self.day)
                      # 页数
                      # allNum = self.get_allnum(date)
                      # # 链接
                      # self.getall_links(allNum, date)
                      self.day += 1
                      print date, 'KO!'
                  elif self.day > delta:
                      self.month = self.month + 1
                      self.day = 1
              elif self.month > 12:
                  self.year = self.year + 1
                  self.month = 1

          elif self.year == datetime.date.today().year:
              if self.month < datetime.date.today().month:
                  delta = self.timedelta(self.year, self.month)
                  print delta
                  # 一个月一个月的抓取
                  if self.day <= delta:
                      # 日期
                      date = self.handledate(self.year, self.month, self.day)
                      # if date < datetime.date.today():
                      #     print 45353
                      # 页数
                      # allNum = self.get_allnum(date)
                      # # 链接
                      # self.getall_links(allNum, date)
                      self.day += 1
                      print date, 'KO!'
                  elif self.day > delta:
                      self.month = self.month + 1
                      self.day = 1
              elif self.month == datetime.date.today().month:
                  delta = self.timedelta(self.year, self.month)
                  print delta
                  # 一个月一个月的抓取
                  if self.day <= datetime.date.today().day:
                      # 日期
                      date = self.handledate(self.year, self.month, self.day)
                      # if date < datetime.date.today():
                      #     print 45353
                      # 页数
                      # allNum = self.get_allnum(date)
                      # # 链接
                      # self.getall_links(allNum, date)
                      self.day += 1
                      print date, 'KO!'

          while(self.year <= 2017):
              while(self.month <= 12):
                  day = 1
                  delta = self.timedelta(self.year, self.month)
                  print delta
                  # 一个月一个月的抓取
                  while day <= delta:
                      # 日期
                      date = self.handledate(self.year, self.month, day)
                      # 页数
                      # allNum = self.get_allnum(date)
                      # # 链接
                      # self.getall_links(allNum, date)
                      day += 1
                      print date, 'KO!'
                  self.month = self.month + 1
              self.year = self.year + 1
              self.month = 1


spider=Spider()
for i in range(0, 10000):
    spider.starturl()

a=spider.client.dequeueUrl("tudiurl",0)
spider.client.update("tudiurl",str(0),{"spider:state":"Download"})
spider.get_information(a["spider:url"])























   


