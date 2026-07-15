# 订单模块接口
import requests

import api
from api import product_id


class ApiOrder:
    # 初始化
    def __init__(self, session=None,product_id=None,order_id=None):
        self.product_id = product_id if product_id is not None else api.product_id
        self.order_id = order_id if order_id is not None else api.order_id
        # 提交订单url
        self.order = api.host + "/checkout"
        # 订单详情url
        self.order_detail = api.host + f"/orders/{self.order_id}"
        # 订单取消url
        self.order_cancel = api.host + f"/orders/{self.order_id}/cancel"
        # 创建一个session对象来自动管理cookie，支持外部传入已登录的session
        self.session = session if session is not None else requests.Session()
    # 提交订单接口
    def api_order(self, receiver_name, phone, address, remark):
        data = {
            "receiver_name": receiver_name,
            "phone": phone,
            "address": address,
            "remark": remark
        }
        return self.session.post(url=self.order, data=data)
    # 订单详情接口
    def api_order_detail(self, order_id=None):
        if order_id is not None:
            url = api.host + f"/orders/{order_id}"
        else:
            url = self.order_detail
        return self.session.get(url=url)
    # 订单取消接口
    def api_order_cancel(self, order_id=None):
        if order_id is not None:
            url = api.host + f"/orders/{order_id}/cancel"
        else:
            url = self.order_cancel
        return self.session.post(url=url)