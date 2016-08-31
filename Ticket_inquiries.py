#!/usr/bin/env python


import re
import json
import time
import random
import requests
import datetime
import argparse
from urllib import parse
from bs4 import BeautifulSoup
#from user_agents import agents


session = requests.session()
#session.headers = {"hearders":random.choice(agents)}
cookie = {"Cookie":''}

def get_flight_info(**kwargs):
    flight_type = kwargs['flight_type']
    price_list = kwargs['price_list']
    time_range = int(kwargs['time_range'])
    from_city = kwargs['from_city']
    to_city = kwargs['to_city']
    day_time = kwargs['date_time']
    from_airport = input_airport_name(from_city)
    to_airport = input_airport_name(to_city)
    url = "http://flights.ctrip.com/domesticsearch/search/SearchFirstRouteFlights?DCity1" \
          "="+str(from_airport)+"&ACity1="+str(to_airport)+"&SearchType=S&DDate1="+str(day_time)+\
          "&IsNearAirportRecommond=0"
    print(url)
    data = session.get(url,timeout = 30,cookies = cookie).text
    sleeptime = (1, 2, 3, 4, 5,6, 1, 2, 1, 3, 1, 4)
    time.sleep(random.choice(sleeptime))
    lowest_price_list = json.loads(data)['lps']

    for key in list(lowest_price_list):
        if lowest_price_list[key] == 0:
            del(lowest_price_list[key])

    lowest_price_list_price = sorted(lowest_price_list.items(),key = lambda x:x[1])
    lowest_price_list_time = sorted(lowest_price_list.items(), key=lambda x: x[0])
    if int(time_range)>len(lowest_price_list):
        time_range = len(lowest_price_list)
    if price_list == 'price':
        print(lowest_price_list_price[0:time_range])
    if price_list == 'day':
        print(lowest_price_list_time[0:time_range])
    fis = json.loads(data)['fis']
    if len(fis) == 0:
        print("%s没有到%s的航班"%(from_city,to_city))
    else:
        for fi in fis:
            flight = fi['fn']
            fly_time = fi['dt']
            arrival_time = fi['at']
            fly_station = fi['dpbn']
            fly_station_code = fi['dcc']
            arrival_station = fi['apbn']
            arrival_station_code = fi['acc']
            if fi['sts'] != None:
                trans_city_name = fi['sts'][0]['cn']
                trans_arrive_time = fi['sts'][0]['at']
                trans_fly_time = fi['sts'][0]['dt']
                a = datetime.datetime.strptime(trans_arrive_time, '%Y-%m-%d %H:%M:%S')
                b = datetime.datetime.strptime(trans_fly_time, '%Y-%m-%d %H:%M:%S')
                stop_time =(b-a).seconds/60
            depart_brigdge = json.loads(fi['confort'])['DepartBridge']
            History_Punctuality = json.loads(fi['confort'])['HistoryPunctuality']
            tax = fi['tax']

            if flight_type == 'dirc':
                if fi['axp'] == None and fi['sts'] == None:
                    output_result(flight,fly_time,arrival_time,depart_brigdge,History_Punctuality,fly_station,
     fly_station_code,arrival_station, arrival_station_code,tax,fi)

            if flight_type == 'trans':
                if fi['sts'] != None:
                    output_result(flight,fly_time,arrival_time,depart_brigdge,History_Punctuality,fly_station,
     fly_station_code,arrival_station, arrival_station_code,tax,fi)
                    print("经停%s" % trans_city_name)
                    print("到达%s的时间为：%s，出发时间为：%s，中间停留：%s分钟" % (
                    trans_city_name, trans_arrive_time, trans_fly_time, stop_time))

            if flight_type == 'inter':
                if fi['axp'] != None:
                    print("该航班不是直达航班，您需要换乘其他交通工具")
                    if fi['axp']['ts']['cc'] != None or fi['axp']['fs']['cc'] != None:
                        if fi['axp']['ts']['cc'].lower() == to_city or fi['axp']['ts']['cc'] == to_city:
                            final_city_name = fi['axp']['fs']['cn']
                            print('该航班最终到达城市%s' % (final_city_name))
                        elif fi['axp']['fs']['cc'].lower() == from_city or fi['axp']['fs']['cc'] == from_city:
                            final_fly_city = fi['axp']['ts']['cn']
                            print('该航班由%s出发' % (final_fly_city))
                    else:
                        final_fly_city = fi['axp']['ts']['cn']
                        print('该航班由%s出发' % (final_fly_city))
                    output_result(flight,fly_time,arrival_time,depart_brigdge,History_Punctuality,fly_station,
     fly_station_code,arrival_station, arrival_station_code,tax,fi)
            if flight_type == 'all':
                output_result(flight, fly_time, arrival_time, depart_brigdge, History_Punctuality, fly_station,
                              fly_station_code, arrival_station, arrival_station_code, tax, fi)
