import pandas as pd
from tqdm import tqdm

data1 = pd.read_excel(r'E:\PycharmProjects\zhengquan\20210128.xlsx')  # 读取前一天数据，需要修改路径
data2 = pd.read_excel(r'E:\PycharmProjects\zhengquan\20210129.xlsx')  # 读取后一天数据，需要修改路径

data1 = data1[['机构分类','机构名称','持股日期','股票名称','持股数量']]
data1.rename(columns={'持股日期':'持股日期1','持股数量':'持股数量1'},inplace=True)
data2 = data2[['机构分类','机构名称','持股日期','股票名称','持股数量']]
data2.rename(columns={'持股日期':'持股日期2','持股数量':'持股数量2'},inplace=True)
data = pd.merge(data1, data2, how='outer', on=['机构分类', '机构名称','股票名称'])


#data['持股数量1'][~data['持股数量1'].isnull()] = [float(i[:-1]) for i in data['持股数量1'][~data['持股数量1'].isnull()]]
#data['持股数量2'][~data['持股数量2'].isnull()] = [float(i[:-1]) for i in data['持股数量2'][~data['持股数量2'].isnull()]]
'''单位为元'''
'''此部分耗时较长，原数据格式为不规则单位字符串，需要单独处理'''
for i in tqdm(range(len(data))):
    tmp = data['持股数量1'][i]
    try:
        if tmp[-1] == '万':
            data['持股数量1'][i] = float(tmp[:-1]) * 10000
        elif tmp[-1] == '亿':
            data['持股数量1'][i] = float(tmp[:-1]) * 100000000
        else:
            pass
    except:  # 数字为nan
        pass

for i in tqdm(range(len(data))):
    tmp = data['持股数量2'][i]
    try:
        if tmp[-1] == '万':
            data['持股数量2'][i] = float(tmp[:-1]) * 10000
        elif tmp[-1] == '亿':
            data['持股数量2'][i] = float(tmp[:-1]) * 100000000
        else:
            pass
    except:
        pass

data['持仓变动'] = data['持股数量2'].astype('float') - data['持股数量1'].astype('float')
data['新开仓'] = (data['持股数量1'].isnull()) & (~data['持股数量2'].isnull())
data['新清仓'] = (data['持股数量2'].isnull()) & (~data['持股数量1'].isnull())

# 新开仓一列为True则为新开仓
print('新开仓的机构和股票：')
print(data[data['新开仓']== True])

# 新清仓一列为True则为新清仓
print('新清仓的机构和股票：')
print(data[data['新清仓']== True])

# 持仓变动为这一列：'持仓变动（万）'
#data['持仓变动（万）']

#若要导出数据，执行此行
data.to_excel(r'E:\PycharmProjects\zhengquan\result.xlsx')



