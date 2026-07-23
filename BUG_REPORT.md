# Bug 报告 - FarmMallTest 自动化测试

**测试执行时间**: 2026-07-23 11:18 ~ 11:33（共 3 轮）  
**最新测试结果**: 23 passed, 1 failed  
**Allure 报告（运行测试用例之后）**: http://127.0.0.1:8923（含趋势图）

---

## BUG-001: 超卖防御失效 - 并发抢购库存=1商品时两人均成功下单

| 属性 | 详情 |
|------|------|
| **严重程度** | 🔴 Critical（严重） |
| **优先级** | P0 |
| **所属模块** | 订单模块 |
| **测试用例** | `test_04_order.py::TestOrder::test_02_seckill` |
| **复现率** | 100%（3轮均失败） |

### 问题描述

当两个不同用户（小农户 + 管理员）同时对一件库存=1的商品并发抢购时，预期只有 1 人成功下单，但实际两人均成功下单（状态码均为 302），导致**超卖**。

### 复现步骤

1. 准备一件库存=1的商品（由 `stock_1_product` 夹具自动创建）
2. 小农户和管理员分别登录获取 Session
3. 两个用户同时执行：加购 → 提交订单
4. 使用 `threading` 启动两个线程模拟并发

### 测试数据

- 商品：`【超卖测试专用】限量1件`（price=99.9, stock=1）
- 用户A：小农户（user_id=2）
- 用户B：管理员（user_id=1, admin）
- 下单参数：receiver_name="并发测试", phone="13800138000", address="北京市朝阳区"

### 实际结果

```
超卖防御失败！预期只有 1 人成功下单，实际成功 2 人，状态码列表: [302, 302]
assert 2 == 1
```

两个用户都返回了 302（重定向到订单详情页），说明两笔订单都成功创建。

### 预期结果

只有 1 人成功下单（返回 302），另 1 人应收到库存不足的提示（返回 200 并显示错误信息）。

### 根因分析

后端在 `/checkout` 接口中可能缺少库存扣减的**原子性操作**（如使用 `SELECT ... FOR UPDATE` 行锁、乐观锁版本号、或 Redis 分布式锁），导致并发场景下两个请求同时读取到 `stock=1`，都通过了库存校验，最终都成功创建订单。

建议修复方案：
1. 数据库层面：在 `orders` 表插入前使用 `SELECT stock FROM products WHERE id=? FOR UPDATE` 锁定商品行，在事务内扣减库存
2. 应用层面：使用 Redis 分布式锁或 Lua 脚本保证库存扣减的原子性
3. 在库存扣减 SQL 中加入条件：`UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0`，通过 `affected_rows` 判断是否扣减成功

### 附件

- 测试代码：[test_04_order.py](file:///D:/PyCharm 2021.2.1/PythonProject/FarmMallTest/scripts/test_04_order.py#L40-L102)
- 数据夹具：[data_maker.py](file:///D:/PyCharm 2021.2.1/PythonProject/FarmMallTest/tool/data_maker.py)

---

## ~~BUG-002: 注册测试用例不可重复执行~~ ✅ 已修复

| 属性 | 详情 |
|------|------|
| **严重程度** | 🟡 Medium（中等） |
| **状态** | ✅ 已修复 |
| **所属模块** | 用户模块 |
| **测试用例** | `test_01_user.py::TestUser::test_03_user_reg` |

### 修复方案

1. 在 `user_reg.yaml` 中使用 `{{timestamp}}` 占位符，测试运行时自动替换为 `YYYYMMDDHHmmssffffff` 格式的唯一时间戳
2. 在 `data_maker.py` 中新增 `clean_user_by_username()` 函数，通过 `DELETE FROM users WHERE username = %s` 清理注册用户
3. 测试方法使用 `try...finally` 结构，无论成功失败都会在 finally 中调用清理函数
4. 测试开始前也会先清理一次，防止上次异常中断导致的残留数据

### 修复文件

- 测试代码：[test_01_user.py](file:///D:/PyCharm 2021.2.1/PythonProject/FarmMallTest/scripts/test_01_user.py#L40-L57)
- 清理函数：[data_maker.py](file:///D:/PyCharm 2021.2.1/PythonProject/FarmMallTest/tool/data_maker.py#L61-L70)
- 测试数据：[user_reg.yaml](file:///D:/PyCharm 2021.2.1/PythonProject/FarmMallTest/data/user_reg.yaml)

---

## 测试统计

| 统计项 | 第1轮 | 第2轮 | 第3轮 |
|--------|-------|-------|-------|
| 通过 | 23 | 22 | 22 |
| 失败 | 1 | 2 | 2 |
| 通过率 | 95.83% | 91.67% | 91.67% |
| 耗时 | 105s | 76s | 101s |

> 第2、3轮多出的 1 个失败即 BUG-002（注册重复），现已修复，下次运行预期 23 passed, 1 failed。

### 各模块通过情况（最新）

| 模块 | 用例数 | 通过 | 失败 |
|------|--------|------|------|
| 用户模块 (test_01) | 4 | 4 | 0 |
| 商品模块 (test_02) | 5 | 5 | 0 |
| 购物车模块 (test_03) | 3 | 3 | 0 |
| 订单模块 (test_04) | 6 | 5 | 1 |
| 管理员模块 (test_05) | 5 | 5 | 0 |
| 全链路 (test_06) | 1 | 1 | 0 |

*报告由自动化测试框架自动生成，可通过 Allure 报告查看详细执行记录和趋势分析。*