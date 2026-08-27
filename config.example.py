import os

BASE_PATH = os.path.dirname(__file__)

# 数据库连接配置（请复制为 config.py 并填入真实信息）
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "your_user",
    "password": "your_password",
    "database": "your_database",
}

# 测试账号配置（请复制为 config.py 并填入真实信息）
# 用于登录/注册测试的默认账号，不提交到 Git
TEST_ACCOUNTS = {
    "user": {"username": "your_user", "password": "your_password"},
    "admin": {"username": "your_admin", "password": "your_admin_password"},
    "default_user": {"username": "your_tester", "password": "your_tester_password"},
}