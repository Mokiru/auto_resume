import os
import random
import time
import traceback
import re
import threading
from datetime import datetime

from base_operates import click_element, click_element_by_ele, open_browser, browser_mouse_move, read_or_create_ini, \
    update_ini_value
from operate_extensions import if_not_selected_click
from page_decorator import say_call_dialog_solve, popup_when_ele_existed, captcha_status
from simple_dialog import popup_input, get_global_root, popup_mixed_inputs, safe_gui_call
from timer_function_decorator import deadline_decorator

CAPTCHA_PAGE_LOCATOR = r'@class=wrap-verify-slider'
MAIN_PAGE_AWESOME_PERSON_CONTAINER_XPATH = r'xpath://*[@id="container"]'  # 推荐牛人界面容器
MAIN_PAGE_AWESOME_PERSON_OVERFLOW_DIALOG_XPATH = r'xpath:/html/body/div[6]'  # 超出打招呼限制弹窗xpath
MAIN_PAGE_AWESOME_PERSON_CHAT_XPATH = r'@class=chat-global-entry'  # 推荐牛人界面 右下角消息
MAIN_PAGE_AWESOME_PERSON_CHAT_SETTING_XPATH = r'@class=setting'  # 消息提醒设置xpath
MAIN_PAGE_AWESOME_PERSON_CHAT_SETTING_CONTAINER_XPATH = r'@class=ui-switch ui-switch-checked'  # 消息提醒开启切换按钮xpath
MAIN_PAGE_AWESOME_PERSON_FILTER_EXPAND = '@class=vip-folded'  # 展开近期未看/活跃/院校等选项
MAIN_PAGE_AWESOME_PERSON_XPATH = r'xpath://*[@id="wrap"]/div[1]/div/dl[2]'  # 主界面左侧菜单推荐牛人元素xpath
MAIN_PAGE_AWESOME_PERSON_HEADER_WRAP_LOCATION = r'xpath://*[@id="headerWrap"]'  # headerWrap
MAIN_PAGE_AWESOME_PERSON_SEARCH_LABEL_LOCATION = r'@|class=ui-dropmenu ui-dropmenu-visible ui-dropmenu-label-arrow ui-dropmenu-drop-arrow job-selecter-wrap expanding@|class=ui-dropmenu ui-dropmenu-label-arrow ui-dropmenu-drop-arrow job-selecter-wrap'  # 主界面点击推荐牛人后的职位筛选框
MAIN_PAGE_AWESOME_PERSON_JOB_SEARCH_LOCATION = r'@@class=ipt chat-job-search@@placeholder=请输入职位名称'  # 点击推荐牛人职位筛选框后出现的搜索框xpath
MAIN_PAGE_AWESOME_PERSON_JOB_LIST_LOCATION = r'@class=job-list'  # 职位列表
MAIN_PAGE_AWESOME_PERSON_JOB_LIST_FIRST_XPATH = r'xpath:/li[1]'  # 相对职位列表，第li元素
MAIN_PAGE_AWESOME_PERSON_LIST_CARD_XPATH = r'xpath://*[@id="recommend-list"]/div/ul/li[{0}]/div'  # 推荐牛人列表card-item format xpath
MAIN_PAGE_AWESOME_PERSON_LIST_SAY_HELLO_BTN_XPATH = r'xpath://*[@id="recommend-list"]/div/ul/li[{0}]/div/div[3]/div[3]/span/div/button'  # 点击推荐牛人后出现的牛人列表中打招呼format xpath
MAIN_PAGE_AWESOME_PERSON_FILTER_LABEL_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div/div'  # 推荐牛人中筛选xpath
MAIN_PAGE_AWESOME_PERSON_FILTER_WRAP_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[1]'  # 筛选界面
MAIN_PAGE_AWESOME_PERSON_FILTER_VIP_ITEM_XPATH_FORMAT = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[1]/div[1]/div[2]/div[{0}]'  # VIP筛选项元素
MAIN_PAGE_AWESOME_PERSON_FILTER_FIX_VIP_ITEM_XPATH_FORMAT = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[1]/div[1]/div[3]/div[{0}]'  # VIP筛选项元素
MAIN_PAGE_AWESOME_PERSON_FILTER_NORMAL_ITEM_XPATH_FORMAT = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[1]/div[2]/div[{0}]'  # 普通筛选项元素
MAIN_PAGE_AWESOME_PERSON_FILTER_WRAP_CONFIRM_XPATH = r'xpath://*[@id="headerWrap"]/div/div/div[4]/div/div[2]/div[2]/div[2]'  # 筛选界面确认按钮xpath
MAIN_PAGE_COMMUNICATION_MESSAGE_CHAT_XPATH = r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]'  # 沟通中的消息对话框xpath
MAIN_PAGE_COMMUNICATION_XPATH = r'xpath://*[@id="wrap"]/div[1]/div/dl[4]'
MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FIRST_ITEM_XPATH = r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]'
MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FILTER_NO_READ_XPATH = r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/span[2]'
MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FILTER_ALL_XPATH = r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/span[1]'
EXTENSION_BS_XPATH = r'xpath://*[@id="talentEyeIcon"]'  # 北森插件xpath

