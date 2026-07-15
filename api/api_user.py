# 用户端接口
import requests

import api


class ApiUser:
    # 1.初始化
    def __init__(self):
        # 登录接口url
        self.url_login = api.host + "/login"
        # 注册接口url
        self.url_reg = api.host + "/register"
        # 退出登录url
        self.url_logout = api.host + "/logout"
        # 创建一个session对象来自动管理cookie
        self.session = requests.Session()
    # 2.登录接口
    def api_user_login(self,username,password):
        # 定义请求数据
        data = {
            "username":username,
            "password":password
        }
        # 调用post方法--返回响应数据
        return self.session.post(url=self.url_login,data=data)
    # 3.注册接口
    def api_user_reg(self,r_username,r_password):
        # 定义请求数据
        data = {
            "username":r_username,
            "password":r_password,
            "confirm":r_password
        }
        # 调用post方法--返回响应数据
        return self.session.post(url=self.url_reg,data=data)
    # 4.退出登录接口
    def api_user_logout(self):
        return self.session.get(url=self.url_logout)
    # 5.成功登录
    def api_user_login_success(self):
        # 定义请求数据
        data = {
            "username": "小农户",
            "password": "REDACTED"
        }
        # 调用post方法--返回响应数据
        return self.session.post(url=self.url_login, data=data)