import os
import threading
import time
import traceback

from base_operates import open_browser, click_element, click_element_by_ele
from simple_dialog import get_global_root, safe_gui_call, popup_input
from timer_function_decorator import deadline_decorator

URL_LOGIN = 'https://lpt.liepin.com'
COMMUNICATION_URL = URL_LOGIN + "/chat/im"
COMMUNICATION_NEW_HELLO_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[1]/div[2]/div/div/div/label[2]'
COMMUNICATION_NO_READ_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[2]/aside/div[1]/div[3]/div/label/span[1]'
COMMUNICATION_PERSON_LIST_XPATH_PREFIX = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[2]/aside/div[2]/div[1]/div/div[{0}]'
COMMUNICATION_GET_RESUME_BUTTON_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[2]/div/div[2]/div[3]/div[1]/div[1]/div/div[1]/div/div[3]/span/span'
COMMUNICATION_CONFIRM_RESUME_BUTTON_FILTER = '@@class=ant-im-btn ant-im-btn-primary@@type=button'
COMMUNICATION_MESSAGE_BOX_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[2]/div/div[2]/div[2]/div[1]'

COMMUNICATION_INITIATED_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[1]/div[2]/div/div/div/label[3]'

USER_DATA_DIR = os.path.join(os.environ['APPDATA'], 'auto_resume', 'liepin')
PORT = 9223


def proactive_resume(page) -> None:
    """
    我主动发起的沟通 索要简历
    :param page: 标签页对象
    :return: None
    """
    page.get(COMMUNICATION_URL)  # 前往沟通界面
    click_element(page, COMMUNICATION_INITIATED_XPATH)  # 点击我发起的
    no_read_ele = page.ele(COMMUNICATION_NO_READ_XPATH)  # 获取未读框
    if no_read_ele.attr('class') != 'ant-im-checkbox ant-im-checkbox-checked':
        click_element_by_ele(page, no_read_ele)  # 需要点击未读
    person_index = 1
    while True:
        print('当前第{}个人'.format(person_index))
        person_ele = page.ele(COMMUNICATION_PERSON_LIST_XPATH_PREFIX.format(person_index),
                              timeout=5)  # 获取当前第person_index个人
        person_index += 1
        if not person_ele:  # 发送结束
            print('我发起的索要简历结束')
            break
        if person_ele.attr('class') != 'im-ui-contact-info':  # 跳过非目标
            continue
        click_element_by_ele(page, person_ele)  # 打开对话框
        # 判断是否触发注销或停用
        _cancel_btn_ele = page.ele(locator=COMMUNICATION_CONFIRM_RESUME_BUTTON_FILTER, timeout=5)
        if _cancel_btn_ele:
            print('对方已注销或停用')
            click_element_by_ele(page, _cancel_btn_ele)
            continue
        _message_box_ele = page.s_ele(COMMUNICATION_MESSAGE_BOX_XPATH)  # 获取消息框
        if not _message_box_ele:
            print('未找到消息框，跳过')
            continue
        _had_request_resume = _message_box_ele.ele('@text()=你已向对方索要简历')
        if _had_request_resume:
            print('已请求过简历')
            continue
        get_resume_button_ele = page.ele(COMMUNICATION_GET_RESUME_BUTTON_XPATH)  # 获取简历相关按钮
        if not get_resume_button_ele:
            print('未找到索要简历按钮')
            continue
        if get_resume_button_ele.text == '索要简历':
            click_element_by_ele(page, get_resume_button_ele)
            confirm_ele = page.ele(COMMUNICATION_CONFIRM_RESUME_BUTTON_FILTER)
            click_element_by_ele(page, confirm_ele)
        else:
            print('对方已发送简历或正在索要中')


def passive_resume(page) -> None:
    """
    他人主动打招呼 索要简历
    :param page: 标签页对象
    :return: None
    """
    page.get(COMMUNICATION_URL)  # 前往沟通界面
    click_element(page, COMMUNICATION_NEW_HELLO_XPATH)  # 点击新招呼
    no_read_ele = page.ele(COMMUNICATION_NO_READ_XPATH)  # 获取未读框
    if no_read_ele.attr('class') != 'ant-im-checkbox ant-im-checkbox-checked':
        click_element_by_ele(page, no_read_ele)  # 需要点击未读
    person_index = 1
    while True:
        print('当前第{}个人'.format(person_index))
        person_ele = page.ele(COMMUNICATION_PERSON_LIST_XPATH_PREFIX.format(person_index),
                              timeout=5)  # 获取当前第person_index个人
        person_index += 1
        if not person_ele:  # 发送结束
            print('新招呼索要简历结束')
            break
        if person_ele.attr('class') != 'im-ui-contact-info':  # 跳过非目标
            continue
        click_element_by_ele(page, person_ele)  # 打开对话框
        # 判断是否触发注销或停用
        _cancel_btn_ele = page.ele(locator=COMMUNICATION_CONFIRM_RESUME_BUTTON_FILTER, timeout=5)
        if _cancel_btn_ele:
            print('对方已注销或停用')
            click_element_by_ele(page, _cancel_btn_ele)
            continue
        _message_box_ele = page.s_ele(COMMUNICATION_MESSAGE_BOX_XPATH)  # 获取消息框
        if not _message_box_ele:
            print('未找到消息框，跳过')
            continue
        _had_request_resume = _message_box_ele.ele('@text()=你已向对方索要简历')
        if _had_request_resume:
            print('已请求过简历')
            continue
        get_resume_button_ele = page.ele(COMMUNICATION_GET_RESUME_BUTTON_XPATH)  # 获取简历相关按钮
        if not get_resume_button_ele:
            print('未找到索要简历按钮')
            continue
        if get_resume_button_ele.text == '索要简历':
            click_element_by_ele(page, get_resume_button_ele)
            confirm_ele = page.ele(COMMUNICATION_CONFIRM_RESUME_BUTTON_FILTER)
            click_element_by_ele(page, confirm_ele)
        else:
            print('对方已发送简历或正在索要中')


def do_chain(page):
    while True:
        proactive_resume(page)
        passive_resume(page)


@deadline_decorator
def run(_deadline_time: str):
    try:
        browser = open_browser(user_data_dir=USER_DATA_DIR, local_port=PORT)
    except FileNotFoundError:
        print("未找到浏览器路径，手动指定")
        browser = open_browser(safe_gui_call(popup_input, '请输入浏览器路径'), user_data_dir=USER_DATA_DIR,
                               local_port=PORT)
    page = browser.latest_tab  # 获取最新标签页
    page.get(URL_LOGIN)  # 前往登录界面
    # 等待登录
    while True:
        if page.ele('人才推荐'):
            break
        else:
            print('\r等待登录...')
            time.sleep(1)
    do_chain(page)


def prepare_run():
    _deadline_time = safe_gui_call(popup_input, '自动终止时间(24小时制),不填默认20:00:00')
    run(_deadline_time)


if __name__ == '__main__':
    try:
        root = get_global_root()
        main_thread = threading.Thread(target=prepare_run, daemon=True)
        main_thread.start()
        root.mainloop()
    except Exception as e:
        # 打印异常到控制台
        traceback.print_exc()
        # 阻塞等待按键
        if os.name == 'nt':  # Windows 下
            os.system('pause')
        else:  # Linux/Mac 可选
            input("\nPress <Enter> to quit...")
