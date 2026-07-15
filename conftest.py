# 项目级 conftest：pytest 启动时自动配置日志，结束后自动生成 Allure 报告
import pytest
from tool.get_logger import GetLogger


def pytest_configure(config):
    """session 启动：配置 loguru 日志"""
    GetLogger.get_logger()


def pytest_sessionfinish(session, exitstatus):
    """session 结束：自动生成带趋势的 Allure 报告"""
    try:
        GetLogger.generate_report()
    except FileNotFoundError:
        pass