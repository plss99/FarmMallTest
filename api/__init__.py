# 公共变量
from config import TEST_ACCOUNTS

# 1.请求域名
host = "http://127.0.0.1:5000"
# 2.请求头
headers = {"content-type": "application/x-www-form-urlencoded"}
# 3.测试用商品/订单ID（由测试用例动态赋值）
product_id = None
order_id = None
# 4.全链路测试默认参数
default_keyword = "苹果"
default_receiver_name = "张三"
default_phone = "13800000000"
default_address = "北京市海淀区"
default_order_status = "已发货"
default_username = TEST_ACCOUNTS["default_user"]["username"]
default_password = TEST_ACCOUNTS["default_user"]["password"]
default_admin_username = TEST_ACCOUNTS["admin"]["username"]
default_admin_password = TEST_ACCOUNTS["admin"]["password"]