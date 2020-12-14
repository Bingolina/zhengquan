'''
用的方法：python3 + selenium webdriver3
1.要安装的库：selenium,openpyxl
命令行输入：pip install selenium
        pip install openpyxl
2.上网下载chromedriver.exe，chrome driver 安装版本要跟chrome一样（在浏览器的设置里面找）,放在Python安装目录下即可，我在D盘放了，就是下面参数的path
    网址：https://npm.taobao.org/mirrors/chromedriver
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.options import Options
from helpFunction import *
#参数
path = 'D:\Python\chromedriver.exe'  # chromedriver.exe在哪里
page_number=1 #默认只要前2页
detail_page_number = 1 # 大部分持股详情页只有1页，如果没有定位到下一页就不翻页了

def setupDriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 静默模式
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=path)
    # driver.set_page_load_timeout(10)   #没了这2句也能跑，这个是页面加载设置超时的时间
    # driver.set_script_timeout(10)
    return driver
def getCodeAndName():
    result=[]
    driver=setupDriver()
    #翻页
    for page in range(1, page_number+1):
        if page != 1:
            print("第",page,"页")
            try:
                driver.find_element(By.XPATH, '//div[@id="PageCont"]/a[text()="下一页"]').click()
                sleep(1)
            except Exception as e:
                print("点击下一页有问题",repr(e))
                break
        else:
            print("第1页")
            try:
                driver.get("http://data.eastmoney.com/hsgtcg/list.html")
                driver.find_element(By.XPATH, '//ul[@id="mkt_type"]/li[@class="at border_left_1" and text()="北向"]')#只是用来确认是我要的那一页
                sleep(1)
            except Exception as e:
                print("北向第一页，网页加载异常", repr(e))
        #下面是真正要的东西，获取代码和名称
        try:
            code_list=driver.find_elements(By.XPATH, "//tbody/tr/td[2]/a")
            name_list=driver.find_elements(By.XPATH, "//tbody/tr/td[3]/a")
        except Exception as e:
            print("找不到代码和名称的位置", repr(e))
            break
        for i in range(len(code_list)):
            result.append([code_list[i].text,name_list[i].text])
        #print(result)   e.g.[['601012', '隆基股份'], ['300760', '迈瑞医疗']]
    driver.close()
    return result
def getTable(each): #e.g.['601012', '隆基股份']
    result = []
    driver = setupDriver()
    url = "http://data.eastmoney.com/hsgtcg/StockHdDetail.aspx?stock=" + each[0]
    # 翻页，大部分只有1页，少部分2页
    for page in range(1, detail_page_number+1):
        if page != 1:
            loc='//div[@id="PageCont"]/a[text()='+str(page)+']'
            try:
                driver.find_element(By.XPATH, loc).click()#试下第n页，存在的话，就点，不存在就说明没有这一页
                sleep(1)
                print("第",page,"页")
            except Exception as e:
                print("没有下一页了",repr(e))
                break
        else:
            print("第1页")
            try:
                driver.get(url)
                sleep(1)
            except Exception as e:
                print(each,"第一页，网页加载异常", repr(e))
        try:
            list = driver.find_elements(By.XPATH, '//table[@id="tb_cgmx"]/tbody/tr')
        except Exception as e:
            print("找不到详情表", repr(e))
            break
        for element in list:
            date = element.find_element(By.XPATH, 'td[1]').text
            shouPanJia = element.find_element(By.XPATH, 'td[2]/span').text
            zhangDie = element.find_element(By.XPATH, 'td[3]/span').text
            name = element.find_element(By.XPATH, 'td[4]/a').text
            chiGuShuLiang = element.find_element(By.XPATH, 'td[6]').text
            chiGuShiZhi = element.find_element(By.XPATH, 'td[7]').text
            percent = element.find_element(By.XPATH, 'td[8]').text
            change_1 = element.find_element(By.XPATH, 'td[9]/span').text
            change_5 = element.find_element(By.XPATH, 'td[10]/span').text
            change_10 =element.find_element(By.XPATH, 'td[11]/span').text
            result.append([each[0],each[1],date,shouPanJia,zhangDie,name,chiGuShuLiang,chiGuShiZhi,percent,change_1,change_5,change_10])
    driver.close()
    return result #[[],[]]


if __name__=='__main__':
    source=getCodeAndName()
    all_result=[]
    if source:
        print("source=",len(source))
        for each in source:
            print("现在是：",each,"=======================================")
            table_result=getTable(each)
            if table_result:
                # 输出方式 1：一个表多个sheets的保存
                #saveResult(each,table_result)
                #print(each,"有",len(table_result),"个","保存成功")

                all_result.append(table_result)
                print(each, "有", len(table_result), "个")
            else:
                print(each[0],each[1],"没有拿到表格")
        print("终于完了！",len(all_result))
        saveAllResult(all_result)#输出方式 2：全在同一张表里
    else:
        print("没有拿到代码和名称")