URL_LOGIN = 'https://www.zhipin.com/web/user/?ka=bticket'
URL_AWESOME = 'https://www.zhipin.com/web/chat/recommend'
URL_COMMUNICATION = 'https://www.zhipin.com/web/chat/index'

TIME_PATTERN = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'

USER_DATA_DIR = os.path.join(os.environ['APPDATA'], 'auto_resume', 'boss')
CONFIG_INI_PATH = os.path.join(os.environ['APPDATA'], 'auto_resume', 'boss.ini')
DEFAULT_CONFIG = {
    'default': {
        'created': 'True'
    },
    'deadline': {
        'time': '20:00:00'
    },
    'common_phrases': {
        'greetings': '方便发一份你的简历过来吗？'
    }
}
PORT = 9222


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


def proactive_resume(page, common_greeting):
    """
    处理主动打招呼后的简历
    :param page:
    :param common_greeting:
    :return:
    """
    if page.url != URL_COMMUNICATION:
        page.get(URL_COMMUNICATION)
    wait_for_ele(page=page, xpath=r'xpath://*[@id="container"]/div[1]/div/div[2]/div[1]/div/div/div/div[3]',
                 funcs=[if_not_selected_click])  # 点击我发起
    wait_for_ele(page=page,
                 xpath=MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FILTER_NO_READ_XPATH,
                 funcs=[click_element_by_ele])  # 点击未读
    time.sleep(random.uniform(1.0, 1.5))
    get_resume_key = {}
    list_first_ele = page.ele(
        MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FIRST_ITEM_XPATH)
    if not list_first_ele:
        with captcha_status['lock']:
            if captcha_status['captcha_status']:
                # 当前正在处理验证
                return
        return
    index = 1
    while True:
        with captcha_status['lock']:
            if captcha_status['captcha_status']:
                # 当前正在处理验证
                break
        # 校验列表是否有元素
        list_item_ele = page.ele(
            r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[' + str(
                index) + ']', timeout=4)
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
            if chat_message_ele.ele(locator='@text():方便发一份你的简历过来吗', timeout=2):
                print('当前已经请求简历，但对方未发送')
                continue
            page.actions.type(common_greeting).type('\n')
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


def passive_resume(page, common_greeting):
    """
    新招呼
    :param page:
    :param common_greeting:
    :return:
    """
    if page.url != URL_COMMUNICATION:
        page.get(URL_COMMUNICATION)
    wait_for_ele(page=page, xpath=r'xpath://*[@id="container"]/div[1]/div/div[2]/div[1]/div/div/div/div[2]',
                 funcs=[if_not_selected_click])
    wait_for_ele(page=page,
                 xpath=MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FILTER_NO_READ_XPATH,
                 funcs=[click_element_by_ele])  # 点击未读
    time.sleep(random.uniform(1.0, 1.5))
    get_resume_key = {}
    list_first_ele = page.ele(
        MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FIRST_ITEM_XPATH)
    if not list_first_ele:
        with captcha_status['lock']:
            if captcha_status['captcha_status']:
                # 当前正在处理验证
                return
        print('当前消息列表为空')
        return
    index = 1
    while True:
        with captcha_status['lock']:
            if captcha_status['captcha_status']:
                # 正在处理验证需要退出 重新进入
                break
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
                locator='@text():方便发一份你的简历过来吗', timeout=2):
                print("当前已获取简历，跳过")
                continue
            page.actions.type(common_greeting).type('\n')
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


