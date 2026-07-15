# 订单模块测试方法
import pytest
import threading
import re
from loguru import logger
from tool.auto_login import user_session, admin_session
from tool.data_maker import active_product, user_order, admin_order, stock_1_product
from tool.get_db_info import GetDBInfo
from api.api_order import ApiOrder
import api
from tool.read_yaml import read_yaml

info = GetDBInfo()

class TestOrder:
    # 初始化
    @pytest.fixture
    def order(self, user_session, active_product,user_order):
        return ApiOrder(
            session=user_session,
            product_id=active_product["id"],
            order_id=user_order)
    # 正常下单测试方法
    @pytest.mark.parametrize("receiver_name, phone, address, remark",read_yaml("order.yaml"))
    def test_01_checkout(self, order, receiver_name, phone, address, remark):
        resp = order.api_order(
            receiver_name=receiver_name,
            phone=phone,
            address=address,
            remark=remark
        )
        try:
            assert resp.status_code == 200
        except Exception as e:
            logger.error(f"下单失败：{e}")
            raise e

    # 超卖防御测试方法-每个线程独立创建 Session 和 ApiOrder()
    def test_02_seckill(self,stock_1_product,user_session, admin_session):
        """
        使用两个不同的已登录用户（小农户 + admin）同时抢购同一件库存=1的商品,
        预期：只有 1 人成功，最终库存为 0
        """
        product_id = stock_1_product

        # 下单所需公共参数
        order_data = {
            "receiver_name": "并发测试",
            "phone": "13800138000",
            "address": "北京市朝阳区",
            "remark": "超卖防御测试"
        }
        # 收集两个线程的响应状态码
        statuses = []

        def place_order(session, user_label):
            """
            单个用户的抢购流程：加购 → 下单
            :param session: 已登录的 requests.Session(用夹具)
            :param user_label: 用于调试的用户标识
            """

            try:
                # 1. 加购
                add_resp = session.post(f"{api.host}/product/{product_id}/buy")
                logger.info(f"[{user_label}] 加购状态码: {add_resp.status_code}")

                # 2. 提交订单（不自动跟随重定向，方便抓取状态码）
                resp = session.post(
                    url=f"{api.host}/checkout",
                    data=order_data,
                    allow_redirects=False
                )
                # 添加状态码到预先设置的列表中
                statuses.append(resp.status_code)
                logger.info(f"[{user_label}] 下单状态码: {resp.status_code}")
            except Exception as err:
                logger.error(f"[{user_label}] 异常: {err}")
                # 把异常状态码也添加进去
                statuses.append(500)
        # 启动两个线程，分别使用两个不同的已登录用户
        t1 = threading.Thread(
            target=place_order,
            args=(user_session, "小农户")
        )
        t2 = threading.Thread(
            target=place_order,
            args=(admin_session, "管理员")
        )

        t1.start()
        t2.start()
        t1.join()
        t2.join()
        try:
            # 把状态码为302的用户(成功下单)加在一起，等于1说明超卖防御成功
            success_count = sum(1 for s in statuses if s == 302)
            assert success_count == 1, (
                f"超卖防御失败！预期只有 1 人成功下单，"
            f"实际成功 {success_count} 人，状态码列表: {statuses}")
        except Exception as e:
            logger.error(e)
            raise e

    # 价格篡改防御测试方法
    def test_03_price_change(self, order, active_product):
        """价格篡改防御：伪造 price=1，验证后端忽略"""
        product_id = active_product["id"]
        # 查真实价格
        real_price = info.get_product_price(product_id)

        # 先加购
        order.session.post(f"{api.host}/product/{product_id}/buy")

        data = {
            "receiver_name": "测试价格篡改防御",
            "phone": "13800138000",
            "address": "北京",
            "remark": "",
            "price": 1,
            "total": 1
        }
        # 下单并篡改
        resp = order.session.post(order.order, data=data, allow_redirects=False)
        try:
            assert resp.status_code == 302
            # 提取订单ID-查找重定向之后的URL中的订单ID
            match = re.search(r'/orders/(\d+)', resp.headers.get("Location", ""))
            assert match is not None, f"未找到订单重定向URL，Location: {resp.headers.get('Location')}"
            order_id = int(match.group(1))
            # 断言金额未被篡改
            assert info.get_order_total(order_id) == real_price
        except Exception as e:
            logger.error(f"价格篡改防御测试失败：{e}")
            raise e

    # 查看具体的订单
    def test_04_order_detail(self,order,user_order):
        resp = order.api_order_detail(order_id=user_order)
        try:
            assert resp.status_code == 200
        except Exception as e:
            logger.error(f"订单详情查看失败：{e}")
            raise e

    # 越权查看他人订单
    def test_05_others_order(self,order,admin_order):
        resp = order.api_order_detail(order_id=admin_order)
        try:
            assert resp.status_code == 200
            assert "订单不存在或无权查看" in resp.text
        except Exception as e:
            logger.error(f"订单详情查看失败：{e}")
            raise e

    # 取消订单
    def test_06_order_cancel(self,order,user_order):
        resp = order.api_order_cancel(order_id=user_order)
        try:
            assert resp.status_code == 200
            assert "订单已取消" in resp.text
        except Exception as e:
            logger.error(f"订单取消失败：{e}")
            raise e