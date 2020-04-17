import tabula
import numpy as np
import pandas as pd
import re

pfile = r"C:/Users/86151/Desktop/pdfbug/deala/PDFdownload1/中国中铁股份有限公司2020年度第一期中期票据募集说明书.pdf"

df = tabula.read_pdf(pfile, pages="183-186", stream=True)
patterns = [r"[\u4E00-\u9FA5]+",r"[1-9]\d*\.\d*|0\.\d*[1-9]\d*$"]

data_list = []
for df_table in df:
    table_list = []
    df_table.fillna("", inplace=True)
    table_list.append(list(df_table.head()))
    array_table = np.array(df_table)
    table_list += array_table.tolist()
    data_list += table_list
    
for data in data_list:
    for info in data[:-2]:
        if re.match(patterns[0], str(info)) and \
            re.match(patterns[1], str(data[data.index(info) + 1]).replace(',', '')) and \
            re.match(patterns[1], str(data[data.index(info) + 2]).replace(',', '')):
            bankname = info
            credit = max(float(re.findall(patterns[1], str(data[data.index(info) + 1]).replace(',', ''))[0]), \
                float(re.findall(patterns[1], str(data[data.index(info) + 2]).replace(',', ''))[0]))
            used = min(float(re.findall(patterns[1], str(data[data.index(info) + 1]).replace(',', ''))[0]), \
                float(re.findall(patterns[1], str(data[data.index(info) + 2]).replace(',', ''))[0])) 
            print("银行名称", bankname + "  授信额度:%.2f" % credit + "  已用额度:%.2f" % used + "  剩余额度:%.2f" % (credit - used))
            print("================\n")
