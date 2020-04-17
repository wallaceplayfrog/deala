import pdfplumber
import pandas as pd
import numpy as np
import re
import os
import tabula
import sqlite3
import time

'''
在爬取出的pdf文件中，通过目录分析可得到发行人银行授信情况都在
[发行人资信情况、企业资信情况、公司资信状况]章节
[]子目录
在目录获取到资信情况的页码后，提取相应页码的授信情况表格
'''
indexs = ["发行人资信情况", "发行人资信状况", "企业资信情况", "公司资信状况", "资信状况", "资信情况"]

def get_index_page_number():
    for page in pdf.pages:
        # print("\n处理页数：", page.page_number)
        # print("\n", page.extract_text())
        if re.match(".*?目[ ]*录", page.extract_text(), flags=re.S):
            return page.page_number


def get_table_ch_number():
    for page in pdf.pages[:10]:
        if page.extract_text():
            textlist = page.extract_text().split('\n')
            for textline in textlist:
                if textline is not None and isin_indexs(textline):
                    if re.match(r"\d+", textline):
                        return int(re.sub(r'[\D]+', '', textline))
                    else: 
                        textline = textlist[textlist.index(textline) + 1]
                        return int(re.sub(r'[\D]+', '', textline))
    return False


def isin_indexs(line):
    for index in indexs:
        if index in line:
            return True
    return False


def get_table_page_number(table_ch_number):
    for page in pdf.pages[table_ch_number - 1:]:
        pagecontent = page.extract_text()
        # print(pagecontent)
        if "授信情况" in pagecontent:
            return page.page_number
        elif "银行授信" in pagecontent:
            return page.page_number
        elif "授信" in pagecontent:
            return page.page_number
    return False


def get_table(filepath, table_page_number):
    '''
    for page in pdf.pages[table_page_number - 1:table_page_number + 2]:
        tables = page.extract_tables()
        if tables:
            for table in tables:
                for line in table:
                    print(line)
                print("\n\n")
    '''
    pages = str(table_page_number) + "-" + str(table_page_number + 2)
    df = tabula.read_pdf(filepath, pages=pages, stream=True)
    return df


def clean_table(df):
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
                info = "银行名称:" + bankname + "  授信额度:%.2f" % credit + "  已用额度:%.2f" % used + "  剩余额度:%.2f" % (credit - used) + "\n"
                log_file.write(info)
                insert_credit_info(cur, bankname, credit, used)


def get_units(table_page_number):
    for page in pdf.pages[table_page_number - 1:table_page_number + 2]:
        if "单位：万元" in page.extract_text():
            return "万元"
        elif "单位：亿元" in page.extract_text():
            return "亿元"
    return False


def insert_company_info(cursor, company, units):
    sql = "insert into company_info (company, units) values ('%s', '%s')" % (company, units)
    cursor.execute(sql)
    conn.commit()
    


def insert_credit_info(cursor, bank, credit, used):
    sql1 = "select id from company_info where company = '%s'" % company
    c = cursor.execute(sql1)
    company_id = c.fetchone()
    sql = "insert into credit_info (bank, credit, uesd, company) values ('%s', '%.2f', '%.2f', '%d')" % (bank, credit, used, int(company_id[0]))
    cursor.execute(sql)
    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect('pdftables.sqlite')
    cur = conn.cursor()


    file_path = r"C:/Users/86151/Desktop/pdfbug/deala/PDFdownload/"
    filelist = os.listdir(file_path)
    log_file = open('mylog.log', 'w', encoding='utf-8')
    
    for each_file in filelist:
        
        log_file.write("================================\n处理文件：%s\n" % each_file)
        log_file.write("开始时间：%s\n" % time.ctime())

        company = each_file
        company = company.replace(".pdf", "")  # 公司名

        each_file = file_path + each_file
        pdf = pdfplumber.open(each_file)
        table_ch_number = get_table_ch_number()
        if table_ch_number:
            log_file.write("表格所在章节数为：%d\n" % table_ch_number)
            table_page_number = get_table_page_number(table_ch_number)
            if table_page_number:
                log_file.write("表格所在页数为：%d\n" % table_page_number)
                units = get_units(table_page_number)
                if units:
                    log_file.write("计量单位为：%s\n" % units)
                    insert_company_info(cur, company, units)
                else:
                    log_file.write("计量单位获取失败\n")
                log_file.write("目标表格提取\n")
                df = get_table(each_file, table_page_number)
                log_file.write("清洗数据\n")
                clean_table(df)
            else:
                log_file.write("未找到表格所在页数\n")
        else:
            log_file.write("未找到表格章节页数\n")
        
        log_file.write("处理完成\n")
        log_file.write("结束时间：%s\n" % time.ctime())
    log_file.close()
    conn.close()