import json
import urllib3
from UI.city import citycode
from urllib.request import urlopen
from bs4 import BeautifulSoup
from UI.city import citycode

# from bs4 import BeautifulSoup
http = urllib3.PoolManager()

def getWeather(cityname):
   cityc = citycode.get(cityname)
   resp = urlopen('http://www.weather.com.cn/weather/%s.shtml' % cityc)
   soup = BeautifulSoup(resp, 'html.parser')
   # print(soup)
   tagToday = soup.find('p', class_="tem")  # 第一个包含class="tem"的p标签即为存放今天天气数据的标签
   # print(tagToday)

   try:
      temperatureHigh = tagToday.span.string  # 有时候这个最高温度是不显示的，此时利用第二天的最高温度代替。
   except AttributeError as e:
      temperatureHigh = tagToday.find_next('p', class_="tem").span.string  # 获取第二天的最高温度代替

   temperatureLow = tagToday.i.string  # 获取最低温度
   weather = soup.find('p', class_="wea").string  # 获取天气

   t = temperatureLow + '~' + temperatureHigh + '℃'
   w =  weather
   return w,t
