import openpyxl
import datetime
import os
today = datetime.date.today()
oneday = datetime.timedelta(days=1)
yesterday = str(today - oneday)
month = str(datetime.datetime.now().month) + "月"
save_dir = "save/"+month + '/'
save_name = save_dir + "/" + str(today) + ".xlsx"

#保存方法1
def saveResult(each,table_result):
    if not os.path.exists(save_name):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        wb = openpyxl.Workbook()
    else:
        wb = openpyxl.load_workbook(save_name)
    ws = wb.create_sheet(title=each[0]+" "+each[1])
    ws.append(["持股日期","当日收盘价（元）","当日涨跌幅（%）","机构名称","持股数量（股）",\
               "持股市值（元）","持股数量占A股百分比（%）","持股市值变化—1日","持股市值变化—5日","持股市值变化—10日"])
    for i in table_result:
        ws.append(i)
    wb.save(save_name)
# 保存方法2  ：全部在一张表里
def saveAllResult(all_result):
    if not os.path.exists(save_name):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        wb = openpyxl.Workbook()
    else:
        wb = openpyxl.load_workbook(save_name)
    ws = wb.create_sheet('all',0)
    ws.append(["持股日期","当日收盘价（元）","当日涨跌幅（%）","机构名称","持股数量（股）",\
               "持股市值（元）","持股数量占A股百分比（%）","持股市值变化—1日","持股市值变化—5日","持股市值变化—10日"])
    for each in all_result:
        for i in each:
            ws.append(i)
    wb.save(save_name)