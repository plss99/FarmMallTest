# 全链路流程测试-用户登录-购买商品-支付订单->管理员登录-修改订单状态->用户查看订单状态
import pytest
from loguru import logger
from api.api_all_chain import ApiAllChain
from tool.get_db_info import GetDBInfo


class TestAllChain:
    def test_all_chain(self):
        chain = ApiAllChain()
        info = GetDBInfo()

        resp = chain.api_all_chain()
        try:
            assert resp.status_code == 200
            db_status = info.get_order_status(chain.order_id)
            assert db_status == "已发货"
        except Exception as e:
            logger.error(f"全链路业务失败: {e}")
            raise e