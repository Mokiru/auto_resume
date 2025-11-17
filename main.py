import os
import random
import time
import traceback
import re

from DrissionPage.errors import ElementNotFoundError

from base_operates import click_element, click_element_by_ele, open_browser
from operate_extensions import if_not_selected_click
from page_decorator import say_call_dialog_solve, popup_when_ele_existed
from simple_dialog import popup_input, popup_multiple_multiselect, get_global_root
from timer_function_decorator import deadline_decorator

CAPTCHA_PAGE_LOCATOR = '@text()=您的账号可能存在异常访问行为'
MAIN_PAGE_AWESOME_PERSON_CONTAINER_XPATH = r'xpath://*[@id="container"]'  # 推荐牛人界面容器
MAIN_PAGE_AWESOME_PERSON_OVERFLOW_DIALOG_XPATH = r'xpath:/html/body/div[6]'  # 超出打招呼限制弹窗xpath
MAIN_PAGE_AWESOME_PERSON_CHAT_XPATH = r'xpath:/html/body/div[5]/div/div'  # 推荐牛人界面 右下角消息
MAIN_PAGE_AWESOME_PERSON_CHAT_SETTING_XPATH = r'xpath:/html/body/div[5]/div[2]/div[1]/div[1]/div/span[2]/span'  # 消息提醒设置xpath
MAIN_PAGE_AWESOME_PERSON_CHAT_SETTING_CONTAINER_XPATH = r'xpath:/html/body/div[5]/div[2]/div[1]/div[1]/div/span[2]/div/span[2]'  # 消息提醒开启切换按钮xpath
MAIN_PAGE_AWESOME_PERSON_XPATH = r'xpath://*[@id="wrap"]/div[1]/div/dl[2]'  # 主界面左侧菜单推荐牛人元素xpath
MAIN_PAGE_AWESOME_PERSON_SEARCH_LABEL_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[2]'  # 主界面点击推荐牛人后的职位筛选框xpath
MAIN_PAGE_AWESOME_PERSON_JOB_SEARCH_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[2]/div[2]/div[1]/input'  # 点击推荐牛人职位筛选框后出现的搜索框xpath
MAIN_PAGE_AWESOME_PERSON_JOB_LIST_INDEX_XPATH_FORMAT = r'xpath://*[@id="headerWrap"]/div/div/div[2]/div[2]/ul/li[{0}]'  # 职位列表
MAIN_PAGE_AWESOME_PERSON_JOB_LIST_FIRST_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[2]/div[2]/ul/li[1]'  # 点击推荐牛人职位筛选框后职位列表的第一个元素xpath
MAIN_PAGE_AWESOME_PERSON_LIST_CARD_XPATH = r'xpath://*[@id="recommend-list"]/div/ul/li[{0}]'  # 推荐牛人列表card-item format xpath
MAIN_PAGE_AWESOME_PERSON_LIST_SAY_HELLO_BTN_XPATH = r'xpath://*[@id="recommend-list"]/div/ul/li[{0}]/div/div[3]/div[3]/span/div/button'  # 点击推荐牛人后出现的牛人列表中打招呼format xpath
MAIN_PAGE_AWESOME_PERSON_FILTER_LABEL_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div/div'  # 推荐牛人中筛选xpath
MAIN_PAGE_AWESOME_PERSON_FILTER_WRAP_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[1]'  # 筛选界面
MAIN_PAGE_AWESOME_PERSON_FILTER_VIP_ITEM_XPATH_FORMAT = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[1]/div[1]/div[2]/div[{0}]'  # VIP筛选项元素
MAIN_PAGE_AWESOME_PERSON_FILTER_FIX_VIP_ITEM_XPATH_FORMAT = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[1]/div[1]/div[3]/div[{0}]'  # VIP筛选项元素
MAIN_PAGE_AWESOME_PERSON_FILTER_NORMAL_ITEM_XPATH_FORMAT = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[1]/div[2]/div[{0}]'  # 普通筛选项元素
MAIN_PAGE_AWESOME_PERSON_FILTER_WRAP_CONFIRM_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[2]/div[2]'  # 筛选界面确认按钮xpath
MAIN_PAGE_COMMUNICATION_MESSAGE_CHAT_XPATH = r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]'  # 沟通中的消息对话框xpath
MAIN_PAGE_COMMUNICATION_XPATH = r'xpath://*[@id="wrap"]/div[1]/div/dl[4]'


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
                        MAIN_PAGE_COMMUNICATION_MESSAGE_CHAT_XPATH,
                        timeout=5)  # 获取消息框元素
                    # if chat_message_ele.ele(locator='@class=message-dialog-icon resume-icon'):
                    if chat_message_ele.ele(locator='@text()=点击预览附件简历', timeout=2):
                        # 发送过简历
                        print('对方已经发送简历')
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
                        _confirm_message = page.ele(locator=MAIN_PAGE_COMMUNICATION_MESSAGE_CHAT_XPATH,
                                                    timeout=5).child(index=can_confirm[0])
                        _confirm_btn = _confirm_message.ele(locator='@@class=card-btn@@text()=同意')
                        click_element_by_ele(page, _confirm_btn)
                        continue
                    if chat_message_ele.ele(locator='@text()=方便发一份你的简历过来吗？', timeout=2):
                        print('当前已经请求简历，但对方未发送')
                        continue
                    page.actions.type('方便发一份你的简历过来吗？\n')
                    time.sleep(random.uniform(1.0, 1.5))
                    click_element(page,
                                  r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/span[1]')  # 求简历
                    time.sleep(random.uniform(0.5, 1.5))
                    click_element(page,
                                  r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/span[2]')  # 确认
                    print("求简历")
                except Exception:
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
                        MAIN_PAGE_COMMUNICATION_MESSAGE_CHAT_XPATH,
                        timeout=5)  # 获取消息框元素
                    if chat_message_ele.ele(locator='@class=message-dialog-icon resume-icon',
                                            timeout=2) or chat_message_ele.ele(
                        locator='@text()=方便发一份你的简历过来吗？', timeout=2):
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
                except Exception:
                    get_resume_key[key] = False
                    continue


@say_call_dialog_solve
def say_hello(page, job_input: str, filter_input: str, interrupt_check=None):
    """
    打招呼
    :param page:
    :param job_input: 示例 产品经理-26届校招(J15116) _ 北京  10-15K
    :param filter_input:
    :param interrupt_check: 中断标识
    :return:
    """
    _job_list = job_input.split(';') if job_input != '' else []
    _filter_list = filter_input.split(';') if filter_input != '' else []  # 筛选条件
    wait_for_ele(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_XPATH, funcs=[click_element_by_ele])  # 点击推荐牛人
    for _job_txt in _job_list:
        try:
            click_element(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_SEARCH_LABEL_XPATH)  # 点击职位筛选框
            click_element(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_JOB_SEARCH_XPATH)  # 点击搜索输入框
            page.actions.type(_job_txt)
            click_element(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_JOB_LIST_FIRST_XPATH)  # 点击搜索结果的职位
            click_element(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_FILTER_LABEL_XPATH)  # 点击筛选条件框
            _filter_wrap_ele = page.ele(locator=MAIN_PAGE_AWESOME_PERSON_FILTER_WRAP_XPATH, timeout=5)  # 获取筛选界面容器元素
            for _filter in _filter_list:
                click_element_by_ele(page, _filter_wrap_ele.ele(locator='@text()={0}'.format(_filter)))  # 点击筛选条件
            click_element(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_FILTER_WRAP_CONFIRM_XPATH)  # 点击确认
            time.sleep(random.uniform(1.5, 2.0))  # 等待搜索结果
            index = 1  # 从列表开始
            while True:
                if interrupt_check['interrupt_check']:
                    # 超出限制 需要终止
                    print('牛人打招呼已打满')
                    while True:
                        if interrupt_check['can_return']:
                            return
                        else:
                            time.sleep(1)
                            continue
                _card_ele = page.ele(
                    locator=MAIN_PAGE_AWESOME_PERSON_LIST_CARD_XPATH.format(index), timeout=5)  # 获取卡片元素
                if not _card_ele:
                    # 当前职位已经没有推荐牛人
                    page.actions.scroll(delta_y=2000)  # 滑动到底部
                    _card_ele = page.ele(
                        locator=MAIN_PAGE_AWESOME_PERSON_LIST_CARD_XPATH.format(index), timeout=10)
                    if not _card_ele:
                        print('当前职位已经没有推荐牛人')
                        break
                _say_hello_ele = _card_ele.ele(locator='xpath:div/div[3]/div[3]/span/div/button', timeout=2)
                index += 1
                if not _say_hello_ele:
                    print('say_hello not found')
                    continue
                try:
                    click_element_by_ele(page, _say_hello_ele)  # 点击打招呼
                except Exception:
                    print("打招呼失败")
                    continue
        except Exception:
            print('当前职位打招呼失败{0}'.format(_job_txt))
            continue


def close_message_information(page):
    """
    关闭消息提醒
    :param page:
    :return:
    """
    wait_for_ele(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_CHAT_XPATH, funcs=[click_element_by_ele])
    click_element(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_CHAT_SETTING_XPATH)  # 点击设置
    _switch_ele = page.ele(locator=MAIN_PAGE_AWESOME_PERSON_CHAT_SETTING_CONTAINER_XPATH, timeout=5)  # 获取设置界面容器元素
    if _switch_ele and _switch_ele.attr('class') == 'ui-switch ui-switch-checked':
        click_element_by_ele(page, _switch_ele)
        print("已关闭消息提醒")


def get_position_list(page):
    """
    获取当前账号的职位列表
    :param page:
    :return: 职位列表
    """
    result = []
    wait_for_ele(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_SEARCH_LABEL_XPATH, funcs=[click_element_by_ele])
    index = 1
    while True:
        _job_ele = page.ele(locator=MAIN_PAGE_AWESOME_PERSON_JOB_LIST_INDEX_XPATH_FORMAT.format(index), timeout=2)
        if not _job_ele:
            break
        result.append(re.search(r'</u>(.*?)</span>', _job_ele.html).group(1))
        index += 1
    return result


def get_filter_option_list(page, format_str):
    """
    获取筛选项option
    :param page:
    :param format_str:
    :return:
    """
    index = 1
    result = []
    while True:
        _filter_item_ele = page.ele(locator=format_str.format(index), timeout=2)
        if not _filter_item_ele:
            break
        index += 1
        if _filter_item_ele.attr('class') == 'filter-item age':
            continue
        _options = _filter_item_ele.eles(locator='@class=option')
        for _option_ele in _options:
            result.append(_option_ele.raw_text)
    return result


def get_filter_list(page):
    """
    获取筛选条件列表
    :param page:
    :return:
    """
    result = []
    wait_for_ele(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_FILTER_LABEL_XPATH, funcs=[click_element_by_ele])  # 点击筛选按钮
    result += get_filter_option_list(page, MAIN_PAGE_AWESOME_PERSON_FILTER_VIP_ITEM_XPATH_FORMAT)
    result += get_filter_option_list(page, MAIN_PAGE_AWESOME_PERSON_FILTER_FIX_VIP_ITEM_XPATH_FORMAT)
    result += get_filter_option_list(page, MAIN_PAGE_AWESOME_PERSON_FILTER_NORMAL_ITEM_XPATH_FORMAT)
    # return ['刚刚活跃', '今日活跃', '本周活跃', '本月活跃', '男', '女', '近14天没有', '近一个月没有', '985', '211',
    #         '双一流院校', '留学', '国内外名校', '公办本科', '5年少于3份', '平均每份工作大于1年', '在校/应届',
    #         '25年毕业', '26年毕业', '26年']
    print(result)
    return result


@popup_when_ele_existed(locator=CAPTCHA_PAGE_LOCATOR)
def do_chain(page):
    page.get('https://www.zhipin.com/web/chat/recommend')  # 推荐牛人界面
    _job_input, _filter_input = popup_multiple_multiselect(
        ["请输入职位名称,多个职位使用;(英文输入法)分隔", "请输入职位筛选条件,多个条件使用;(英文输入法)分隔"],
        [get_position_list(page), get_filter_list(page)])
    print(_job_input, _filter_input)
    # 进入主界面
    close_message_information(page)  # 关闭消息提醒
    say_hello(page, _job_input, _filter_input)  # 第一步 打招呼
    click_element(page=page, xpath=MAIN_PAGE_COMMUNICATION_XPATH)  # 点击沟通
    proactive_resume(page)  # 第二步 收取主动打招呼的简历
    passive_resume(page)  # 第三步 处理新招呼 求简历


@deadline_decorator
def run(_deadline_time: str):
    try:
        browser = open_browser()
    except FileNotFoundError:
        print("未找到浏览器路径，手动指定")
        browser = open_browser(popup_input("请输入浏览器路径"))
    page = browser.latest_tab  # 获取最新标签页
    page.get('https://www.zhipin.com/web/chat/recommend')  # 前往推荐牛人
    # 等待登录
    while True:
        try:
            ele = page.ele('推荐牛人')  # 查找是否有登录元素
            _ = ele.rect
            time.sleep(1)  # 间隔1s
            break
        except ElementNotFoundError:
            # 元素不存在说明非登录状态
            print('等待登录...')
            continue
    do_chain(page)


def prepare_run():
    _deadline_time = popup_input('自动终止时间(24小时制),不填默认20:00:00')
    run(_deadline_time)


if __name__ == '__main__':
    try:
        root = get_global_root()
        prepare_run()
    except Exception as e:
        # 打印异常到控制台
        traceback.print_exc()
        # 阻塞等待按键
        if os.name == 'nt':  # Windows 下
            os.system('pause')
        else:  # Linux/Mac 可选
            input("\nPress <Enter> to quit...")
