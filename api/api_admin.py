# 管理员模块接口
import requests
from loguru import logger

import api


class ApiAdmin:
    def __init__(self, session=None, product_id=None, order_id=None):
        self.product_id = product_id if product_id is not None else api.product_id
        self.order_id = order_id if order_id is not None else api.order_id
        self.url_login = api.host + "/admin"
        self.url_coerce = api.host + f"/admin/product/{self.product_id}/toggle"
        self.url_status = api.host + f"/admin/orders/{self.order_id}/status"
        self.url_users = api.host + "/admin/users"
        self.session = session if session is not None else requests.Session()

    def api_admin_login(self, username="admin", password="REDACTED"):
        login_url = api.host + "/login"
        data = {"username": username, "password": password}
        logger.info("管理员登录 | POST {} | data={}", login_url, data)
        self.session.post(url=login_url, data=data)
        logger.info("管理员访问后台 | GET {}", self.url_login)
        resp = self.session.get(url=self.url_login)
        logger.info("管理员访问后台 | 响应状态码: {}", resp.status_code)
        return resp

    def api_admin_coerce(self):
        logger.info("强制上下架 | POST {} | product_id={}", self.url_coerce, self.product_id)
        resp = self.session.post(url=self.url_coerce)
        logger.info("强制上下架 | 响应状态码: {}", resp.status_code)
        return resp

    def api_admin_status(self, status):
        data = {"status": status}
        logger.info("修改订单状态 | POST {} | data={}", self.url_status, data)
        resp = self.session.post(url=self.url_status, data=data)
        logger.info("修改订单状态 | 响应状态码: {}", resp.status_code)
        return resp

    def api_admin_users(self):
        logger.info("查看用户列表 | GET {}", self.url_users)
        resp = self.session.get(url=self.url_users)
        logger.info("查看用户列表 | 响应状态码: {}", resp.status_code)
        return resp