def get_resume_in_had_resume(page, init_resume):
    """
    已获取简历 点击
    :param page:
    :param init_resume:
    :return:
    """
    if page.url != URL_COMMUNICATION:
        page.get(URL_COMMUNICATION)
    wait_for_ele(page=page, xpath=r'@title=已获取简历',
                 funcs=[if_not_selected_click])
    # if init_resume == 1:
    #     print('已获取简历-未读')
    #     wait_for_ele(page=page,
    #                  xpath=r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/span[2]',
    #                  funcs=[click_element_by_ele])  # 点击未读
    print('已获取简历-全部')
    wait_for_ele(page=page,
                 xpath=MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FILTER_ALL_XPATH,
                 funcs=[click_element_by_ele])  # 点击全部
    list_first_ele = page.ele(
        MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FIRST_ITEM_XPATH)
    if not list_first_ele:
        with captcha_status['lock']:
            if captcha_status['captcha_status']:
                # 当前正在处理验证
                return
        print('当前消息列表为空')
        return
    index = 1
    _check_map = {}  # 存储已经点击过的key
    list_item_ele = page.ele(MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FIRST_ITEM_XPATH,
                             timeout=5)
    if not list_item_ele:
        print('列表没有简历-1')
        return
    _list_first_key = list_item_ele.attr('key')  # 获取当前列表第一个key
    while True:
        with captcha_status['lock']:
            if captcha_status['captcha_status']:
                # 正在处理验证需要退出 重新进入
                break
        _list_first_item_ele = page.ele(
            MAIN_PAGE_COMMUNICATION_MESSAGE_LIST_FIRST_ITEM_XPATH,
            timeout=5)
        if not _list_first_item_ele:
            print('列表没有简历-2')
            break
        _first_key = _list_first_item_ele.attr('key')
        if _first_key != _list_first_key:
            # 当前翻页了 下标需要相对偏移
            _first_item_index = _check_map.get(_first_key, 0)  # 获取当前列表第一个key的index
            index = index - _first_item_index + 1  # 正确下标
            _list_first_key = _first_key
        _list_item_ele = page.ele(
            r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[' + str(
                index) + ']', timeout=5)
        if not _list_item_ele:
            break
        index += 1
        _item_key = _list_item_ele.attr('key')
        if _item_key in _check_map:
            continue
        _check_map[_item_key] = index - 1
        if init_resume == 1 and not check_today(_list_item_ele):
            # 非第一次遍历且不是今日消息
            continue
        try:
            click_element_by_ele(page, _list_item_ele)
        except Exception:
            continue


def check_today(page):
    """
    校验列表span是否是今日消息
    :param page:
    :return:
    """
    time_span_ele = page.ele(r'xpath:/div/div/div[2]/div/span')
    _time_text = time_span_ele.text.strip('"\'').strip()
    if re.match(TIME_PATTERN, _time_text):
        try:
            datetime.strptime(_time_text, '%H:%M')
            return True
        except ValueError:
            return False
    return False


def check_bs_extension_exist(page) -> bool:
    """
    判断指定页面是否存在北森插件
    :param page:
    :return:
    """
    return page.ele(EXTENSION_BS_XPATH, timeout=5)


