# 定义函数
import os
# pyyaml
import yaml

from config import BASE_PATH


def read_yaml(filename):
    file_path = BASE_PATH + os.sep + "data" + os.sep + filename
    # 定义空列表 组装测试数据
    arrs = []
    # 获取文件流
    with open(file_path,"r",encoding="utf-8") as f:
        # 遍历  调用yaml.safe_load().values()方法
        for datas in yaml.safe_load(f).values():
            arrs.append(tuple(datas.values()))
    # 返回结果
    return arrs