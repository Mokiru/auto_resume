import math
import os
import random
import time
import traceback
import tkinter as tk
from tkinter import simpledialog
from typing import Optional

from DrissionPage import *
from DrissionPage.errors import ElementNotFoundError


def generate_random_center(x, y, width, height, center_ratio=0.5):
    """
    生成随机偏移后的坐标，使其落在矩形的中心区域。
    参数:
    x (int): 矩形左上角的 x 坐标
    y (int): 矩形左上角的 y 坐标
    width (int): 矩形的宽度
    height (int): 矩形的高度
    center_ratio (float): 中心区域的宽高比例，默认为 0.5
    返回:
    tuple: 随机偏移后的坐标 (new_x, new_y)
    """
    # 计算中心区域的宽高
    center_width = width * center_ratio
    center_height = height * center_ratio

    # 计算中心区域的左上角坐标
    center_x = x + (width - center_width) / 2
    center_y = y + (height - center_height) / 2

    # 生成随机偏移量
    random_x = random.uniform(center_x, center_x + center_width) - x
    random_y = random.uniform(center_y, center_y + center_height) - y

    return random_x, random_y


def get_ele_end_point(ele, is_random=True):
    """
    获取元素左上角坐标和偏移量
    左上角x坐标,左上角y坐标,偏移量x,偏移量y
    :param ele:
    :param is_random:
    :param cursor_click: 是否光标移动
    :return:
    """
    _loc_x, _loc_y = ele.rect.location  # 获取元素位置
    _w, _h = ele.rect.size  # 元素宽-高
    _offset_x, _offset_y = 0, 0
    if is_random:
        _offset_x, _offset_y = generate_random_center(_loc_x, _loc_y, _w, _h, 0.4)  # 根据元素左上角做坐标和宽高生成随机偏移
    return _loc_x, _loc_y, _offset_x, _offset_y


def get_curr_mouse_loc(tab):
    """
    获取当前标签页中，鼠标位置
    """
    return tab.actions.curr_x, tab.actions.curr_y


def browser_mouse_move(tab, end_point):
    """
    浏览器移动鼠标到end_point
    """
    _start_x, _start_y = get_curr_mouse_loc(tab)
    _browser_mouse_move(tab, (_start_x, _start_y), end_point)


def get_point_list(start_point, end_point):
    """
    根据起点和终点生成曲线点列表
    默认点50个
    """
    _start_x, _start_y = start_point
    _end_x, _end_y = end_point
    # 直线距离
    distance = math.sqrt((_end_x - _start_x) ** 2 + (_end_y - _start_y) ** 2)
    # 根据距离动态计算点数（每10像素约1个点，最少10个点，最多100个点）
    num_points = max(10, min(100, int(distance / 10)))
    min_x, max_x = min(_start_x, _end_x), max(_start_x, _end_x)
    min_y, max_y = min(_start_y, _end_y), max(_start_y, _end_y)
    control_x1 = _start_x + (_end_x - _start_x) * 0.3 + random.randint(-int(min_x),
                                                                       int(max_x - min_x)) if min_x > 0 else random.randint(
        -10, 10)
    control_y1 = _start_y + (_end_y - _start_y) * 0.2 + random.randint(-int(min_y),
                                                                       int(max_y - min_y)) if min_y > 0 else random.randint(
        -10, 10)
    control_x2 = _start_x + (_end_x - _start_x) * 0.7 + random.randint(-int(min_x),
                                                                       int(max_x - min_x)) if min_x > 0 else random.randint(
        -10, 10)
    control_y2 = _start_y + (_end_y - _start_y) * 0.8 + random.randint(-int(min_y),
                                                                       int(max_y - min_y)) if min_y > 0 else random.randint(
        -10, 10)

    return _cubic_bezier_curve(start_point, (control_x1, control_y1), (control_x2, control_y2), end_point,
                               num_points=num_points)


def _cubic_bezier_curve(start_point, control_point1, control_point2, end_point, num_points=30):
    """
    生成三阶贝塞尔曲线路径点

    :param start_point: 起始点 (x, y)
    :param control_point1: 第一个控制点 (x, y)
    :param control_point2: 第二个控制点 (x, y)
    :param end_point: 结束点 (x, y)
    :param num_points: 生成点的数量
    :return: 路径点列表
    """
    points = []
    for i in range(num_points + 1):
        t = i / num_points
        # 三阶贝塞尔曲线公式: B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
        points.append(((1 - t) ** 3 * start_point[0] + 3 * (1 - t) ** 2 * t * control_point1[0] + 3 * (1 - t) * t ** 2 *
                       control_point2[0] + t ** 3 * end_point[0],
                       (1 - t) ** 3 * start_point[1] + 3 * (1 - t) ** 2 * t * control_point1[1] + 3 * (1 - t) * t ** 2 *
                       control_point2[1] + t ** 3 * end_point[1]))
    return points