@say_call_dialog_solve
def say_hello(page, person_input: list[int], job_input: list[list[str]], filter_input: list[list[str]],
              desired_input: list[list[str]], age_input: list[list[str]],
              interrupt_check=None):
    """
    打招呼
    :param page:
    :param person_input: 打招呼人数
    :param job_input: 示例 ['产品经理-26届校招(J15116) _ 北京  10-15K']
    :param filter_input: 筛选条件
    :param desired_input: 期望职位筛选
    :param age_input: 年龄筛选
    :param interrupt_check: 中断标识
    :return:
    """
    wait_for_ele(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_XPATH, funcs=[click_element_by_ele])  # 点击推荐牛人
    _bs_extension_exist = check_bs_extension_exist(page)
    for i in range(len(job_input)):
        _current_job_index = 0
        while _current_job_index < len(job_input[i]):  # 遍历当前筛选项对应的职位列表
            if interrupt_check['interrupt_check']:
                # 超出限制 需要终止
                print('牛人打招呼已打满')
                while True:
                    if interrupt_check['can_return']:
                        return
                    else:
                        time.sleep(1)
                        continue
            _job_txt = job_input[i][_current_job_index]  # 职位名称
            person_num = person_input[i]  # 打招呼人数
            try:
                _header_wrap_ele = page.ele(locator=MAIN_PAGE_AWESOME_PERSON_HEADER_WRAP_LOCATION,
                                            timeout=5)  # 获取推荐牛人界面 头部栏元素
                _search_label_ele = _header_wrap_ele.ele(locator=MAIN_PAGE_AWESOME_PERSON_SEARCH_LABEL_LOCATION,
                                                         timeout=3)  # 头部栏中的职位框
                click_element_by_ele(page, _search_label_ele)  # 点击职位框
                _search_label_input_ele = _header_wrap_ele.ele(locator=MAIN_PAGE_AWESOME_PERSON_JOB_SEARCH_LOCATION,
                                                               timeout=3)  # 获取头部栏中职位框中的搜索框
                click_element_by_ele(page, _search_label_input_ele)  # 点击搜索输入框
                page.actions.type(_job_txt)  # 输入职位名称
                _search_result_list_ele = _header_wrap_ele.ele(locator=MAIN_PAGE_AWESOME_PERSON_JOB_LIST_LOCATION,
                                                               timeout=3)  # 获取搜索后的结果列表
                _truth_search_result_ele = _search_result_list_ele.ele(
                    locator=MAIN_PAGE_AWESOME_PERSON_JOB_LIST_FIRST_XPATH, timeout=3)  # 列表中的第一个元素
                click_element_by_ele(page, _truth_search_result_ele)  # 点击第一个元素
                if len(filter_input[i]) > 0 and filter_input[i][0] != '':
                    click_element(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_FILTER_LABEL_XPATH)  # 点击筛选条件框
                    _expand_filter = page.ele(locator=MAIN_PAGE_AWESOME_PERSON_FILTER_EXPAND, timeout=3)  # 获取 展开元素
                    if _expand_filter:
                        click_element_by_ele(page, _expand_filter)  # 如果需要展开则点击
                    _filter_wrap_ele = page.ele(locator=MAIN_PAGE_AWESOME_PERSON_FILTER_WRAP_XPATH,
                                                timeout=5)  # 获取筛选界面容器元素
                    if not _filter_wrap_ele:
                        print('未找到筛选界面-尝试刷新页面后获取')
                        page.refresh()
                        continue
                    for _filter in filter_input[i]:
                        _target_filter_ele = _filter_wrap_ele.ele(locator='@@class=option@@text():{0}'.format(_filter))
                        if not _target_filter_ele:
                            _target_filter_ele = _filter_wrap_ele.ele(
                                locator='@@class=name@@text()={0}'.format(_filter))
                            if not _target_filter_ele:
                                print(f'未找到筛选条件：{_filter}')
                        click_element_by_ele(page, _target_filter_ele)  # 点击筛选条件
                        if interrupt_check['interrupt_check']:
                            # 非vip
                            print('当前账号非vip，无法选择vip筛选项')
                            while True:
                                if interrupt_check['can_return']:
                                    break
                                else:
                                    time.sleep(1)
                                    continue
                            interrupt_check['interrupt_check'] = False
                            interrupt_check['can_return'] = False
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
                        _job_select_ele = _header_wrap_ele.ele(locator=MAIN_PAGE_AWESOME_PERSON_SEARCH_LABEL_LOCATION,
                                                               timeout=2)
                        browser_mouse_move(page, _job_select_ele.rect.location)
                        page.actions.scroll(delta_y=10000)  # 滑动到底部
                        _card_ele = page.ele(
                            locator=MAIN_PAGE_AWESOME_PERSON_LIST_CARD_XPATH.format(index), timeout=10)
                        if not _card_ele:
                            print('当前职位已经没有推荐牛人')
                            break
                    _no_match_ele = _card_ele.ele(locator='@class=recommend-mome-ui', timeout=1)  # 获取无匹配结果元素
                    if _no_match_ele:
                        print('当前职位已经没有推荐牛人')
                        break
                    index += 1
                    if _card_ele.attr('class') == 'similar-geek-wrap':
                        # 跳过相似推荐
                        continue
                    _desired_ele = _card_ele.ele(locator='xpath:div[1]/div[2]/div[3]/span[2]/div')
                    can_say_hello = False
                    if _desired_ele:
                        _desired_txt = _desired_ele.text
                        for _desired in desired_input[i]:
                            if _desired in _desired_txt:
                                can_say_hello = True
                                break
                    else:
                        print('未找到期望职位元素')
                        continue
                    if not can_say_hello:
                        print('当前职位期望职位不符')
                        continue
                    _age_ele = _card_ele.ele(locator='xpath:div[1]/div[2]/div[2]/div')
                    if _age_ele:
                        _age = int(re.search(r'(\d{1,3})岁', _age_ele.text).group(1))
                        if _age < int(age_input[i][0]) or _age > int(age_input[i][1]):
                            print('当前职位年龄不符')
                            continue
                    _say_hello_ele = _card_ele.ele(locator='@class=btn btn-greet', timeout=2)
                    if not _say_hello_ele:
                        print("当前职位没有推荐牛人")
                        continue
                    # 北森插件简历查重
                    if _bs_extension_exist:
                        # 存在北森插件，则点击人选
                        click_element_by_ele(page, _age_ele) # 通过点击年龄信息打开简历
                        click_element(page, EXTENSION_BS_XPATH) # 点击插件
                        _res_ele = page.ele(locator='@|text()=系统发现疑似简历@|text()=未发现重复或疑似简历', timeout=10)
                        if _res_ele and _res_ele.text == '系统发现疑似简历':
                            print('当前职位有疑似简历')
                            continue
                    try:
                        print('{0}职位将打招呼{1}人'.format(_job_txt, person_input[
                            i] - person_num + 1))  # fix-可能点击与限制弹窗出现次序问题，如 点击-弹窗关闭-成功打招呼日志输出(该成功只能说明点击成功而不能说明真正打招呼成功即超出限制) 顺序问题
                        click_element_by_ele(page, _say_hello_ele)  # 点击打招呼
                        person_num -= 1
                        print('{0}职位已打招呼{1}人'.format(_job_txt, person_input[i] - person_num))
                        if person_num <= 0:
                            print('{0}职位打招呼结束'.format(_job_txt))
                            break
                        time.sleep(random.uniform(1.5, 2.0))  # 等待打招呼页面加载 fix-可能打完招呼后页面会刷新加入相似推荐卡片在列表中
                    except Exception:
                        print("打招呼失败")
                        continue
                _current_job_index += 1
            except Exception as ex:
                traceback.print_exc()
                with captcha_status['lock']:
                    if not captcha_status['captcha_status']:
                        _current_job_index += 1
                        print('当前职位打招呼中断{0}'.format(_job_txt))
                        continue
                # 当前正在处理验证
                wait_for_ele(page=page, xpath=MAIN_PAGE_AWESOME_PERSON_XPATH,
                             funcs=[click_element_by_ele])  # 点击推荐牛人
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
    if _switch_ele:
        click_element_by_ele(page, _switch_ele)
        print("已关闭消息提醒")


