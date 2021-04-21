import requests
import re
import time
import random
import pandas as pd
from time import sleep, ctime
import threading
import json
import openpyxl
import datetime
import os

def url1(page,date):
    month, day = date[:2], date[2:]
    url1 = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?callback=jQuery1123021347848488552068_1618556013073&st=HDDATE&sr=-1&ps=50&p="+str(page)+"&type=HSGTCOMSTA&token=894050c76af8597a853f5b408b759f5d&js=%7B%22data%22%3A(x)%2C%22pages%22%3A(tp)%2C%22font%22%3A(font)%7D&filter=(MARKET%3D%27N%27)(HDDATE%3D%5E2021%2F"+str(month)+"%2F"+str(day)+"%5E)"
    return url1
def url2(page,date,code):
    month, day = date[:2], date[2:]
    url2 = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?callback=jQuery1123004297432063462936_1618504179999&st=HDDATE&sr=-1&ps=50&p="+str(page)+"&token=894050c76af8597a853f5b408b759f5d&js=%7B%22data%22%3A(x)%2C%22pages%22%3A(tp)%2C%22font%22%3A(font)%7D&filter=(PARTICIPANTCODE%3D%27"+code+"%27)(MARKET+in+(%27001%27%2C%27003%27))(HDDATE%3D%5E2021%2F"+str(month)+"%2F"+str(day)+"%5E)&type=HSGTNHDDET"
    return url2
# 第一步获取所有机构
def main1(date):
    l=[]
    response = requests.get(url1(1, date))
    pages = re.findall('"pages":(.*?),',response.text)[0]
    print("pages=",pages)
    for page in range(1,int(pages)+1):
        response = requests.get(url1(page,date))
        print("page=", page,response.status_code)
        DATE = re.findall('"HDDATE":"(.*?)",',response.text)#日期
        participantCode = re.findall('"PARTICIPANTCODE":"(.*?)"',response.text)#机构编号
        print(participantCode)
        participantName = re.findall('"PARTICIPANTNAME":"(.*?)",',response.text)#机构名称
        SHAREHOLDCOUNT = re.findall('"SHAREHOLDCOUNT":(.*?),',response.text)#持股数量
        SHAREHOLDPRICE = re.findall('"SHAREHOLDPRICE":(.*?),',response.text)#持股市值
        ONE = re.findall('"SHAREHOLDPRICEONE":(.*?),',response.text)#一日市值变化
        FIVE = re.findall('"SHAREHOLDPRICEFIVE":(.*?),',response.text)#5日市值变化

        for i in range(len(DATE)):
            l.append([DATE[i][:10],participantCode[i],participantName[i],SHAREHOLDCOUNT[i],SHAREHOLDPRICE[i],
                          ONE[i],FIVE[i]])
            # 【日期，机构编号，机构名称，持股数量，持股市值，一日市值变化，5日市值变化】
        time.sleep(random.randint(2,4))
    print(len(l),l[0])
    return l
def getResponse(url):# 连接失败的话，尝试3次
    i = 0
    while i < 3:
        try:
            response = requests.get(url,timeout=(5,10))
            return response
        except requests.exceptions.RequestException as e:
            i += 1
            print("第%d次连接不上:" % i,e)
    return ""
