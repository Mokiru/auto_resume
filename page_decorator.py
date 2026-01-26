import threading
import time

from base_operates import click_element_by_ele, click_element
from simple_dialog import show_warning_dialog, safe_gui_call

captcha_status = {
    'captcha_status': False,
    'lock': threading.Lock(),
}


def _solve_over_say_hello_dialog(page, interrupt_check, stop_event):
    """
    处理因为打招呼超出数量出现的弹窗
    :param page:
    :return:
    """
    locator = r'@class=boss-popup__wrapper boss-dialog boss-dialog__wrapper business-block-dialog business-block-wrap circle'
    btn_locator = r'@class=icon-close'
    while not stop_event.is_set():
        _dialog_ele = page.ele(
            locator=locator,
            timeout=5)
        if _dialog_ele:
            # 超出限制
            interrupt_check['interrupt_check'] = True
            # 点击关闭
            _close_btn_ele = _dialog_ele.ele(locator=btn_locator)
            if not _close_btn_ele:
                print('未找到超出打招呼限制弹窗的关闭按钮')
                break
            else:
                try:
                    print('尝试关闭弹窗')
                    click_element_by_ele(page, _close_btn_ele)
                    print('关闭成功')
                except Exception:
                    print('关闭弹窗失败-重试')
                    continue
            interrupt_check['can_return'] = True
        time.sleep(0.1)


def say_call_dialog_solve(func):
    def wrapper(*args, **kwargs):
        page = args[0]  # 获取页面对象
        interrupt_check = {
            'interrupt_check': False,
            'can_return': False
        }
        # 处理弹窗

        stop_event = threading.Event()
        monitor_thread = threading.Thread(target=_solve_over_say_hello_dialog, args=(page, interrupt_check, stop_event),
                                          daemon=True)
        monitor_thread.start()
        try:
            result = func(*args, **kwargs, interrupt_check=interrupt_check)
            return result
        finally:
            stop_event.set()
            monitor_thread.join(timeout=2.0)

    return wrapper


def check_dialog_popup(page, locator, stop_event):
    while not stop_event.is_set():
        _error_ele = page.ele(locator=locator, timeout=2)
        if _error_ele:
            # 出现验证
            with captcha_status['lock']:
                captcha_status['captcha_status'] = True
            safe_gui_call(show_warning_dialog, '请处理验证')
            print('验证')
            while page.ele(locator=locator, timeout=2):
                time.sleep(1)
            with captcha_status['lock']:
                captcha_status['captcha_status'] = False
        else:
            time.sleep(0.2)
            continue


def popup_when_ele_existed(locator: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            page = args[0]  # 获取标签页
            stop_event = threading.Event()
            monitor_thread = threading.Thread(target=check_dialog_popup, args=(page, locator, stop_event), daemon=True)
            monitor_thread.start()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                stop_event.set()
                monitor_thread.join(timeout=2.0)

        return wrapper

    return decorator
