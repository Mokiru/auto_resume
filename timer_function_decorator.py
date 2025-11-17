import time
import threading
from functools import wraps
from datetime import datetime


def deadline_decorator(deadline_time):
    """基于绝对时间点的装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def check_deadline():
                while True:
                    current_time = datetime.now().time()
                    if current_time >= deadline_time:
                        print(f"🕒 到达截止时间 {deadline_time}，终止程序")
                        # 强制终止进程
                        import os
                        os._exit(1)
                    time.sleep(1)  # 每秒检查一次

            # 启动后台检查线程
            monitor_thread = threading.Thread(target=check_deadline, daemon=True)
            monitor_thread.start()

            return func(*args, **kwargs)

        return wrapper

    return decorator