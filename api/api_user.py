# 用户端接口
import requests
from loguru import logger

import api
from config import TEST_ACCOUNTS


class ApiUser:
    def __init__(self):
        self.url_login = api.host + "/login"
        self.url_reg = api.host + "/register"
        self.url_logout = api.host + "/logout"
        self.session = requests.Session()

    def api_user_login(self, username, password):
        data = {"username": username, "password": password}
        logger.info("用户登录 | POST {} | username={}", self.url_login, username)
        resp = self.session.post(url=self.url_login, data=data)
        logger.info(f"用户登录 | 响应状态码: {resp.status_code} | 响应内容: {resp.text}")
        return resp

    def api_user_reg(self, r_username, r_password):
        data = {"username": r_username, "password": r_password, "confirm": r_password}
        logger.info("用户注册 | POST {} | username={}", self.url_reg, r_username)
        resp = self.session.post(url=self.url_reg, data=data)
        logger.info(f"用户注册 | 响应状态码: {resp.status_code} | 响应内容: {resp.text}")
        return resp

    def api_user_logout(self):
        logger.info("用户退出 | GET {}", self.url_logout)
        resp = self.session.get(url=self.url_logout)
        logger.info(f"用户退出 | 响应状态码: {resp.status_code}")
        return resp

    def api_user_login_success(self):
        data = dict(TEST_ACCOUNTS["user"])
        logger.info("普通用户快速登录 | POST {} | username={}", self.url_login, data["username"])
        resp = self.session.post(url=self.url_login, data=data)
        logger.info(f"普通用户快速登录 | 响应状态码: {resp.status_code}")
        return resp