def output_result(*args):
    (flight,fly_time,arrival_time,depart_brigdge,History_Punctuality,fly_station,
     fly_station_code,arrival_station, arrival_station_code,tax,fi) = args
    print("航班：", flight)
    print("起飞时间：", fly_time)
    print("到达时间：", arrival_time)
    print("廊桥率：", depart_brigdge)
    print("准点率：", History_Punctuality)
    print("出发站台：%s(%s)" % (fly_station, fly_station_code))
    print("到达站台：%s(%s)" % (arrival_station, arrival_station_code))
    print("民航发展基金:", tax)
    prices = fi['scs']
    for price in prices:
        alt_price = price['salep']
        print("可选价位", alt_price)
    print("==================================================")
def get_flight_url():
    all_flight_urls = []
    html = session.get('http://flights.ctrip.com/schedule/',timeout = 30).text
    bsobj = BeautifulSoup(html,"lxml")
    city_flights = bsobj.findAll("div",{"class":"m"})
    for city_flight in city_flights:
        flight_urls = re.findall('a href="(.*)"',str(city_flight))
        for flight_url in flight_urls:
            flight_url = 'http://flights.ctrip.com'+flight_url
            all_flight_urls.append(flight_url)
    for url in all_flight_urls:
        days = 1
        crawl_num = 1
    #while days<90:
        today = datetime.date.today()
        next_day = datetime.date(today.year, today.month,today.day) + datetime.timedelta(days)
        next_day = '{}-{}-{}'.format(next_day.year,next_day.month,next_day.day)
        print("出发日期：",next_day)
        sleeptime = (1, 2, 3, 4,8, 5, 1, 2, 1, 3, 1, 4)
        time.sleep(random.choice(sleeptime))
        html = session.get(url,timeout = 30).text
        crawl_num += 1
        bsobj = BeautifulSoup(html,'lxml')
        contents = bsobj.findAll('div',{"class":"m"})
        for content in contents:
            city_name = content.get_text()
            print(city_name)
            city_city_flights = re.findall('a href="(.*)"',str(content))
            for city_city_flight in  city_city_flights:
                citys = city_city_flight.split('/')[4].split('.')
                from_city = citys[0]
                to_city = citys[1]
                print(from_city,to_city)
                #get_flight_info(from_city,to_city,next_day)
                crawl_num += 1
                time.sleep(10)
        days += 1

def get_air_port_name(city):
    airport_code = []
    airport_name = []
    code = parse.quote(city,encoding='gb2312')
    url = "http://www.feeyo.com/airport_code.asp?code="+str(code)
    html = requests.get(url).content.decode('gb2312')
    bsobj = BeautifulSoup(html,"lxml")
    contents = bsobj.findAll("tr",{"onmouseout":"this.style.backgroundColor='';"})
    for content in contents :
        airport_code.append(content.findAll("td",{"align":"center"})[1].get_text())
        airport_name.append(re.findall('td nowrap="">(.*)</td><td nowrap',str(content))[0])
    return airport_name,airport_code


def input_airport_name(city):
    while True:
        airport_name,airport_code = get_air_port_name(city)
        if len(airport_name) == 0:
            print("该城市没有机场,请重新输入您出发的城市")
            city = input("请输入出发城市：")
        else:
            for i in range(len(airport_name)):
                print('%s(%s)'%(airport_name[i],airport_code[i]))
            if len(airport_name) == 1:
                airport = airport_code[0]
            else:
                airport = input('请输入机场代码:')
            return airport
            break
#def main(from_city,to_city,date_time,flight_type,price_list,):

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='终端查询机票价格')
    parser.add_argument('-C', '--from_city', dest='from_city', nargs='?', default='北京',
                        help='the set off city,default is Beijing.')
    parser.add_argument('-D', '--to_city', dest='to_city', nargs='?', default='上海',
                        help='the arrival city,default is 上海.')
    parser.add_argument('-T', '--date_time', dest='date_time', nargs='?', default=time.strftime(("%Y-%m-%d")),
                    help='set_off time,default time is todat')

    parser.add_argument('-F','--flight_type',dest = 'flight_type',nargs = '?',
                    default = 'all',help = 'choose the flight type:dirc is Direct Flights;'
                                           'trans is Transfer Flights;inter means you need '
                                           'take another Transportation,all is all of the three')
    parser.add_argument('-P', '--price_list', dest='price_list', nargs='?', default='price',
                        help='last 90 days price sort by price or time,price is print the '
                             'price_list order by price High to Low;day is sorted by time')
    parser.add_argument('-L','--time_range',dest='time_range',nargs='?',default=10,help =  'print time_range days fligth price')
    args = parser.parse_args()
    print(args.from_city,args.to_city,args.date_time,args.flight_type,args.price_list,args.time_range)

    get_flight_info(from_city=args.from_city,
                    to_city=args.to_city,
                    date_time=args.date_time,
                    flight_type=args.flight_type ,
                    price_list=args.price_list,
                    time_range=args.time_range)
