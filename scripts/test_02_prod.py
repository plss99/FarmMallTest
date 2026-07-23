import pytest
from api.api_prod import ApiProd
from loguru import logger

from tool.data_maker import active_product, my_product, db_assert
from tool.read_yaml import read_yaml
from tool.auto_login import user_session


class TestProd:
    def test_01_prod_list(self):
        prod = ApiProd()
        resp = prod.api_prod_list()
        try:
            assert resp.status_code == 200
            assert "商品列表" in resp.text
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e

    def test_02_prod_search(self, active_product):
        product_name = active_product["name"]
        prod = ApiProd(product_id=active_product["id"])
        try:
            resp = prod.api_prod_search(keyword=product_name)
            assert resp.status_code == 200
            assert product_name in resp.text
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e
        finally:
            prod = None

    def test_03_prod_detail(self, active_product):
        product_name = active_product["name"]
        prod = ApiProd(product_id=active_product["id"])
        resp = prod.api_prod_detail()
        try:
            assert resp.status_code == 200
            assert product_name in resp.text
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e

    @pytest.mark.parametrize("name,category_id,price,stock,origin,description",
                             read_yaml("prod_add.yaml"))
    def test_04_prod_add(self, user_session, my_product,
                         name, category_id, price, stock, origin, description):
        sell_product_id = my_product
        prod = ApiProd(session=user_session, seller_id=sell_product_id)
        resp = prod.api_prod_add(
            name=name,
            category_id=category_id,
            price=price,
            stock=stock,
            origin=origin,
            description=description
        )
        try:
            assert resp.status_code == 200
            db_assert(sell_product_id, name=name)
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e

    def test_05_prod_update(self, user_session, my_product):
        sell_product_id = my_product
        prod = ApiProd(session=user_session, seller_id=sell_product_id)
        resp = prod.api_prod_status()
        try:
            assert resp.status_code == 200
            db_assert(sell_product_id, status='off')
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e