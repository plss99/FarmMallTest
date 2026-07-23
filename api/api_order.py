# 订单模块接口
import requests
from loguru import logger

import api


class ApiOrder:
    def __init__(self, session=None, product_id=None, order_id=None):
        self.product_id = product_id if product_id is not None else api.product_id
        self.order_id = order_id if order_id is not None else api.order_id
        self.order = api.host + "/checkout"
        self.order_detail = api.host + f"/orders/{self.order_id}"
        self.order_cancel = api.host + f"/orders/{self.order_id}/cancel"
        self.session = session if session is not None else requests.Session()

    def api_order(self, receiver_name, phone, address, remark):
        data = {
            "receiver_name": receiver_name,
            "phone": phone,
            "address": address,
            "remark": remark
        }
        logger.info("提交订单 | POST {} | data={}", self.order, data)
        resp = self.session.post(url=self.order, data=data)
        logger.info("提交订单 | 响应状态码: {}", resp.status_code)
        return resp

    def api_order_detail(self, order_id=None):
        url = api.host + f"/orders/{order_id}" if order_id is not None else self.order_detail
        logger.info("订单详情 | GET {}", url)
        resp = self.session.get(url=url)
        logger.info("订单详情 | 响应状态码: {}", resp.status_code)
        return resp

    def api_order_cancel(self, order_id=None):
        url = api.host + f"/orders/{order_id}/cancel" if order_id is not None else self.order_cancel
        logger.info("取消订单 | POST {}", url)
        resp = self.session.post(url=url)
        logger.info("取消订单 | 响应状态码: {} | 响应内容: {}", resp.status_code, resp.text[:200])
        return resp