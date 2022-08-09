# 项目描述

用来汉化暗黑地牢Mod的工具，将xxx.string_table.xml转为python对象进行种种操作。

## 使用方法
### 第一步，配置百度翻译api
进入https://api.fanyi.baidu.com/manage/developer
拿到APP ID与密钥并更改模块内变量
```python
app_id = '你的APP ID'
key = '你的密钥'
```
### 第二步，开始翻译
```python
import dd_tool  # 引入工具模块

# xml的file对象
xml_file = open('toy_trinket.string_table.xml', encoding='utf-8')
# 获取到ChineseStringTable对象
c = dd_tool.ChineseStringTable(xml_file)
# 同过parse函数，拿到多个Entry对象，调用Entry对象函数来进行翻译
for i in c.parse():  # type: dd_tool.Entry
    print(i.origin_text)  # 未翻译的文本
    print(i.translate_text)  # 自动翻译的文本
    t = input('翻译（回车自动翻译，加号保留原文本）：')
    if t == '':
        i.translate_auto()  # 自动翻译
    elif t == '+':
        i.no_translate()  # 不翻译
    else:
        i.translate_with_text(t)  # 自定义翻译
    print()
c.write_xml('aaa.string_table.xml')  # 写入文件
xml_file.close()
```
