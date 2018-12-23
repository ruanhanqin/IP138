#!/usr/bin/env python
# encoding: utf-8


"""
@author: Hanqin Ruan
@desc:根据手机号段码从网站查询该号段码所属省份及运营商
url:http://www.ip138.com:8080/pipsearch.asp?mobile=1364084&action=mobile

网上查询到的数据格式：
1364084 测吉凶(新)
广东 广州市
移动预付费卡
020
510000 更详细的..
"""


import pandas as pd
from urllib import request, parse
from bs4 import BeautifulSoup
import re

Pro_Code = {  # 省份代码
    '北京': '11',
    '天津': '12',
    '河北': '13',
    '山西': '14',
    '内蒙古': '15',
    '辽宁': '21',
    '吉林': '22',
    '黑龙江': '23',
    '上海': '31',
    '江苏': '32',
    '浙江': '33',
    '安徽': '34',
    '福建': '35',
    '江西': '36',
    '山东': '37',
    '河南': '41',
    '湖北': '42',
    '湖南': '43',
    '广东': '44',
    '广西': '45',
    '海南': '46',
    '重庆': '50',
    '四川': '51',
    '贵州': '52',
    '云南': '53',
    '西藏': '54',
    '陕西': '61',
    '甘肃': '62',
    '青海': '63',
    '宁夏': '64',
    '新疆': '65',
    '台湾': '71',
    '香港': '81',
    '澳门': '82'
}
Mobil_Code = {  # 运营商代码
    '移动': '1',
    '联通': '2',
    '电信': '3'
}


def get_area_from_code(data_frame):
    for index in data_frame.index:
        code = str(data_frame.loc[index].values[0:][0])  # 获取DataFrame 里每一行的号码
        url = 'http://www.ip138.com:8080/search.asp?mobile={}&action=mobile'.format(parse.quote(code))  # 构造查询url
        response = request.urlopen(url)
        html_doc = response.read().decode('gb2312')  # 转码
        soup = BeautifulSoup(html_doc, 'html.parser')
        pattern_code = re.compile('\d+')
        area_code_string = soup.select('.tdc2')[0].get_text()  # 根据class标签获取
        area_code = pattern_code.search(area_code_string).group()  # 查找号码正则
        province_string = soup.select('.tdc2')[1].get_text()
        if re.split(r'\s+', province_string)[0] == '未知' or re.split(r'\s+', province_string)[0] == '':  # 省份未知或为空时，不保存
            continue
        else:
            province = re.split(r'\s+', province_string)[0]
            mobil_corp_string = soup.select('.tdc2')[2].get_text()
            patter_mobile = re.compile(r'移动|联通|电信')
            mobil_corp = patter_mobile.search(mobil_corp_string).group()
        recoder = area_code + '   ' + province + '   ' + mobil_corp  # 按号段，省份，运营商 组合成一条记录
        recoder_list.append(recoder)  # 加入列表
    return recoder_list


def replace_to_code():  # 省份，运营商代码转换
    with open('Recoder_File.txt', 'r') as fp:
        strings = fp.read()
        for pro in Pro_Code:
            if re.search(pro, strings):
                strings = strings.replace(re.search(pro, strings).group(0), Pro_Code[pro])
        for crop in Mobil_Code:
            if re.search(crop, strings):
                strings = strings.replace(re.search(crop, strings).group(0), Mobil_Code[crop])
    return strings


def create_sql(sql):  # 生成sql语句
    sql_str_list = []
    with open('Recoder_File_replace.txt', 'r') as fp:
        line = fp.readline()
        while line:
            recoder = line.split()  # 转成列表
            sql_str = sql.format(recoder[0], recoder[0], recoder[1], recoder[2])
            sql_str_list.append(sql_str)
            line = fp.readline()
    return sql_str_list


if __name__ == "__main__":
    recoder_list = []  # 保存查询结果列表
    sql_List = []  # 保存sql语句列表
    sep = '\n'  # 结果记录分隔换行符
    sql = """
    INSERT INTO TB_USER_ROUTE_RULE(RULE_ID,RULE_NAME,SECTION_NO,STATUS,INSERT_TIME,INSERT_STAFF_ID,LAST_MOD_TIME,
    LAST_MOD_STAFF_ID,PROVINCE,MOBIL_CORP)VALUES(sys_guid(),'{}','{}','1',sysdate,'rhq',sysdate,'rhq','{}','{}');
    """
    df = pd.read_excel('AreaCode.xlsx', usecols=0)  # 读取号段码文件（EXCEL格式）DataFrame
    recoder_list = get_area_from_code(df)
    with open('Recoder_File.txt', 'w') as fp:
        fp.write(sep.join(recoder_list))

    string = replace_to_code()
    with open('Recoder_File_replace.txt', 'w') as fp:
        fp.write(string)

    sql_list = create_sql(sql)
    with open('Recoder_File_sql.sql', 'w') as fp:
        fp.write(sep.join(sql_list))
