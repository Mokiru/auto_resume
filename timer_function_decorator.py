import time
import threading
from datetime import datetime

from datetime import time as dt_time


def deadline_decorator(func):
    """基于绝对时间点的装饰器"""

    def wrapper(*args, **kwargs):
        deadline_time = dt_time(20, 00, 00)
        if args[0] != '':
            hours, minutes, seconds = map(int, args[0].split(':'))
            deadline_time = dt_time(hours, minutes, seconds)

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
