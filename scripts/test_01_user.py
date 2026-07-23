from datetime import datetime
from loguru import logger

import pytest

from api.api_user import ApiUser
from tool.data_maker import clean_user_by_username
from tool.read_yaml import read_yaml


class TestUser:
    @classmethod
    def setup_class(cls):
        cls.user = ApiUser()

    @pytest.mark.parametrize("username,password", read_yaml("user_login.yaml"))
    def test_01_user_login(self, username, password):
        resp = self.user.api_user_login(username, password)
        print(f"登录的结果为：{resp.text}")
        try:
            assert resp.status_code == 200
            assert f"欢迎回来，{username}。" in resp.text
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e

    @pytest.mark.parametrize("username,password", read_yaml("user_login_error.yaml"))
    def test_02_user_login_error(self, username, password):
        resp = self.user.api_user_login(username, password)
        try:
            assert resp.status_code == 200
            assert "用户名或密码错误" in resp.text
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e

    @pytest.mark.parametrize("r_username,r_password", read_yaml("user_reg.yaml"))
    def test_03_user_reg(self, r_username, r_password):
        # 解析动态用户名，确保每次运行唯一
        if "{{timestamp}}" in r_username:
            r_username = r_username.replace(
                "{{timestamp}}", datetime.now().strftime("%Y%m%d%H%M%S%f")
            )
        # 先清理可能残留的旧数据（上次运行异常中断的情况）
        clean_user_by_username(r_username)
        try:
            resp = self.user.api_user_reg(r_username, r_password)
            assert resp.status_code == 200
            assert "注册成功，已自动登录。" in resp.text
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e
        finally:
            # 无论成功失败，清理测试数据，确保下次可重复运行
            clean_user_by_username(r_username)

    def test_04_user_logout(self):
        self.user.api_user_login_success()
        resp = self.user.api_user_logout()
        try:
            assert resp.status_code == 200
            assert "已退出登录。" in resp.text
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e