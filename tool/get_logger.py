# 日志封装 + 自动生成带趋势的 Allure 报告
import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from loguru import logger

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "log"
REPORT_DIR = BASE_DIR / "report"
RESULT_DIR = REPORT_DIR / "allure_results"
HTML_DIR = REPORT_DIR / "allure_report"
HISTORY_DIR = HTML_DIR / "history"
# 虚拟环境中的 allure 命令行工具路径
_VENV_DIR = BASE_DIR / ".venv"
_ALLURE_BIN = _VENV_DIR / "allure-cli" / "allure-2.45.0" / "bin" / "allure.bat"


class GetLogger:
    _configured = False

    @classmethod
    def _setup(cls):
        if cls._configured:
            return
        cls._configured = True

        # 移除默认 handler
        logger.remove()

        # 控制台输出（带颜色）
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            level="DEBUG",
            colorize=True,
        )

        # 文件输出（按天归档）
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        logger.add(
            LOG_DIR / "run_{time:YYYYMMDD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            encoding="utf-8",
        )

    @staticmethod
    def get_logger():
        """获取配置好的 logger 实例"""
        GetLogger._setup()
        return logger

    # ========== Allure 报告相关 ==========

    @staticmethod
    def _ensure_dirs():
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        RESULT_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _clean_results():
        if RESULT_DIR.exists():
            shutil.rmtree(RESULT_DIR)
            RESULT_DIR.mkdir()

    @staticmethod
    def clean_results():
        """清理 allure_results 目录（测试前调用，避免新旧结果混在一起）"""
        GetLogger._setup()
        if RESULT_DIR.exists():
            shutil.rmtree(RESULT_DIR)
        RESULT_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("已清理 allure_results 目录")
        return RESULT_DIR

    @staticmethod
    def _copy_history():
        if not HISTORY_DIR.exists():
            return
        target = RESULT_DIR / "history"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(HISTORY_DIR, target)

    @staticmethod
    def copy_history_for_trend():
        """
        在 pytest 启动时将上一次报告的 history 复制到 allure_results，
        这样 Allure 生成报告时才能合并历史数据，产生趋势图。
        必须在 pytest 写入测试结果之前调用。
        """
        GetLogger._setup()
        if not HISTORY_DIR.exists():
            logger.debug("未找到历史报告 history 目录，首次运行无趋势图属于正常现象")
            return
        RESULT_DIR.mkdir(parents=True, exist_ok=True)
        target = RESULT_DIR / "history"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(HISTORY_DIR, target)
        logger.info("已复制历史趋势数据到 {}", target)

    @staticmethod
    def run_tests(test_target=None, markers=None, clean=True):
        """
        运行 pytest 并产出 allure 原始数据
        :param test_target: 测试目标，如 "scripts/test_05_admin.py"
        :param markers:     pytest 标记，如 "single" 或 "scenario"
        :param clean:       是否清空上次 allure_results
        """
        GetLogger._setup()
        GetLogger._ensure_dirs()
        if clean:
            GetLogger.clean_results()

        cmd = [sys.executable, "-m", "pytest"]
        if test_target:
            cmd.append(test_target)
        if markers:
            cmd.extend(["-m", markers])

        logger.info("开始运行测试: {}", " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE_DIR))
        logger.info("测试完成，退出码: {}", result.returncode)
        return result.returncode

    @staticmethod
    def generate_report():
        """生成带趋势的 Allure HTML 报告（趋势数据已在 pytest_configure 中复制）"""
        GetLogger._setup()

        if not RESULT_DIR.exists() or not any(RESULT_DIR.iterdir()):
            logger.warning("allure_results 目录为空，请先运行测试")
            return 1

        cmd = f'"{_ALLURE_BIN}" generate "{RESULT_DIR}" -o "{HTML_DIR}" --clean'
        logger.info("生成报告: {}", cmd)
        result = subprocess.run(cmd, cwd=str(BASE_DIR), shell=True)

        if result.returncode == 0:
            logger.info("报告已生成: {}", HTML_DIR / "index.html")
        else:
            logger.error("报告生成失败，请确认已安装 allure 命令行工具")
        return result.returncode

    @staticmethod
    def serve_report(port=8923):
        """启动 HTTP 服务查看 Allure 报告，按 Ctrl+C 停止"""
        GetLogger._setup()
        index = HTML_DIR / "index.html"
        if not index.exists():
            logger.error("报告文件不存在，请先运行 pytest 生成报告")
            return

        import http.server
        import socketserver

        os.chdir(str(HTML_DIR))

        handler = http.server.SimpleHTTPRequestHandler
        try:
            with socketserver.TCPServer(("", port), handler) as httpd:
                url = f"http://127.0.0.1:{port}"
                logger.info("Allure 报告已启动: {}", url)
                print(f"\n{'='*60}")
                print(f"  Allure 报告: {url}")
                print(f"  按 Ctrl+C 停止服务")
                print(f"{'='*60}\n")
                httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("报告服务已停止")
        except OSError as e:
            logger.error("端口 {} 已被占用: {}", port, e)

    @staticmethod
    def run_and_report(test_target=None, markers=None, clean=True):
        """一键运行测试 + 生成报告（带趋势）"""
        GetLogger._setup()
        GetLogger.run_tests(test_target, markers, clean)
        GetLogger.generate_report()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行测试并生成带趋势的 Allure 报告")
    parser.add_argument("target", nargs="?", default=None,
                        help="测试目标，如 scripts/test_05_admin.py")
    parser.add_argument("-m", "--markers", default=None,
                        help="pytest 标记，如 single 或 scenario")
    parser.add_argument("--no-clean", action="store_true",
                        help="不清空上次的 allure_results")
    parser.add_argument("--report-only", action="store_true",
                        help="仅生成报告，不运行测试")
    parser.add_argument("-s", "--serve", action="store_true",
                        help="启动 HTTP 服务查看报告")
    parser.add_argument("-p", "--port", type=int, default=8923,
                        help="报告服务端口（默认 8923）")

    args = parser.parse_args()

    if args.serve:
        GetLogger.serve_report(args.port)
    elif args.report_only:
        GetLogger.generate_report()
    else:
        GetLogger.run_and_report(args.target, args.markers, clean=not args.no_clean)