def _browser_mouse_move(tab, start_point, end_point):
    path_points = get_point_list(start_point, end_point)  # 生成轨迹点
    for i, (_x, _y) in enumerate(path_points):
        if i != 0 and i != len(path_points) - 1:
            _x = max(0, _x + random.randint(-2, 2))
            _y = max(0, _y + random.randint(-2, 2))
        tab.actions.move_to(ele_or_loc=(_x, _y), duration=0.01)
        # time.sleep(random.uniform(0.01, 0.03))


def _click_element(tab, ele, button='left', count=1, is_random=True):
    """
    在标签页tab中点击元素ele
    """
    _loc_x, _loc_y, _offset_x, _offset_y = get_ele_end_point(ele, is_random)
    browser_mouse_move(tab, (_loc_x + _offset_x, _loc_y + _offset_y))
    time.sleep(0.2)
    ele.click.at(offset_x=_offset_x, offset_y=_offset_y, button=button, count=count)


def open_browser(path: Optional[str] = None) -> Chromium:
    if path:
        co = ChromiumOptions()
        co.set_browser_path(path)
        browser = Chromium(co)
    else:
        browser = Chromium()
    return browser


def click_element(page, xpath):
    ele = page.ele(xpath)
    _click_element(page, ele)
    time.sleep(random.uniform(0.3, 0.7))


def click_element_by_ele(page, ele):
    _click_element(page, ele)
    time.sleep(random.uniform(0.3, 0.7))


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
    click_element(page, r'xpath://*[@id="container"]/div[1]/div/div[2]/div[1]/div/div/div/div[7]/span')  # 点击我发起的
    click_element(page, r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/span[2]')  # 点击未读
    time.sleep(random.uniform(5.0, 6.5))
    unread_list_ele = page.ele(
        r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]')  # 获取列表元素
    children_list = unread_list_ele.children()  # 获取子元素列表
    for ele in children_list:
        # 遍历子元素列表
        if not check_unread(ele):
            continue
        # 未读标识
        ele.click()
        dialog_ele = page.ele(
            r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]')  # 获取消息框元素
        message_list = dialog_ele.children()  # 找到发送简历元素
        for message_ele in message_list:
            # 遍历消息
            confirm_ele = message_ele.ele(locator='同意')
            try:
                confirm_ele.click()
                print("已同意发送简历")
            except ElementNotFoundError:
                continue


def check_have_resume(page):
    """
    判断对方是否已经发送简历
    :param page:
    :return:
    """
    chat_message_ele = page.s_ele(
        r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]')  # 获取消息框元素
    resum_icon_ele = chat_message_ele.ele(locator='@class=message-dialog-icon resume-icon')
    if not resum_icon_ele:
        return False
    return True


def passive_resume(page):
    """
    新招呼
    :param page:
    :return:
    """
    while True:
        try:
            new_call_ele = page.ele(r'xpath://*[@id="container"]/div[1]/div/div[2]/div[1]/div/div/div/div[2]')
            if new_call_ele.attr('class') != 'chat-label-item selected':
                # click_element(page, r'xpath://*[@id="container"]/div[1]/div/div[2]/div[1]/div/div/div/div[2]/span')  # 点击新招呼
                new_call_ele.click()
            while True:
                click_element(page,
                              r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/span[2]')  # 点击未读
                time.sleep(random.uniform(1.0, 1.5))
                unread_list_ele = page.ele(
                    r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]')  # 获取列表元素
                # //*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]
                get_resume_key = {}
                list_first_ele = page.ele(
                    r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[1]')
                if not list_first_ele:
                    return
                index = 1
                while True:
                    list_item_ele = page.ele(
                        r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[' + str(
                            index) + ']')
                    if not list_item_ele:
                        break
                    index += 1
                    key = list_item_ele.attr('key')
                    if key in get_resume_key:
                        print("已获取过该简历")
                        continue
                    click_element_by_ele(page, list_item_ele)
                    get_resume_key[key] = 1
                    if check_have_resume(page):
                        print("当前已获取简历，跳过")
                        continue
                    try:
                        # chat_editor_ele = page.ele(r'xpath://*[@id="boss-chat-editor-input"]')  # 获取消息发送框元素
                        # click_element(page, chat_editor_ele)
                        page.actions.type('方便发一份你的简历过来吗？\n')
                        time.sleep(random.uniform(1.0, 1.5))
                        click_element(page,
                                      r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/span[1]')  # 求简历
                        time.sleep(random.uniform(0.5, 1.5))
                        click_element(page,
                                      r'xpath://*[@id="container"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/span[2]') # 确认
                        print("求简历")
                    except ElementNotFoundError:
                        print("失败，跳过")
                        continue
        except Exception:
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
    # proactive_resume(page)  # 第一步 收取主动打招呼的简历
    passive_resume(page)


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
