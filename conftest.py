# 项目级 conftest：pytest 启动时自动配置日志、复制历史趋势，结束后自动生成 Allure 报告
import pytest
from tool.get_logger import GetLogger


def pytest_configure(config):
    """session 启动：配置 loguru 日志 + 复制历史趋势数据到 allure_results"""
    GetLogger.get_logger()
    GetLogger.copy_history_for_trend()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """pytest 全部结束后（含插件）自动生成带趋势的 Allure 报告"""
    GetLogger.generate_report()
    terminalreporter.write_sep("=", "Allure 报告", bold=True)
    terminalreporter.write_line("报告路径: report/allure_report/index.html")
    terminalreporter.write_line("查看报告: python tool/get_logger.py -s")