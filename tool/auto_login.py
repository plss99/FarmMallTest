import pytest
import requests
import api

# 会话型夹具（登录不同的角色）
@pytest.fixture
def user_session(username="小农户", password="REDACTED"):
    """普通用户登录态（小农户）"""
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
            "username": "admin",
            "password": "REDACTED"
        })
    # 在测试结束后自动执行清理工作
    yield session
    # 关闭连接，释放系统资源
    session.close()

