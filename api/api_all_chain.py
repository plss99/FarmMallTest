# 全链路接口-以用户购买苹果为例
import re

import requests

import api


class ApiAllChain:
    # 初始化
    def __init__(self):
        # 用户session：注册、搜索、购买、结算、查看订单
        self.user_session = requests.Session()
        # 管理员session：登录后台、修改订单状态
        self.admin_session = requests.Session()
        # 搜索商品url
        self.url_search = api.host + "/"
        # 结算订单url
        self.url_order = api.host + "/checkout"
        # 管理员登录url
        self.url_admin_login = api.host + "/admin"
        self.product_id = None
        self.order_id = None

    # 1.用户登录
    def api_01_login(self, username=None, password=None):
        if username is None:
            username = api.default_username
        if password is None:
            password = api.default_password
        login_url = api.host + "/login"
        data = {
            "username": username,
            "password": password,
        }
        return self.user_session.post(login_url, data=data)

    # 2.搜索商品，从响应体中提取商品ID
    def api_02_search(self, keyword=None):
        if keyword is None:
            keyword = api.default_keyword
        params = {"keyword": keyword}
        resp = self.user_session.get(self.url_search, params=params)
        match = re.search(r'/product/(\d+)', resp.text)
        if not match:
            raise Exception(f"搜索 '{keyword}' 未找到商品")
        self.product_id = int(match.group(1))
        return self.product_id

    # 3.加入购物车
    def api_03_buy(self):
        url = api.host + f"/product/{self.product_id}/buy"
        return self.user_session.post(url)

    # 4.结算订单，从响应中提取订单ID
    def api_04_order(self, receiver_name=None, phone=None, address=None, remark=""):
        if receiver_name is None:
            receiver_name = api.default_receiver_name
        if phone is None:
            phone = api.default_phone
        if address is None:
            address = api.default_address
        data = {
            "receiver_name": receiver_name,
            "phone": phone,
            "address": address,
            "remark": remark,
        }
        resp = self.user_session.post(self.url_order, data=data, allow_redirects=False)
        match = re.search(r'/orders/(\d+)', resp.headers.get("Location", ""))
        if match:
            self.order_id = int(match.group(1))
        return resp

    # 5.管理员登录
    def api_05_admin_login(self, username=None, password=None):
        if username is None:
            username = api.default_admin_username
        if password is None:
            password = api.default_admin_password
        login_url = api.host + "/login"
        data = {
            "username": username,
            "password": password,
        }
        self.admin_session.post(login_url, data=data)
        return self.admin_session.get(self.url_admin_login)

    # 6.管理员修改订单状态
    def api_06_admin_update(self, order_id=None, status=None):
        if order_id is None:
            order_id = self.order_id
        if status is None:
            status = api.default_order_status
        url = api.host + f"/admin/orders/{order_id}/status"
        data = {"status": status}
        return self.admin_session.post(url, data=data)

    # 7.用户查看订单状态
    def api_07_user_view(self, order_id=None):
        if order_id is None:
            order_id = self.order_id
        url = api.host + f"/orders/{order_id}"
        return self.user_session.get(url=url)

    # 组合业务方法
    def api_all_chain(self):
        self.api_01_login()
        self.api_02_search()
        self.api_03_buy()
        self.api_04_order()
        self.api_05_admin_login()
        self.api_06_admin_update()
        return self.api_07_user_view()