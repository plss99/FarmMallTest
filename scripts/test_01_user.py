from loguru import logger

import pytest

from api.api_user import ApiUser
from tool.read_yaml import read_yaml


class TestUser:
    # 初始化
    @classmethod
    def setup_class(cls):
        # 获取ApiUser对象
        cls.user = ApiUser()
    # 1.登录接口测试方法
    @pytest.mark.parametrize("username,password", read_yaml("user_login.yaml"))
    def test_01_user_login(self,username,password):
        # 调用登录接口
        resp = self.user.api_user_login(username,password)
        # 打印输出结果
        print(f"登录的结果为：{resp.text}")
        try:
            # 断言状态码
            assert resp.status_code == 200
            # 断言响应信息
            assert f"欢迎回来，{username}。" in resp.text
        except Exception as e:
            # 写日志
            logger.error(f"错误日志:{e}")
            # 抛异常
            raise e
    # 2.正确用户名+错误密码
    @pytest.mark.parametrize("username,password", read_yaml("user_login_error.yaml"))
    def test_02_user_login_error(self,username,password):
        # 调用登录接口
        resp = self.user.api_user_login(username,password)
        try:
            # 断言状态码
            assert resp.status_code == 200
            # 断言响应信息
            assert "用户名或密码错误" in resp.text
        except Exception as e:
            # 写日志
            logger.error(f"错误日志:{e}")
            # 抛异常
            raise e
    # 3.注册接口测试方法
    @pytest.mark.parametrize("r_username,r_password", read_yaml("user_reg.yaml"))
    def test_03_user_reg(self,r_username,r_password):
        # 调用注册接口
        resp = self.user.api_user_reg(r_username,r_password)
        try:
            # 断言状态码
            assert resp.status_code == 200
            # 断言响应信息
            assert "注册成功，已自动登录。" in resp.text
        except Exception as e:
            # 写日志
            logger.error(f"错误日志:{e}")
            # 抛异常
            raise e
    # 4.用户退出登录接口测试方法
    def test_04_user_logout(self):
        # 调用成功登录接口
        self.user.api_user_login_success()
        # 调用退出登录接口
        resp = self.user.api_user_logout()
        try:
            # 断言状态码
            assert resp.status_code == 200
            # 断言响应信息
            assert "已退出登录。" in resp.text
        except Exception as e:
            # 写日志
            logger.error(f"错误日志:{e}")
            # 抛异常
            raise e