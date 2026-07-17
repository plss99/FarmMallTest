# noinspection SqlNoDataSourceInspection,SqlResolve,PyUnresolvedReferences
# 数据库连接工具
from datetime import datetime
from decimal import Decimal

import pymysql
import pytest

# 连接数据库函数，返回数据库连接对象
def get_db_conn():
    from config import DB_CONFIG
    return pymysql.connect(**DB_CONFIG)

# 数据库断言工具
def db_assert(product_id, **expected):
    """
    验证 products 表中指定商品的字段值是否与期望一致
    :param product_id: 商品ID
    :param expected: 键值对，如 name='新名称', price=99.9, status='off'
    用法：
        db_assert(123, name='新名称', price=99.9, stock=50)    # 编辑后验证
        db_assert(123, status='off')                          # 下架后验证
        db_assert(123, name='原始名称')                         # 越权验证（期望不变）
    """
    conn = get_db_conn()  # 假设你已封装好数据库连接
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    row = cursor.fetchone()
    if not row:
        raise AssertionError(f"商品 ID {product_id} 不存在")

    # 获取列名并组装成字典
    columns = [desc[0] for desc in cursor.description]
    row_dict = dict(zip(columns, row))
    cursor.close()
    conn.close()

    # 逐字段断言
    for field, expected_value in expected.items():
        actual = row_dict.get(field)
        # 处理 Decimal 类型（数据库中的价格/库存可能为 Decimal）
        if isinstance(actual, Decimal):
            actual = float(actual)
        if actual != expected_value:
            raise AssertionError(
                f"字段 '{field}' 断言失败，期望: {expected_value}，实际: {actual}"
            )

# 清理数据库函数，删除订单数据
def clean_order_data(order_id):
    """通用清理：删除订单及明细"""
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
    cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    cursor.close()
    conn.close()

# 数据型夹具（造测试数据 + 自动清理）
@pytest.fixture
def active_product():
    """
    直接从数据库里拿一个已上架的商品 ID（不造新数据，只读）
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id,name FROM products WHERE status='active' ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not result:
        # 如果库里没数据，就报错
        raise ValueError("数据库中无上架商品，请先执行 init_db.py 初始化数据！")

    # 返回商品 ID
    yield  {"id": result[0],"name": result[1]}

# 卖家商品数据
@pytest.fixture
def my_product():
    """
    卖家自己的商品（用于编辑、上下架）
    在数据库里插入一条属于小农户的商品，返回 product_id
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO products(
                seller_id, category_id, name, 
                image, price, stock, 
                origin, description, status
                )
               VALUES (2, 1, '【夹具造数】测试苹果', 
               'uploads/default.svg', 19.9, 100, 
               '夹具产地', '仅供自动化测试', 'active'
               )
            """
        )
        conn.commit()
        product_id = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

    yield product_id

    # 清理测试数据
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# 构造库存只有1件的商品数据
@pytest.fixture
def stock_1_product():
    """库存只有1件的商品（专门用于测试超卖）"""
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO products(
                seller_id, category_id, name, 
                image, price, stock, origin, description, status)
               VALUES (2, 1, '【超卖测试专用】限量1件', 
               'uploads/default.svg', 99.9, 1, '测试产地', '仅剩1件，测并发','active')""")
        conn.commit()
        product_id = cursor.lastrowid
    finally:
        cursor.close()
        conn.close()
    yield product_id
    # 清理测试数据
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# 构造管理员订单
@pytest.fixture
def admin_order():
    """
    在数据库中创建一个属于 admin (user_id=1) 的订单，
    并返回订单ID。
    依赖：需要有一个商品存在（如果数据库为空，会自动创建一个占位商品）
    """
    conn = get_db_conn()
    cursor = conn.cursor()

    # 确保有一个商品可以关联到订单明细
    cursor.execute("SELECT id FROM products WHERE status='active' LIMIT 1")
    product = cursor.fetchone()
    if not product:
        # 如果没有商品，插入一个默认商品（seller_id=1 即admin）
        cursor.execute("""
            INSERT INTO products(seller_id, category_id, name, image, price, stock, origin, description, status)
            VALUES(1, 1, '管理员商品', 'uploads/default.svg', 10.0, 100, '测试产地', '夹具自动创建', 'active')
        """)
        conn.commit()
        product_id = cursor.lastrowid
    else:
        product_id = product[0]

    # 插入一笔订单，user_id = 1 (admin)
    order_no = datetime.now().strftime('%Y%m%d%H%M%S') + 'ADMIN'
    cursor.execute("""
        INSERT INTO orders(order_no, user_id, total_amount, receiver_name, phone, address, status)
        VALUES(%s, 1, 10.0, '管理员账户', '13800000000', '管理员地址', '待处理')
    """, (order_no,))
    conn.commit()
    order_id = cursor.lastrowid

    # 插入订单明细
    cursor.execute("""
        INSERT INTO order_items(order_id, product_id, seller_id, product_name, product_image, category_name, price, quantity, subtotal)
        VALUES(%s, %s, 1, '管理员商品', 'uploads/default.svg', '时令水果', 10.0, 1, 10.0)
    """, (order_id, product_id))
    conn.commit()
    cursor.close()
    conn.close()

    # 将订单ID返回给测试用例
    yield order_id

    # 清理该订单及明细
    clean_order_data(order_id)

# 构造小农户订单
@pytest.fixture
def user_order():
    """
    在数据库中创建一个属于小农户 (user_id=2) 的订单，
    状态为“待处理”，并返回订单ID。
    同时需要关联一个商品（该商品也属于小农户，以便库存回滚验证）
    """
    conn = get_db_conn()
    cursor = conn.cursor()

    # 确保有一个商品属于小农户 (seller_id=2)
    cursor.execute("SELECT id FROM products WHERE seller_id=2 AND status='active' LIMIT 1")
    product = cursor.fetchone()
    if not product:
        # 如果没有，插入一个
        cursor.execute("""
            INSERT INTO products(seller_id, category_id, name, image, price, stock, origin, description, status)
            VALUES(2, 1, '小农户商品', 'uploads/default.svg', 19.9, 100, '测试产地', '夹具自动创建', 'active')
        """)
        conn.commit()
        product_id = cursor.lastrowid
    else:
        product_id = product[0]

    # 插入一笔订单，user_id = 2 (小农户)
    order_no = datetime.now().strftime('%Y%m%d%H%M%S') + 'XNH'
    cursor.execute("""
        INSERT INTO orders(order_no, user_id, total_amount, receiver_name, phone, address, status)
        VALUES(%s, 2, 19.9, '小农户', '13900139000', '小农户地址', '待处理')
    """, (order_no,))
    conn.commit()
    order_id = cursor.lastrowid

    # 插入订单明细
    cursor.execute("""
        INSERT INTO order_items(order_id, product_id, seller_id, product_name, product_image, category_name, price, quantity, subtotal)
        VALUES(%s, %s, 2, '小农户商品', 'uploads/default.svg', '时令水果', 19.9, 1, 19.9)
    """, (order_id, product_id))
    conn.commit()
    cursor.close()
    conn.close()

    yield order_id

    # 清理该订单及明细
    clean_order_data(order_id)