# 管理员模块接口
import requests

import api


class ApiAdmin:
    # 初始化
    def __init__(self, session=None,product_id=None,order_id=None):
        self.product_id = product_id if product_id is not None else api.product_id
        self.order_id = order_id if order_id is not None else api.order_id
        # 管理员正常访问url
        self.url_login = api.host + "/admin"
        # 管理员强制上下架商品url
        self.url_coerce = api.host + f"/admin/product/{self.product_id}/toggle"
        # 管理员修改订单状态url
        self.url_status = api.host + f"/admin/orders/{self.order_id}/status"
        # 管理员查看所有用户url
        self.url_users = api.host + "/admin/users"
        # 创建一个session对象来自动管理cookie，支持外部传入已登录的session
        self.session = session if session is not None else requests.Session()
    # 管理员正常访问接口
    def api_admin_login(self, username="admin", password="REDACTED"):
        login_url = api.host + "/login"
        data = {
            "username": username,
            "password": password
        }
        self.session.post(url=login_url, data=data)
        return self.session.get(url=self.url_login)
    # 管理员强制上下架商品接口
    def api_admin_coerce(self):
        return self.session.post(url=self.url_coerce)
    # 管理员修改订单状态接口
    def api_admin_status(self, status):
        data = {"status": status}
        return self.session.post(url=self.url_status, data=data)
    # 管理员查看所有用户接口
    def api_admin_users(self):
        return self.session.get(url=self.url_users )