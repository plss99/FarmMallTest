# 商品模块接口
import requests
from loguru import logger

import api


class ApiProd:
    def __init__(self, session=None, product_id=None, seller_id=None):
        self.product_id = product_id if product_id is not None else api.product_id
        self.seller_id = seller_id if seller_id is not None else api.product_id
        self.url_list = api.host + "/"
        self.url_detail = api.host + f"/product/{self.product_id}"
        self.url_add = api.host + f"/seller/product/{self.seller_id}/edit"
        self.url_status = api.host + f"/seller/product/{self.seller_id}/toggle"
        self.session = session if session is not None else requests.Session()

    def api_prod_list(self):
        logger.info("商品列表 | GET {}", self.url_list)
        resp = self.session.get(url=self.url_list)
        logger.info("商品列表 | 响应状态码: {}", resp.status_code)
        return resp

    def api_prod_search(self, keyword):
        logger.info("商品搜索 | GET {} | keyword={}", self.url_list, keyword)
        resp = self.session.get(url=self.url_list, params={"keyword": keyword})
        logger.info("商品搜索 | 响应状态码: {}", resp.status_code)
        return resp

    def api_prod_detail(self):
        logger.info("商品详情 | GET {}", self.url_detail)
        resp = self.session.get(url=self.url_detail)
        logger.info("商品详情 | 响应状态码: {}", resp.status_code)
        return resp

    def api_prod_add(self, name, category_id, price, stock, origin, description):
        data = {
            "name": name, "category_id": category_id,
            "price": price, "stock": stock,
            "origin": origin, "description": description
        }
        logger.info("商品编辑 | POST {} | data={}", self.url_add, data)
        resp = self.session.post(url=self.url_add, data=data)
        logger.info("商品编辑 | 响应状态码: {}", resp.status_code)
        return resp

    def api_prod_status(self):
        logger.info("商品上下架 | POST {}", self.url_status)
        resp = self.session.post(url=self.url_status)
        logger.info("商品上下架 | 响应状态码: {}", resp.status_code)
        return resp