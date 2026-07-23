# 获取数据库信息
from tool.data_maker import get_db_conn


class GetDBInfo:
    @staticmethod
    def get_product_id_by_keyword(keyword):
        """通过关键词搜索商品名称，返回匹配的商品ID（返回 int）"""
        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM products WHERE name LIKE %s ORDER BY id DESC LIMIT 1",
                (f"%{keyword}%",)
            )
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if not result:
            raise Exception(f"未找到包含关键词 '{keyword}' 的商品")
        return int(result[0])

    @staticmethod
    def get_product_price(product_id):
        """获取商品价格（返回 float）"""
        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if not result:
            raise Exception(f"商品 ID {product_id} 不存在")
        return float(result[0])

    @staticmethod
    def get_product_stock(product_id):
        """获取商品库存（返回 int）"""
        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT stock FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if not result:
            raise Exception(f"商品 ID {product_id} 不存在")
        return int(result[0])

    @staticmethod
    def get_order_total(order_id):
        """获取订单总金额（返回 float）"""
        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT total_amount FROM orders WHERE id = %s", (order_id,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if not result:
            raise Exception(f"订单 ID {order_id} 不存在")
        return float(result[0])

    @staticmethod
    def get_product_status(product_id):
        """获取商品状态（返回 str）"""
        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if not result:
            raise Exception(f"商品 ID {product_id} 不存在")
        return result[0]

    @staticmethod
    def get_order_status(order_id):
        """获取订单状态（返回 str）"""
        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if not result:
            raise Exception(f"订单 ID {order_id} 不存在")
        return result[0]

    @staticmethod
    def get_order_id(username):
        """
        根据用户名获取该用户最新的一笔订单ID（按创建时间倒序）
        :param username: 用户名字符串
        :return: 订单ID（int），如果没有订单则返回 None
        """
        conn = get_db_conn()
        cursor = conn.cursor()
        try:
            # 1. 先查用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if not user:
                raise ValueError(f"用户 '{username}' 不存在")
            user_id = user[0]

            # 2. 查询该用户最新订单
            cursor.execute(
                "SELECT id FROM orders WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            result = cursor.fetchone()
            if not result:
                return None
            return result[0]
        finally:
            cursor.close()
            conn.close()