# 第二步，获取所有持股信息
# 备注：因网络连接经常中断，跳过受影响的那个机构，直接下一个机构，不保存该机构已获取的持股信息，保存编号，后面再跑一次
def main2(date,codeList,countList):
    all=[]
    wrong_list_code=[]
    wrong_list_count=[]
    for i in range(len(codeList)):
        l=[]
        code, count = codeList[i],countList[i]
        print("now is %d,%s,共%s个========================" % (i + 1, code,count))
        response = getResponse(url2(1,date,code)) # 避免如果网络连接没有相应情况
        if response:
            pages = re.findall('"pages":(.*?),',response.text)[0]
            print("     pages=",pages)
            for page in range(1,int(pages)+1):
                response=getResponse(url2(page,date,code))
                if not response:
                    break
                print("     page=%d,状态码=%s" % (page,response.status_code))
                DATE = re.findall('"HDDATE":"(.*?)",',response.text)#日期
                participantName = re.findall('"PARTICIPANTNAME":"(.*?)",',response.text)#机构名称
                SCODE = re.findall('"SCODE":"(.*?)",', response.text)  # 股票编号
                SNAME = re.findall('"SNAME":"(.*?)",', response.text)  # 股票名称
                CLOSEPRICE = re.findall('"CLOSEPRICE":(.*?),', response.text)  # 当日收盘价
                SHAREHOLDSUM = re.findall('"SHAREHOLDSUM":(.*?),', response.text)  # 持股数量
                SHAREHOLDPRICE = re.findall('"SHAREHOLDPRICE":(.*?),', response.text)  # 持股市值
                ZDF = re.findall('"ZDF":(.*?),', response.text)  # 当日涨跌幅(%)
                ONE = re.findall('"SHAREHOLDPRICEONE":(.*?),', response.text)  # 一日市值变化
                FIVE = re.findall('"SHAREHOLDPRICEFIVE":(.*?),', response.text)  # 5日市值变化
                for j in range(len(DATE)):
                    l.append([DATE[j][:10],code,participantName[j],SCODE[j],SNAME[j],CLOSEPRICE[j],SHAREHOLDSUM[j],
                                  SHAREHOLDPRICE[j],ZDF[j],ONE[j],FIVE[j]])
                    # 【日期，机构编号，机构名称，股票编号，股票名称，当天收盘价，持股数量，持股市值，当日涨跌幅，一日市值变化，5日市值变化】
                time.sleep(random.randint(2,4))
        print("     结果=%d个" % len(l))
        if len(l) != int(count):
            print("**%s 持股数量不对,应该为%s" % (code,count),i)
            wrong_list_code.append(code)
            wrong_list_count.append(count)
        else:
            for k in l:
                all.append(k)
    return all,wrong_list_code,wrong_list_count

if __name__ == '__main__':
    t=["0415"]#要多少日期在这里填 "0408","0409","0412"
    startTime = ctime()
    # 获取某交易日机构编号
    for date in t:
        if not os.path.exists(date + "机构名单.xlsx"):
            l=main1(date)
            df1 = pd.DataFrame(l, columns=['日期', '机构编号', '机构名称', '持股数量','持股市值','一日市值变化','5日市值变化'])
            df1.to_excel(date+"机构名单.xlsx")
    # 获取持股详情
    for date in t:
        print("run %s机构名单.xlsx" % date)
        df = pd.read_excel(date+"机构名单.xlsx")
        codeList=df['机构编号'].tolist()
        countList=df['持股数量'].tolist()
        print("机构数量=",len(codeList),codeList)
        data,wrong_list_code, wrong_list_count = main2(date,codeList,countList)
        df1 = pd.DataFrame(data, columns=['日期','机构编号','机构名称','股票编号','股票名称','当天收盘价','持股数量','持股市值','当日涨跌幅','一日市值变化','5日市值变化'])
        df1.to_excel(date + "持股明细.xlsx")
        # 处理没有跑成功的
        if len(wrong_list_count)>0:
            r ,wrong_list_code, wrong_list_count = main2(date,wrong_list_code,wrong_list_count)
            sum=0
            for i in wrong_list_count:
                sum+=int(i)
            if len(r)==sum:
                df2 = pd.DataFrame(r,columns=['日期', '机构编号', '机构名称', '股票编号', '股票名称', '当天收盘价', '持股数量', '持股市值', '当日涨跌幅','一日市值变化', '5日市值变化'])
                df2.to_excel(date + "失败的例子又跑成功的.xlsx")
            else:
                print("wronglist 记录的机构没有跑成功")
                df3 = pd.DataFrame({"机构编号":wrong_list_code,"机构持股数量":wrong_list_count})
                df3.to_excel(date + "跑不成功的例子.xlsx")
    print('全部完成，开始时间%s，结束时间%s' % (startTime, ctime()))

