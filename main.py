import random
import time

from DrissionPage import *
from DrissionPage.errors import ElementNotFoundError


def open_browser() -> Chromium:
    browser = Chromium()
    return browser


def click_element(page, xpath):
    ele = page.ele(xpath)
    ele.click()
    time.sleep(1)


def check_unread(ele) -> bool:
    """
    判断消息是否未读
    :param ele:
    :return:
    """
    red_ele = ele.ele('@class=badge-count badge-count-common-less')
    try:
        red_ele.rect()
        return True
    except ElementNotFoundError:
        return False


def proactive_resume(page):
    """
    处理主动打招呼后的简历
    :param page:
    :return:
    """
    click_element(page, 'xpath://*[@id="container"]/div[1]/div/div[2]/div[1]/div/div/div/div[7]/span')  # 点击我发起的
    click_element(page, 'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/span[2]')  # 点击未读
    time.sleep(random.uniform(5.0, 6.5))
    unread_list_ele = page.ele('xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]')  # 获取列表元素
    children_list = unread_list_ele.children()  # 获取子元素列表
    for ele in children_list:
        # 遍历子元素列表
        if not check_unread(ele):
            continue
        # 未读标识
        ele.click()
        dialog_ele = page.ele('xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]')  # 获取消息框元素
        message_list = dialog_ele.children(locator='对方想发送附件简历给您，您是否同意') # 找到发送简历元素
        for message_ele in message_list:
            # 遍历消息
            confirm_ele = message_ele.ele(locator='同意')
            try:
                confirm_ele.click()
            except ElementNotFoundError:
                continue


def run():
    browser = open_browser()
    page = browser.latest_tab  # 获取最新标签页
    page.get('https://www.zhipin.com/web/chat/index')  # 前往沟通页面
    # 等待登录
    ele = page.ele('登录')  # 查找是否有登录元素
    while True:
        try:
            _ = ele.rect
            time.sleep(1)  # 间隔1s
        except ElementNotFoundError:
            # 元素不存在说明是登录状态
            break
    # 进入主界面
    page.get('https://www.zhipin.com/web/chat/index')
    click_element(page, 'xpath://*[@id="wrap"]/div[1]/div/dl[4]/dt/a')  # 点击沟通
    proactive_resume(page)  # 第一步 收取主动打招呼的简历


if __name__ == '__main__':
    run()
