# FarmMallTest - 田禾优选电商平台自动化测试

基于 **Pytest + Requests + Allure** 的接口自动化测试框架，覆盖用户、商品、购物车、订单、管理员及全链路业务场景。

---

## 前置条件

本项目是 [farm-mall](https://github.com/SoliBooster/farm-mall) 开源电商平台的配套测试项目，**必须先启动 farm-mall 后端服务**

> 确保 farm-mall 后端正常运行且 MySQL 数据库已启动，否则所有测试用例都会失败。

---

## 项目结构

```
FarmMallTest/
├── api/                  # 接口封装（6 个模块）
├── data/                 # YAML 测试数据
├── scripts/              # 测试用例（24 条，6 个模块）
├── tool/                 # 工具层（夹具、日志、报告、数据清理）
├── log/                  # 日志输出
├── report/               # Allure 报告
├── config.example.py      # 数据库/账号配置模板（复制为 config.py）
├── conftest.py           # Pytest 全局配置（日志 + 自动生成报告）
├── pytest.ini            # Pytest 运行配置
└── requirements.txt      # 依赖列表
```

---

## 快速开始

```bash
# 1. 激活虚拟环境
.venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置数据库与测试账号（在样例模板中填入真实信息之后另存为 config.py）
copy config.example.py config.py

# 4. 复制本地测试数据模板（真实账号密码只保存在本地，不提交到 Git）
copy data\user_login.example.yaml data\user_login.yaml
copy data\user_login_error.example.yaml data\user_login_error.yaml
copy data\admin_login.example.yaml data\admin_login.yaml
copy data\user_reg.example.yaml data\user_reg.yaml

# 5. 确保 farm-mall 后端已启动后，运行测试
pytest
```

---

## 运行测试

```bash
# 全部测试（自动生成带趋势图的 Allure 报告）
pytest

# 指定模块
pytest scripts/test_01_user.py

# 按标记运行
pytest -m "single"      # 单接口测试
pytest -m "scenario"    # 场景链路测试
```

---

## 查看报告

pytest 运行结束后会自动生成 HTML 报告，启动服务即可查看：

```bash
python tool/get_logger.py -s
```

```bash
python tool/get_logger.py -s -p 8080
```
---
浏览器打开 `http://127.0.0.1:8923`，按 `Ctrl+C` 停止。

## 测试覆盖

| 模块 | 用例数 | 覆盖场景 |
|------|--------|----------|
| 用户模块 | 4 | 登录、登录异常、注册、退出登录 |
| 商品模块 | 5 | 商品列表、搜索、详情、编辑、下架 |
| 购物车模块 | 3 | 加入购物车、查看、移除 |
| 订单模块 | 6 | 正常下单、超卖防御、价格篡改防御、详情、越权查看、取消 |
| 管理员模块 | 5 | 管理员登录、越权拦截、强制上下架、修改订单状态、查看用户列表 |
| 全链路 | 1 | 搜索→加购→下单→管理员发货→用户查看 |
| **合计** | **24** | |

---

## 设计亮点

- **数据驱动**：YAML 管理测试数据
- **夹具自动清理**：`yield` 夹具自动造数据 + 测试后自动清理，`clean_user_by_username` 确保注册测试可重复执行
- **数据库断言**：`db_assert` 直接校验数据库字段，确保接口操作落库正确
- **并发超卖测试**：`threading` 模拟多用户并发抢购，验证库存=1时的超卖防御
- **全链路测试**：串联搜索→加购→下单→发货→查看完整业务流
- **日志与报告**：Loguru 按天归档 + `pytest` 一键自动生成 Allure 报告（含趋势图）