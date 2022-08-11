"""
@author: Stear

描述：该模块将xxx.string_table.xml类型的文件转为python对象，进行翻译操作.

依赖第三方库：xmltodict.

使用方法：
c = dd_tool.ChineseStringTable(open('toy_trinket.string_table.xml', encoding='utf-8'))
    for i in c.parse():  # type: dd_tool.Entry
        print(i.origin_text)
        print(i.translate_text)
        t = input('翻译：')
        if t == '':
            i.translate_auto()
        elif t == '+':
            i.no_translate()
        else:
            i.translate_with_text(t)
        print()

    c.write_xml('a.xml')
"""

import hashlib
import json
import random
import re
import time

import requests
import xmltodict

app_id = '你的APP ID'
key = '你的密钥'


def str2md5(string):
    """
    对字符串进行md5加密
    :param string: 待加密字符串
    :return: 加密后的字符串
    """
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


def translate(q, l_from='en', l_to='zh'):
    """
    调用百度翻译接口
    :param q: 待翻译文本
    :param l_from: 源文本语种
    :param l_to: 目标语种
    :return: 翻译结果，0为翻译失败
    """
    global app_id
    global key
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    salt = str(random.randint(1000000, 9999999))
    sign = str2md5(app_id + q + salt + key)
    url += '?q=' + q + '&from=' + l_from + '&to=' + l_to + '&appid=' + app_id + '&salt=' + salt + '&sign=' + sign

    j_r = json.loads(requests.get(url).text)
    if 'error_code' in j_r:
        return 0
    return j_r['trans_result'][0]['dst']


def replace_with_sign(string: str):
    """
    颜色代码不需要翻译，暂时替换颜色代码
    :param string: 待替换字符串
    :return: 元组（替换过的字符串，替换下来的字符串用于回填）
    """
    re_str_list = re.findall('{.*?}', string)
    if re_str_list:
        print('出现颜色代码：' + string)
    for item in re_str_list:
        string = string.replace(item, ' 010 ')
    return string, re_str_list


def put_sign(string, re_str_list: list):
    """
    对颜色代码替换过的字符串回填
    :param string: 待回填字符串
    :param re_str_list: 回填内容，list类型
    :return:
    """
    result = re.findall('010', string)
    for index, item in enumerate(result):
        string = string.replace('010', re_str_list[index])
    return string


class Entry:
    """
    实体类，存储一条待翻译entr标签
    """

    def __init__(self, entry: dict, translate_text: str):
        self.__entry = entry
        self.__origin_text = entry['#text']
        self.__translate_text = translate_text

    @property
    def translate_text(self):
        return self.__translate_text

    @property
    def origin_text(self):
        return self.__origin_text

    def translate_with_text(self, text: str):
        """
        用户输入翻译
        :param text: 翻译后的文本
        """
        self.__entry['#text'] = '<![CDATA[' + text + ']]>'

    def translate_auto(self):
        """
        使用用百度自动翻译
        """
        self.__entry['#text'] = '<![CDATA[' + self.translate_text + ']]>'

    def no_translate(self):
        """
        不翻译，保留原有内容
        :return:
        """
        self.__entry['#text'] = '<![CDATA[' + self.__origin_text + ']]>'


class ChineseStringTable:
    """工具类，处理string_table.xml"""

    def __init__(self, file):
        """
        初始化方法，将xml解析成ChineseStringTable对象
        :param file: xml形成的file对象
        """
        if hasattr(file, 'read'):
            self._doc = xmltodict.parse(file.read())
        else:
            raise Exception('传入的非file对象：', type(file))

        self.__list_origin_entry = []  # 未翻译的entry节点列表
        self.__list_result_entry = []  # 翻译后的Entry对象列表
        self.__parse_list_entry()

    def __get_chinese_node(self):
        """
        获取xml中的id=‘schinese’的language节点
        :return: dict:language
        """
        if 'root' in self._doc:
            for i in self._doc['root']:
                if i != 'language':
                    raise Exception('root的子标签必须都为language标签')
            else:
                for language in self._doc['root']['language']:
                    if language['@id'] == 'schinese':
                        return language
                else:
                    raise Exception('没有id="schinese"的language标签')
        raise Exception('根标签必须为root标签')

    def __parse_list_entry(self):
        """
        把language里的每个entry放到_list_origin_entry
        """
        d = self.__get_chinese_node()

        for entry in d['entry']:
            if '#text' in entry:
                self.__list_origin_entry.append(entry)
            else:
                continue

    def parse(self):
        """
        核心函数，翻译与封装
        :return: list of Entry
        """
        for i in self.__list_origin_entry:
            text = i['#text']  # entry内的文本
            text, re_str_list = replace_with_sign(text)  # 暂时清除与回填颜色代码
            text = translate(text)  # 百度翻译

            if text:  # text!=0,翻译成功
                text = put_sign(text, re_str_list)  # 颜色代码回填
                self.__list_result_entry.append(Entry(i, text))  # 存储翻译过的Entry
            else:
                print('翻译出错：' + i['#text'])
                self.__list_result_entry.append(Entry(i, '翻译出错'))
            time.sleep(0.11)  # 百度接口一秒最多请求十次
        return self.__list_result_entry

    def write_xml(self, path, pretty=True):
        """
        写入xml文件
        :param path: 文件路径与文件名
        :param pretty: 是否格式化，默认True
        """
        r = xmltodict.unparse(self._doc, pretty=pretty)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(r.replace('&lt;', '<').replace('&gt;', '>'))

    def get_xml(self, pretty=True):
        """
        获得xml字符串
        :param pretty: 是否格式化，默认True
        :return: 字符串
        """
        return xmltodict.unparse(self._doc, pretty=pretty)

