import sqlite3
import sys

class OperateTable(object):

    def __init__(self):
        self.conn = sqlite3.connect('pdftables.sqlite')
        self.cur = self.conn.cursor()
    
    def  create_table(self):
        sql_bank = '''CREATE TABLE myapp_credit_info (
            id integer primary key Autoincrement not null,
            bank text not null,
            credit decimal(15,2) not null,
            used decimal(15,2) not null,
            company_id integer not null,
            FOREIGN KEY (company_id) REFERENCES myapp_company_info(id))
            '''

        sql_company = '''CREATE TABLE myapp_company_info (
            id integer primary key Autoincrement not null,
            company text not null,
            units text not null)
            '''
        
        self.cur.execute(sql_bank)
        self.cur.execute(sql_company)
    
    def drop_table(self):
        self.cur.execute('drop table myapp_credit_info')
        self.cur.execute('drop table myapp_company_info')


if __name__ == '__main__':
    app = OperateTable()
    argv = sys.argv[1]

    if argv == 'createtable':
        app.create_table()
    elif argv == 'droptable':
        app.drop_table()
    else:
        print("输入参数必须为createtable或droptable其中之一")
        raise ValueError 