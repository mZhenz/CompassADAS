import requests, re
from urllib import parse
def query(region):
    header = {'User-Agent': 'Opera/8.0 (Windows NT 5.1; U; en)'}
    url = 'http://apis.map.qq.com/jsapi?'
    data = {
        'qt': 'poi',
        'wd': region,
        'pn': 0,
        'rn': 10,
        'rich_source': 'qipao',
        'rich': 'web',
        'nj': 0,
        'c': 1,
        'key': 'FBOBZ-VODWU-C7SVF-B2BDI-UK3JE-YBFUS',
        'output': 'jsonp',
        'pf': 'jsapi',
        'ref': 'jsapi',
        'cb': 'qq.maps._svcb3.search_service_0'}
    coordinate_url = url + parse.urlencode(data)
    r = requests.get(coordinate_url, headers=header)
    longitude = re.findall('"pointx":\s*"(.+?)"', r.text)[0]
    latitude = re.findall('"pointy":\s*"(.+?)"', r.text)[0]
    print([region, longitude, latitude])


query('广州')