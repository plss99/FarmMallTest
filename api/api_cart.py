# 购物车模块接口
import requests

import api


class ApiCart:
    # 初始化
    def __init__(self, session=None, product_id=None):
        self.product_id = product_id if product_id is not None else api.product_id
        # 购物车添加、列表、移除接口url
        self.url_cart_add = api.host + f"/product/{self.product_id}/buy"
        self.url_cart_list = api.host + "/cart"
        self.url_cart_remove = api.host + f"/cart/product/{self.product_id}/remove"
        # 创建一个session对象来自动管理cookie，支持外部传入已登录的session
        self.session = session if session is not None else requests.Session()
    # 添加接口
    def api_cart_add(self):
        return self.session.post(self.url_cart_add)
    # 查看接口
    def api_cart_list(self):
        return self.session.get(self.url_cart_list)
    # 移除接口
    def api_cart_remove(self):
        return self.session.post(self.url_cart_remove)