def get_position_list(page):
    """
    获取当前账号的职位列表
    :param page:
    :return: 职位列表
    """
    result = []
    _header_wrap_ele = page.ele(locator=MAIN_PAGE_AWESOME_PERSON_HEADER_WRAP_LOCATION, timeout=10)
    _selector_ele = _header_wrap_ele.ele(locator=MAIN_PAGE_AWESOME_PERSON_SEARCH_LABEL_LOCATION)
    click_element_by_ele(page, _selector_ele)
    position_list_ele = _header_wrap_ele.ele(locator=MAIN_PAGE_AWESOME_PERSON_JOB_LIST_LOCATION, timeout=2)
    if not position_list_ele:
        print('未获取到职位列表')
        return []
    _list_html = position_list_ele.html
    matches = re.findall(r'</u>(.*?)</span>', _list_html)
    for match in matches:
        cleaned_match = match.strip('"\'')
        result.append(cleaned_match)
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
        _name = _filter_item_ele.ele(locator='xpath:div/div[1]')
        if not _name or _name.text in ['牛人关键词', '专业']:
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
    _expand_filter = page.ele(locator=MAIN_PAGE_AWESOME_PERSON_FILTER_EXPAND, timeout=3)  # 获取 展开元素
    if _expand_filter:
        click_element_by_ele(page, _expand_filter)  # 如果需要展开则点击
    result += get_filter_option_list(page, MAIN_PAGE_AWESOME_PERSON_FILTER_VIP_ITEM_XPATH_FORMAT)
    result += get_filter_option_list(page, MAIN_PAGE_AWESOME_PERSON_FILTER_FIX_VIP_ITEM_XPATH_FORMAT)
    result += get_filter_option_list(page, MAIN_PAGE_AWESOME_PERSON_FILTER_NORMAL_ITEM_XPATH_FORMAT)
    # return ['刚刚活跃', '今日活跃', '本周活跃', '本月活跃', '男', '女', '近14天没有', '近一个月没有', '985', '211',
    #         '双一流院校', '留学', '国内外名校', '公办本科', '5年少于3份', '平均每份工作大于1年', '在校/应届',
    #         '25年毕业', '26年毕业', '26年']
    result.append('只看第一学历（第一学历为全日制本科）')
    print(result)
    return result


