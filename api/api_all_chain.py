# 全链路接口-以用户购买苹果为例
import requests
from loguru import logger
from tool.get_db_info import GetDBInfo
import api


class ApiAllChain:
    def __init__(self, session=None, product_id=None, order_id=None):
        self.session = session if session is not None else requests.Session()
        self.url_reg = api.host + "/register"
        self.url_search = api.host + "/"
        self.url_order = api.host + "/checkout"
        self.login_url = api.host + "/login"
        self.product_id = product_id if product_id is not None else api.product_id
        self.order_id = order_id if order_id is not None else api.order_id
        self.info = GetDBInfo()
        self.admin_session = requests.Session()

    def api_00_reg(self):
        data = {
            "username": api.default_username,
            "password": api.default_password,
            "confirm": api.default_password
        }
        logger.info(f"全链路-用户注册 | POST {self.url_reg} | username={data['username']}")
        resp = self.session.post(self.url_reg, data=data)
        return resp

    def api_01_login(self):
        data = {"username": api.default_username, "password": api.default_password}
        logger.info(f"全链路-用户登录 | POST {self.login_url} | username={data['username']}")
        resp = self.session.post(self.login_url, data=data)
        logger.info(f"全链路-用户登录 | 响应状态码: {resp.status_code}")
        return resp

    def api_02_search(self,keyword=None):
        keyword = keyword or api.default_keyword
        params = {"keyword": keyword}
        logger.info(f"全链路-搜索商品 | GET {self.url_search} | keyword={keyword}")
        resp = self.session.get(self.url_search, params=params)
        logger.info(f"全链路-搜索商品 | 响应状态码: {resp.status_code}")
        self.product_id = self.info.get_product_id_by_keyword(keyword)
        logger.info(f"全链路-搜索商品 | 提取到 product_id={self.product_id}")
        return self.product_id

    def api_03_buy(self):
        url = api.host + f"/product/{self.product_id}/buy"
        logger.info(f"全链路-加入购物车 | POST {url} | product_id={self.product_id}")
        resp = self.session.post(url)
        logger.info(f"全链路-加入购物车 | 响应状态码: {resp.status_code}")
        return resp, self.order_id

    def api_04_order(self):
        data = {
            "receiver_name": api.default_receiver_name,
            "phone": api.default_phone,
            "address": api.default_address,
            "remark": "",
        }
        logger.info(f"全链路-提交订单 | POST {self.url_order} | data={data}")
        resp = self.session.post(url=self.url_order, data=data)
        logger.info(f"全链路-提交订单 | 响应状态码: {resp.status_code}")
        location = resp.headers.get("Location", "")
        logger.info(f"全链路-提交订单 | Location: {location}")

        self.order_id = self.info.get_order_id(api.default_username)
        logger.info(f"全链路-提交订单 | 提取到 order_id={self.order_id}")
        return resp, self.order_id

    def api_05_admin_login(self):
        logger.info(f"全链路-管理员登录 | POST {self.login_url}")
        data = {"username": api.default_admin_username, "password": api.default_admin_password}
        resp = self.admin_session.post(self.login_url, data=data)
        logger.info(f"全链路-管理员登录 | 响应状态码: {resp.status_code}")
        return resp

    def api_06_admin_update(self):
        url = api.host + f"/admin/orders/{self.order_id}/status"
        data = {"status": api.default_order_status}
        logger.info(f"全链路-修改订单状态 | POST {url} | data={data}")
        resp = self.admin_session.post(url, data=data)
        logger.info(f"全链路-修改订单状态 | 响应状态码: {resp.status_code}")
        return resp

    def api_07_user_view(self):
        url = api.host + f"/orders/{self.order_id}"
        logger.info(f"全链路-查看订单状态 | GET {url}")
        resp = self.session.get(url=url)
        logger.info(f"全链路-查看订单状态 | 响应状态码: {resp.status_code}")
        return resp

    def api_all_chain(self):
        self.api_00_reg()
        self.api_01_login()
        self.api_02_search()
        self.api_03_buy()
        self.api_04_order()
        self.api_05_admin_login()
        self.api_06_admin_update()
        return self.api_07_user_view()