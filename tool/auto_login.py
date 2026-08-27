import pytest
import requests
import api
from config import TEST_ACCOUNTS

# 会话型夹具（登录不同的角色）
@pytest.fixture
def user_session(username=None, password=None):
    """普通用户登录态（小农户）"""
    if username is None or password is None:
        username = TEST_ACCOUNTS["user"]["username"]
        password = TEST_ACCOUNTS["user"]["password"]
    session = requests.Session()
    url = api.host + "/login"
    session.post(
        url=url,
        data={
            "username": username,
            "password": password
        })
    #在测试结束后自动执行清理工作
    yield session
    # 关闭连接，释放系统资源
    session.close()

@pytest.fixture
def admin_session():
    """管理员登录态（admin）"""
    session = requests.Session()
    url = api.host + "/login"
    session.post(
        url=url,
        data={
            "username": TEST_ACCOUNTS["admin"]["username"],
            "password": TEST_ACCOUNTS["admin"]["password"]
        })
    # 在测试结束后自动执行清理工作
    yield session
    # 关闭连接，释放系统资源
    session.close()