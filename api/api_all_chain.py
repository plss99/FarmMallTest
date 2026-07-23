# 全链路接口-以用户购买苹果为例
import re
import requests
from loguru import logger

import api


class ApiAllChain:
    def __init__(self):
        self.user_session = requests.Session()
        self.admin_session = requests.Session()
        self.url_search = api.host + "/"
        self.url_order = api.host + "/checkout"
        self.url_admin_login = api.host + "/admin"
        self.product_id = None
        self.order_id = None

    def api_01_login(self, username=None, password=None):
        username = username or api.default_username
        password = password or api.default_password
        login_url = api.host + "/login"
        data = {"username": username, "password": password}
        logger.info("全链路-用户登录 | POST {} | data={}", login_url, data)
        resp = self.user_session.post(login_url, data=data)
        logger.info("全链路-用户登录 | 响应状态码: {}", resp.status_code)
        return resp

    def api_02_search(self, keyword=None):
        keyword = keyword or api.default_keyword
        params = {"keyword": keyword}
        logger.info("全链路-搜索商品 | GET {} | keyword={}", self.url_search, keyword)
        resp = self.user_session.get(self.url_search, params=params)
        logger.info("全链路-搜索商品 | 响应状态码: {}", resp.status_code)
        match = re.search(r'/product/(\d+)', resp.text)
        if not match:
            raise Exception(f"搜索 '{keyword}' 未找到商品")
        self.product_id = int(match.group(1))
        logger.info("全链路-搜索商品 | 提取到 product_id={}", self.product_id)
        return self.product_id

    def api_03_buy(self):
        url = api.host + f"/product/{self.product_id}/buy"
        logger.info("全链路-加入购物车 | POST {} | product_id={}", url, self.product_id)
        resp = self.user_session.post(url)
        logger.info("全链路-加入购物车 | 响应状态码: {}", resp.status_code)
        return resp

    def api_04_order(self, receiver_name=None, phone=None, address=None, remark=""):
        receiver_name = receiver_name or api.default_receiver_name
        phone = phone or api.default_phone
        address = address or api.default_address
        data = {
            "receiver_name": receiver_name,
            "phone": phone,
            "address": address,
            "remark": remark,
        }
        logger.info("全链路-提交订单 | POST {} | data={}", self.url_order, data)
        resp = self.user_session.post(self.url_order, data=data, allow_redirects=False)
        logger.info("全链路-提交订单 | 响应状态码: {}", resp.status_code)
        match = re.search(r'/orders/(\d+)', resp.headers.get("Location", ""))
        if match:
            self.order_id = int(match.group(1))
            logger.info("全链路-提交订单 | 提取到 order_id={}", self.order_id)
        return resp

    def api_05_admin_login(self, username=None, password=None):
        username = username or api.default_admin_username
        password = password or api.default_admin_password
        login_url = api.host + "/login"
        data = {"username": username, "password": password}
        logger.info("全链路-管理员登录 | POST {} | data={}", login_url, data)
        self.admin_session.post(login_url, data=data)
        logger.info("全链路-管理员访问后台 | GET {}", self.url_admin_login)
        resp = self.admin_session.get(self.url_admin_login)
        logger.info("全链路-管理员访问后台 | 响应状态码: {}", resp.status_code)
        return resp

    def api_06_admin_update(self, order_id=None, status=None):
        order_id = order_id or self.order_id
        status = status or api.default_order_status
        url = api.host + f"/admin/orders/{order_id}/status"
        data = {"status": status}
        logger.info("全链路-修改订单状态 | POST {} | data={}", url, data)
        resp = self.admin_session.post(url, data=data)
        logger.info("全链路-修改订单状态 | 响应状态码: {}", resp.status_code)
        return resp

    def api_07_user_view(self, order_id=None):
        order_id = order_id or self.order_id
        url = api.host + f"/orders/{order_id}"
        logger.info("全链路-查看订单状态 | GET {}", url)
        resp = self.user_session.get(url=url)
        logger.info("全链路-查看订单状态 | 响应状态码: {}", resp.status_code)
        return resp

    def api_all_chain(self):
        self.api_01_login()
        self.api_02_search()
        self.api_03_buy()
        self.api_04_order()
        self.api_05_admin_login()
        self.api_06_admin_update()
        return self.api_07_user_view()