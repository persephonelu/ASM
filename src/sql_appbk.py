#!/usr/bin/env python
#coding=utf-8
#功能，appbk数据库访问
#输入数据库表和sql命令，返回结果
import os
import sys
import time
import json
import MySQLdb
reload(sys)
sys.setdefaultencoding('utf-8')

g_db_host = "rm-bp1w81w3y5da24apeo.mysql.rds.aliyuncs.com" #线上机器
#g_db_host = "rds5ytuekh6hv4k36g4n.mysql.rds.aliyuncs.com"
g_db_user = "rootali"
g_db_pw = "Rootali1"
g_db_name = "appbk" #数据库名

"""
功能：连接数据
"""
def connect_db():
    db = ''
    try:
        db = MySQLdb.connect(host = g_db_host, user=g_db_user, passwd = g_db_pw, db = g_db_name, charset='utf8',connect_timeout=10)
    except Exception as e:
        return '-1'

    return db

"""
功能：执行mysql命令，返回结果
输入：sql_com, sql命令
返回：mysql查询结果数组
"""
def mysql_com(sql_com):
    #连接数据库
    for i in range(3):
        db = connect_db()

        if db:
            break
        else:
            i = i + 1

    result = []
    if db != '-1':
        #执行mysql命令
        #cursor = db.cursor()
        cursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute(sql_com)
        result = cursor.fetchall()
        db.commit()
        db.close()
    return result

if __name__=="__main__":
    #sql_com ='select a.app_id from (select distinct(app_id) from aso_search_result_new) as a  left join app_info on a.app_id = app_info.app_id where app_info.app_id is null'
    #sql_com ="update gamearts_user set firstname='ella' where email='ella.smith@sjsu.edu'"
    sql_com = "select * from asm_campaign where email='chenkexin@youyue-inc.com' limit 10"
    result = mysql_com(sql_com)
    for ret in result:
        print ret['id']
    #for row in result:
    #    print row[0]
        #print row[0],'\t',row[1],'\t',row[2],'\t',row[3],'\t',row[4]
