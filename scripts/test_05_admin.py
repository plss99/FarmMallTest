import pytest
from loguru import logger

import api
from api.api_admin import ApiAdmin
from tool.auto_login import admin_session, user_session
from tool.data_maker import active_product, admin_order
from tool.get_db_info import GetDBInfo
from tool.read_yaml import read_yaml

info = GetDBInfo()


class TestAdmin:
    # 初始化-把接口类对象写成夹具
    @pytest.fixture
    def admin(self, admin_session, active_product, admin_order):
        return ApiAdmin(
            session=admin_session,
            product_id=active_product["id"],
            order_id=admin_order
        )

    # 测试管理员正常访问接口
    @pytest.mark.parametrize("username,password", read_yaml("admin_login.yaml"))
    def test_01_admin_login(self, admin, username, password):
        resp = admin.api_admin_login(username, password)
        try:
            assert resp.status_code == 200, f"管理员登录失败，状态码：{resp.status_code}"
            assert "管理员" in resp.text or "admin" in resp.text.lower(), "响应内容未包含管理员标识"
        except Exception as e:
            logger.error(f"管理员登录失败：{e}")
            raise e


    # 普通用户越权访问-预期：访问管理员接口均被拦截
    def test_02_admin_login(self, admin, user_session):
        urls = [
            f"{api.host}/admin",
            f"{api.host}/admin/product/{admin.product_id}/toggle",
            f"{api.host}/admin/orders/{admin.order_id}/status",
        ]
        for url in urls:
            method = user_session.post if "toggle" in url or "status" in url else user_session.get
            resp = method(
                url=url,
                data={"status": "已发货"} if "status" in url else None,
                allow_redirects=False)
            assert resp.status_code == 302, f"越权拦截失败：{url}，状态码：{resp.status_code}"
            assert resp.headers.get("Location") == "/", f"未重定向到首页：{url}，Location：{resp.headers.get('Location')}"

    # 强制上下架某商品
    def test_03_admin_coerce(self, admin, active_product):
        product_id = active_product["id"]
        old_status = info.get_product_status(product_id)
        resp = admin.api_admin_coerce()
        try:
            assert resp.status_code == 200, f"强制上下架失败，状态码：{resp.status_code}"
            new_status = info.get_product_status(product_id)
        except Exception as e:
            logger.error(f"强制上下架失败：{e}")
            raise e
        assert old_status != new_status, f"商品状态未切换，操作前后状态均为：{old_status}"

    # 修改订单状态
    def test_04_admin_status(self, admin, admin_order):
        resp = admin.api_admin_status(status="已发货")
        try:
            assert resp.status_code == 200, f"修改订单状态失败，状态码：{resp.status_code}"
            new_status = info.get_order_status(admin_order)
        except Exception as e:
            logger.error(f"修改订单状态失败：{e}")
            raise e
        assert new_status == "已发货", f"订单状态修改未生效，预期：已发货，实际：{new_status}"

    # 查看所有用户
    def test_05_admin_users(self, admin):
        resp = admin.api_admin_users()
        try:
            assert resp.status_code == 200, f"查看用户列表失败，状态码：{resp.status_code}"
            assert len(resp.text) > 0, "用户列表响应为空"
        except Exception as e:
            logger.error(f"查看用户列表失败：{e}")
            raise e