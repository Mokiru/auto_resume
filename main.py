import os
import random
import time
import traceback
import tkinter as tk
from tkinter import simpledialog

from DrissionPage.errors import ElementNotFoundError

from base_operates import click_element, click_element_by_ele, open_browser
from operate_extensions import if_not_selected_click

COMMUNICATION_MESSAGE_CHAT_XPATH = r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]'


def check_unread(ele) -> bool:
    """
    判断消息是否未读
    :param ele:
    :return:
    """
    red_ele = ele.ele('@class=badge-count badge-count-common-less')
    if not red_ele:
        return False
    return True


def proactive_resume(page):
    """
    处理主动打招呼后的简历
    :param page:
    :return:
    """
    while True:
        wait_for_ele(page=page, xpath=r'xpath://*[@id="container"]/div[1]/div/div[2]/div[1]/div/div/div/div[7]',
                     funcs=[if_not_selected_click])  # 点击我发起
        while True:
            wait_for_ele(page=page,
                         xpath=r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/span[2]',
                         funcs=[click_element_by_ele])  # 点击未读
            time.sleep(random.uniform(1.0, 1.5))
            get_resume_key = {}
            list_first_ele = page.ele(
                r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]')
            if not list_first_ele:
                return
            index = 1
            while True:
                # 校验列表是否有元素
                list_item_ele = page.ele(
                    r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[' + str(
                        index) + ']', timeout=5)
                if not list_item_ele:
                    break
                index += 1
                key = list_item_ele.attr('key')
                if key in get_resume_key:
                    continue
                try:
                    click_element_by_ele(page, list_item_ele)
                    get_resume_key[key] = True
                    chat_message_ele = page.s_ele(
                        COMMUNICATION_MESSAGE_CHAT_XPATH,
                        timeout=5)  # 获取消息框元素
                    # if chat_message_ele.ele(locator='@class=message-dialog-icon resume-icon'):
                    if chat_message_ele.ele(locator='@text()=点击预览附件简历'):
                        # 发送过简历
                        continue
                    can_confirm = [0, False]
                    for _message_ele in chat_message_ele.children():
                        can_confirm[0] += 1
                        if not _message_ele.ele(locator='@class=message-dialog-icon message-dialog-icon-resume'):
                            continue
                        can_confirm[1] = True
                        break
                    if can_confirm[1]:
                        # 点击同意，接收简历
                        print('点击同意，接收简历')
                        _confirm_message = page.ele(locator=COMMUNICATION_MESSAGE_CHAT_XPATH, timeout=5).child(index=can_confirm[0])
                        _confirm_btn = _confirm_message.ele(locator='@@class=card-btn@@text()=同意')
                        click_element_by_ele(page, _confirm_btn)
                        continue
                    page.actions.type('方便发一份你的简历过来吗？\n')
                    time.sleep(random.uniform(1.0, 1.5))
                    click_element(page,
                                  r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/span[1]')  # 求简历
                    time.sleep(random.uniform(0.5, 1.5))
                    click_element(page,
                                  r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/span[2]')  # 确认
                    print("求简历")
                except ElementNotFoundError:
                    get_resume_key[key] = False
                    continue


def wait_for_ele(page, xpath, funcs: list = None):
    while True:
        _ele = page.ele(locator=xpath, timeout=5)
        if not _ele:
            print('元素不存在')
            continue
        else:
            break
    # 元素出现
    if funcs:
        for func in funcs:
            func(page, _ele)


def passive_resume(page):
    """
    新招呼
    :param page:
    :return:
    """
    while True:
        wait_for_ele(page=page, xpath=r'xpath://*[@id="container"]/div[1]/div/div[2]/div[1]/div/div/div/div[2]',
                     funcs=[if_not_selected_click])
        while True:
            wait_for_ele(page=page,
                         xpath=r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/span[2]',
                         funcs=[click_element_by_ele])  # 点击未读
            time.sleep(random.uniform(1.0, 1.5))
            get_resume_key = {}
            list_first_ele = page.ele(
                r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]')
            if not list_first_ele:
                return
            index = 1
            while True:
                list_item_ele = page.ele(
                    r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[' + str(
                        index) + ']', timeout=5)
                if not list_item_ele:
                    break
                index += 1
                key = list_item_ele.attr('key')
                if key in get_resume_key:
                    print("已获取过该简历")
                    continue
                try:
                    click_element_by_ele(page, list_item_ele)
                    get_resume_key[key] = True
                    chat_message_ele = page.s_ele(
                        COMMUNICATION_MESSAGE_CHAT_XPATH,
                        timeout=5)  # 获取消息框元素
                    resum_icon_ele = chat_message_ele.ele(locator='@class=message-dialog-icon resume-icon')
                    if resum_icon_ele:
                        print("当前已获取简历，跳过")
                        continue
                    page.actions.type('方便发一份你的简历过来吗？\n')
                    time.sleep(random.uniform(1.0, 1.5))
                    click_element(page,
                                  r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/span[1]')  # 求简历
                    time.sleep(random.uniform(0.5, 1.5))
                    click_element(page,
                                  r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/span[2]')  # 确认
                    print("求简历")
                except ElementNotFoundError:
                    get_resume_key[key] = False
                    continue


def popup_input(prompt: str = "请输入值") -> str | None:
    """弹出输入框，返回字符串或 None（点取消）"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.resizable(False, False)

    root.attributes('-topmost', True)  # 置顶
    user_input = simpledialog.askstring("输入", prompt, parent=root)
    root.destroy()
    return user_input


def run():
    try:
        browser = open_browser()
    except FileNotFoundError:
        print("未找到浏览器路径，手动指定")
        browser = open_browser(popup_input("请输入浏览器路径"))
    page = browser.latest_tab  # 获取最新标签页
    page.get('https://www.zhipin.com/web/chat/index')  # 前往沟通页面
    # 等待登录
    while True:
        try:
            ele = page.ele('新招呼')  # 查找是否有登录元素
            _ = ele.rect
            time.sleep(1)  # 间隔1s
            break
        except ElementNotFoundError:
            # 元素不存在说明非登录状态
            print('等待登录...')
            continue
    # 进入主界面
    page.get('https://www.zhipin.com/web/chat/index')
    click_element(page, r'xpath://*[@id="wrap"]/div[1]/div/dl[4]/dt/a')  # 点击沟通
    proactive_resume(page)  # 第一步 收取主动打招呼的简历
    passive_resume(page)  # 第二步处理新招呼 求简历


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        # 打印异常到控制台
        traceback.print_exc()
        # 阻塞等待按键
        if os.name == 'nt':  # Windows 下
            os.system('pause')
        else:  # Linux/Mac 可选
            input("\nPress <Enter> to quit...")
