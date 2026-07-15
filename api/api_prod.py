# 商品模块接口
import requests

import api


class ApiProd:
    def __init__(self, session=None, product_id=None, seller_id=None):
        self.product_id = product_id if product_id is not None else api.product_id
        self.seller_id = seller_id if seller_id is not None else api.product_id
        # 接口url
        self.url_list = api.host + "/"
        self.url_detail = api.host + f"/product/{self.product_id}"
        self.url_add = api.host + f"/seller/product/{self.seller_id}/edit"
        self.url_status = api.host + f"/seller/product/{self.seller_id}/toggle"
        self.session = session if session is not None else requests.Session()
    # 列表接口
    def api_prod_list(self):
        return self.session.get(url=self.url_list)
    # 关键词搜索
    def api_prod_search(self,keyword):
        return self.session.get(
            url=self.url_list,
            params={"keyword":keyword}
        )
    # 详情接口
    def api_prod_detail(self):
        return self.session.get(url=self.url_detail)
    # 卖家编辑商品接口
    def api_prod_add(self,name,category_id,price,stock,origin,description):
        data = {
            "name":name,
            "category_id":category_id,
            "price":price,
            "stock":stock,
            "origin":origin,
            "description":description
        }
        return self.session.post(url=self.url_add, data=data)
    # 卖家下架商品接口
    def api_prod_status(self):
        return self.session.post(url=self.url_status)