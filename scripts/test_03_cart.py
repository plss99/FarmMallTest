import pytest
from api.api_cart import ApiCart
from loguru import logger

from tool.auto_login import user_session
from tool.data_maker import active_product


class TestCart:
    @pytest.fixture
    def cart(self, user_session, active_product):
        return ApiCart(session=user_session, product_id=active_product["id"])

    def test_01_cart_add(self, cart):
        resp = cart.api_cart_add()
        try:
            assert resp.status_code == 200
            assert "商品已加入购物车。" in resp.text
        except Exception as e:
            logger.error(f"购物车添加失败：{e}")
            raise e

    def test_02_cart_list(self, cart):
        resp = cart.api_cart_list()
        try:
            assert resp.status_code == 200
        except Exception as e:
            logger.error(f"购物车列表查看失败：{e}")
            raise e

    def test_03_cart_remove(self, cart):
        resp = cart.api_cart_remove()
        try:
            assert resp.status_code == 200
            assert "已从购物车移除。" in resp.text
        except Exception as e:
            logger.error(f"购物车移除失败：{e}")
            raise e