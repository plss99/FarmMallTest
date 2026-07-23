# 购物车模块接口
import requests
from loguru import logger

import api


class ApiCart:
    def __init__(self, session=None, product_id=None):
        self.product_id = product_id if product_id is not None else api.product_id
        self.url_cart_add = api.host + f"/product/{self.product_id}/buy"
        self.url_cart_list = api.host + "/cart"
        self.url_cart_remove = api.host + f"/cart/product/{self.product_id}/remove"
        self.session = session if session is not None else requests.Session()

    def api_cart_add(self):
        logger.info("加入购物车 | POST {} | product_id={}", self.url_cart_add, self.product_id)
        resp = self.session.post(self.url_cart_add)
        logger.info("加入购物车 | 响应状态码: {} | 响应内容: {}", resp.status_code, resp.text[:200])
        return resp

    def api_cart_list(self):
        logger.info("查看购物车 | GET {}", self.url_cart_list)
        resp = self.session.get(self.url_cart_list)
        logger.info("查看购物车 | 响应状态码: {}", resp.status_code)
        return resp

    def api_cart_remove(self):
        logger.info("移除购物车 | POST {} | product_id={}", self.url_cart_remove, self.product_id)
        resp = self.session.post(self.url_cart_remove)
        logger.info("移除购物车 | 响应状态码: {} | 响应内容: {}", resp.status_code, resp.text[:200])
        return resp