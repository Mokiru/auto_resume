import math
import random
import time
from typing import Optional

from DrissionPage import *


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
    co = ChromiumOptions()
    co.auto_port()
    co.set_argument('--start-maximized')
    if path:
        co.set_browser_path(path)
        browser = Chromium(co)
    else:
        browser = Chromium(co)
    return browser


def click_element(page, xpath):
    ele = page.ele(xpath)
    _click_element(page, ele)
    time.sleep(random.uniform(0.3, 0.7))


def click_element_by_ele(page, ele):
    _click_element(page, ele)
    time.sleep(random.uniform(0.3, 0.7))