@popup_when_ele_existed(locator=CAPTCHA_PAGE_LOCATOR)
def do_chain(page):
    page.get(URL_AWESOME)  # 推荐牛人界面
    _position_list = get_position_list(page)
    _filter_list = get_filter_list(page)
    _person_input, _job_input, _filter_input, _desired_input, _age_input = [], [], [], [], []
    while True:
        result = safe_gui_call(popup_mixed_inputs, [
            {'type': 'input', 'title': '打招呼人数'},
            {'type': 'multiselect', 'title': '选择职位', 'choices': _position_list},
            {'type': 'multiselect', 'title': '选择筛选条件', 'choices': _filter_list},
            {'type': 'input', 'title': '期望职位'},
            {'type': 'input', 'title': '年龄范围(x-y格式)例如1-18'}
        ], '下一步', '停止选择')
        if not result:
            print("取消")
            break
        _person_input.append(int(result[0]))
        _job_input.append(result[1].split(';'))
        _filter_input.append(result[2].split(';'))
        _desired_input.append(result[3].split(';'))
        _age_input.append(result[4].split('-'))
    print(_person_input, _job_input, _filter_input, _desired_input, _age_input)
    # 进入主界面
    close_message_information(page)  # 关闭消息提醒
    say_hello(page, _person_input, _job_input, _filter_input, _desired_input, _age_input)  # 第一步 打招呼
    page.get(URL_COMMUNICATION)
    init_resume = 0
    _config = read_or_create_ini(file_path=CONFIG_INI_PATH, default_config=DEFAULT_CONFIG)
    _common_greeting = None
    if 'common_phrases' in _config and 'greetings' in _config['common_phrases']:
        _common_greeting = _config['common_phrases']['greetings']
    if _common_greeting is None or _common_greeting == '':
        _common_greeting = '方便发一份你的简历过来吗？'
        update_ini_value(CONFIG_INI_PATH, 'common_phrases', 'greetings', _common_greeting)
    while True:
        proactive_resume(page, _common_greeting)  # 第二步 收取主动打招呼的简历
        passive_resume(page, _common_greeting)  # 第三步 处理新招呼 求简历
        get_resume_in_had_resume(page, init_resume)
        init_resume |= 1


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
        if page.ele('推荐牛人'):
            break
        else:
            print('\r等待登录...')
            time.sleep(1)
    do_chain(page)


def prepare_run():
    _config = read_or_create_ini(file_path=CONFIG_INI_PATH, default_config=DEFAULT_CONFIG)
    _config_deadline = _config['deadline']['time']
    if _config_deadline is None or _config_deadline == '' or len(_config_deadline.split(':')) != 3:
        _config_deadline = '20:00:00'
        update_ini_value(CONFIG_INI_PATH, 'deadline', 'time', _config_deadline)
    _deadline_time = safe_gui_call(popup_input, f'自动终止时间(24小时制),不填默认{_config_deadline}')
    if _deadline_time != '':
        update_ini_value(CONFIG_INI_PATH, 'deadline', 'time', _deadline_time)
    else:
        _deadline_time = _config_deadline
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
