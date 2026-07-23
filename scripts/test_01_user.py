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
        logger.info("登录结果: {}", resp.text[:200])
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
        r_username = r_username
        resp = self.user.api_user_reg(r_username, r_password)
        try:
            assert resp.status_code == 200
        except Exception as e:
            logger.error(f"错误日志:{e}")
            raise e
        finally:
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