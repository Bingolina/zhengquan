'''
目的：获取东方财富网的机构列表，并爬出这些机构分别持有哪些股票
目标网址：http://data.eastmoney.com/hsgtcg/InstitutionStatistics.aspx

用的方法：python3 + selenium webdriver3
1.要安装的库：selenium,openpyxl
命令行输入：pip install selenium
        pip install openpyxl
2.上网下载chromedriver.exe，chrome driver 安装版本要跟chrome一样（在浏览器的设置里面找）,放在Python安装目录下即可，我在D盘放了，就是下面参数的path
    网址：https://npm.taobao.org/mirrors/chromedriver
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpFunction import *
import math
from time import sleep, ctime
import threading
#参数
path = 'D:\Python\chromedriver.exe'  # 要改，chromedriver.exe在哪里
page_number=5 #可改（根据机构列表有多少页手动改）
Company_list_url = "http://data.eastmoney.com/hsgtcg/InstitutionStatistics.aspx" #不用改！！
nextLoc = '//div[@id="PageCont"]/a[text()="下一页"]' #不用改！！

def setupDriver():
    # chrome_options = webdriver.ChromeOptions()
    chrome_options = Options()
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            'javascript': 2
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)

    chrome_options.add_argument('--headless')  # 静默模式
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options, executable_path=path)
    # driver.set_page_load_timeout(10)   #没了这2句也能跑，这个是页面加载设置超时的时间
    # driver.set_script_timeout(10)
    return driver
def getNameListAndUrl():
    result=[]
    driver=setupDriver()
    #翻页
    for page in range(1, page_number+1):
        nowLoc = (By.XPATH, '//div[@id="PageCont"]/span[@class="at" and text()=' + str(page) + ']')
        nextPageLoc='//div[@id="PageCont"]/a[text()=' + str(page) + ']'
        print("获取机构第", page, "页")
        try:
            if page != 1:
                driver.find_element(By.XPATH, nextLoc).click()#点击下一页
                # driver.find_element(By.XPATH, nextPageLoc).click() #点击下一页
                WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(nowLoc))  # 等待，直到页面转到第page页，才继续
            else:
                driver.get(Company_list_url)
                WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(\
                    (By.XPATH, '//ul[@class="tabtit"]/li[@class="at"]/a[text()="每日机构统计"]')))  # 只是用来确认是我要的那一页
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.XPATH, "//tbody/tr/td[2]/a")))
        except Exception as e:
            print("没有第",page,"页", repr(e))

            break
        #下面是真正要的东西，获取代码和名称
        try:
            name_list=driver.find_elements(By.XPATH, "//tbody/tr/td[2]/a")
            url_list=driver.find_elements(By.XPATH, "//tbody/tr/td[3]/a")
            total_list = driver.find_elements(By.XPATH, "//tbody/tr/td[4]")#当日持有股票总个数
        except Exception as e:
            print("机构第", page, "页，找不到机构的位置", repr(e))
            break
        for i in range(len(name_list)):
            result.append([name_list[i].text,url_list[i].get_attribute("href"),total_list[i].text])
    driver.close()
    return result
def getTable(l,detail_page_number,n): #e.g
    result = []
    company=l[0]
    url = l[1]
    driver = setupDriver()
    # 翻页 ''
    for page in range(1, detail_page_number+1):
        nowLoc = (By.XPATH, '//div[@id="PageCont"]/span[@class="at" and text()=' + str(page) + ']')
        tableLoc=(By.XPATH, '//table[@id="tb_cgmx"]/tbody/tr')
        log('线程%d,%s,共%d页，进入第%d页' % (n,company,detail_page_number,page),n)
        try:
            if page != 1:
                driver.find_element(By.XPATH, nextLoc).click()#点击下一页
            else:
                driver.get(url)
            if detail_page_number!=1:
                WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(nowLoc))  # 等待，直到页面转到第page页，才继续
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(tableLoc))
            table = driver.find_elements(By.XPATH, '//table[@id="tb_cgmx"]/tbody/tr')
        except Exception as e:
            log('线程%d,%s,共%d页，第%d页的表没有加载完全.\n %s' % (n, company, detail_page_number, page, repr(e)), n)
            break
        try:
            for element in table:
                # date = element.find_element(By.XPATH, 'td[1]').text
                code = element.find_element(By.XPATH, 'td[2]/a').text
                name = element.find_element(By.XPATH, 'td[3]/a').text
                # shouPanJia = element.find_element(By.XPATH, 'td[4]/span').text
                # zhangDie = element.find_element(By.XPATH, 'td[5]/span').text
                chiGuShuLiang = element.find_element(By.XPATH, 'td[7]').text
                chiGuShiZhi = element.find_element(By.XPATH, 'td[8]').text
                percent = element.find_element(By.XPATH, 'td[9]').text
                change_1 = element.find_element(By.XPATH, 'td[10]/span').text
                result.append([company,str(today),code,name,chiGuShuLiang,chiGuShiZhi,percent,change_1])
        except Exception as e:
                l='线程%d,%s,共%d页，第%d页的表加载完全,但是取数有问题？？ %s' % (n, company, detail_page_number, page, repr(e))
                log(l, n)
                break
    driver.close()
    return result #[[],[]]
def Source(n):
    if not os.path.exists(url_save_txt):
        source=getNameListAndUrl()
        total = len(source)
        print("一共", total, "个机构")
        saveAndSplit(source,n)#分十份保存到十个txt
def runDetail(list,total,n,i):#list=[机构名，url，持有机构数量]
    detail_page_number = math.ceil(int(list[2]) / 50)
    # detail_page_number=2#测试用
    l='========线程%d,共%d个，现在是第%d个，%s，共%d页，时间开始：%s' % (n,total,(i+1),list[0],detail_page_number, ctime())
    log(l,n)
    return getTable(list, detail_page_number,n)
def loopDetail(n):# 第n个线程
    print("线程", n, "最开始的时间：", ctime())
    source=getUrl(n)#[[机构名，url，持有机构数量],[]],从对应txt获取
    total=len(source)
    sum=0
    for i in range(total):
        table_result=[]
        try:
            table_result=runDetail(source[i],total,n,i)
        except Exception as e:
            print("线程",n,"第",(i+1),"个出错",repr(e))

        if len(table_result)==int(source[i][2]):#确保保存下来的每一个机构的数据是完整的，不然就放到tmp.txt里面，后续重新跑
            saveResult(table_result, n)
            sum += int(source[i][2])
        else:
            l = '线程%d:  %s 失败,原因：结果有%d个，实际%s个，网址：%s，保存在tmp.txt' % (n,source[i][0],len(table_result),source[i][2],source[i][1])
            print(l)
            log(l, n)
            saveTmp(source[i])

        l='========线程 %d ,总共%d个，现在到%d，%s 结束，原本有%s个，实际%d个，时间结束：%s' % (n,total,i+1,source[i][0],source[i][2],len(table_result),ctime())
        log(l,n)
    print("线程",n,"结束，时间：",ctime(),"个数",sum)
# def chooseBrowser(browser):
#     if browser == 'ie':
#         driver = webdriver.Ie()
#     elif browser == "chrome":
#         driver = webdriver.Chrome()
#     elif browser == 'ff':
#         driver = webdriver.Firefox()
#     else:
#         print("browser 参数有误，只能为ie ，ff，chrome")
if __name__=='__main__':
    N = 1  # 假设分N个线程,不要调大，没有用，会炸
    Tag = 1 # 如果正常跑，填1，如果跑之前没有成功的url（就是tmp.txt里面的），改成2
    if Tag == 1:
        Source(N)
        startTime=ctime()
        threads = []
        for t in range(N):
            threads.append(threading.Thread(target=loopDetail, args=(t+1,)))

        # 启动线程
        for t in range(N):
            threads[t].start()
            sleep(2)
        # 守护线程
        for t in range(N):
            threads[t].join()
        sleep(10)

        print(' 主线程开始和结束:%s，%s' % (startTime,ctime()))
    if Tag==2:
        pass








