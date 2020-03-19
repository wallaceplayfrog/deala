import tabula
import pdfminer
import pdfplumber

df = tabula.read_pdf(r"C:\Users\86151\Desktop\pdfbug\pdf\国家电网有限公司2020年度第一期超短期融资券募集说明书.pdf", encoding="gbk", pages="all")
print(df)
