import os
import random
import sys
import threading
import time
import traceback

from DrissionPage._functions.keys import Keys

from base_operates import open_browser, click_element, click_element_by_ele
from simple_dialog import get_global_root, safe_gui_call, popup_input, popup_mixed_inputs
from timer_function_decorator import deadline_decorator

# 筛选项
JOB_SELECT_CHOICES = ['不选择', '全部职位', '目前职位', '过往职位']
COMPANY_SELECT_CHOICES = ['不选择', '全部公司', '目前公司', '过往公司']
EXPERIENCE_CHOICES = ['不选择', '不限', '在校/应届', '1-3年', '3-5年', '5-10年', '自定义']
EDUCATION_CHOICES = ['不选择', '不限', '本科', '硕士', '博士/博士后', '大专', '中专/中技', '高中及以下']
UNIFIED_RECRUITMENT_REQUIREMENT_CHOICES = ['不选择', '不限', '统招本科', '统招硕士', '统招博士', '统招大专']
UNIVERSITY_REQUIREMENT_CHOICES = ['不选择', '不限', '211', '985', '双一流', '海外留学']
ACTIVE_STATUS_CHOICES = ['不选择', '不限', '今天活跃', '3天内活跃', '7天内活跃', '30天内活跃', '最近三个月活跃',
                         '最近半年活跃']
JOB_HUNTING_CHOICES = ['不选择', '不限', '离职，正在找工作', '在职，急寻新工作', '在职，看看新机会', '在职，暂无跳槽打算']
FREQUENCY_OF_JOB_HOPPING_CHOICES = ['不选择', '不限', '近5年不超过3段', '近3年不超过2段', '近2段均不低于2年']
AGE_REQUIREMENT_CHOICES = ['不选择', '不限', '20-25岁', '25-30岁', '30-35岁', '35-40岁', '40岁以上', '自定义']
SEX_REQUIREMENT_CHOICES = ['不选择', '不限', '男', '女']
LANGUAGE_REQUIREMENT_CHOICES = ['不选择', '不限', '英语', '日语', '粤语', '其他']
GRADUATION_YEAR_CHOICES = ['不选择', '不限', '2025年毕业', '2026年毕业', '2027年毕业', '2028年毕业', '2029年毕业',
                           '2030年毕业']
CURRENT_ANNUAL_SALARY_CHOICES = ['不选择', '不限', '5万以下', '5-10万', '10-20万', '20-30万', '30-40万', '40-50万',
                                 '50-65万',
                                 '65-80万',
                                 '80-100万', '100万以上', '自定义']
EXPECTATION_ANNUAL_SALARY_CHOICES = ['不选择', '不限', '5万以下', '5-10万', '10-20万', '20-30万', '30-40万', '40-50万',
                                     '50-65万',
                                     '65-80万',
                                     '80-100万', '100万以上', '自定义']
RESUME_LANGUAGE_CHOICES = ['不选择', '不限', '中文简历', '英文简历']
NATURE_OF_THE_COMPANY_CHOICES = ['不选择', '不限', '外商独资/外企办事处', '中外合营(合资/合作)', '私营/民营企业',
                                 '国有企业',
                                 '国内上市公司', '政府机关／非盈利机构', '事业单位', '其他']
COMMUNICATION_STATUS_CHOICES = ['不选择', '不限', '隐藏我已沟通', '隐藏我和同事已沟通']
CONTACT_STATUS_CHOICES = ['不选择', '不限', '隐藏我已获取联系方式', '隐藏我和同事已获取联系方式']
CHECKBOX_CHOICES = ['不选择', '是', '否']

URL_LOGIN = 'https://lpt.liepin.com'
URL_SEARCH_PERSON = 'https://lpt.liepin.com/search'
URL_JOB_MANAGEMENT = 'https://lpt.liepin.com/job/manager'
SEARCH_PERSON_FILTER_WRAP_CLASS = r'@|class=wrap--bbDaK@|class=wrap--bbDaK submited'  # 筛选栏class
SEARCH_PERSON_FILTER_CLICK_ATTACH_FILTER_WRAP_XPATH = r'xpath:/div[3]'  # 在筛选栏中的筛选项wrap 相对xpath
SEARCH_PERSON_FILTER_SEARCH_BOX_ATTACH_XPATH = r'xpath:/div[2]/div/div/div/div/div[3]/div/input'  # 搜索栏
SEARCH_PERSON_FILTER_SEARCH_BOX_CONFIRM_ATTACH_XPATH = r'xpath:/div[2]/div/div/div/button'  # 开始搜索
# 以下相对xpath都是基于SEARCH_PERSON_FILTER_CLICK_ATTACH_FILTER_WRAP_XPATH
SEARCH_PERSON_FILTER_JOB_INPUT_ATTACH_XPATH = r'xpath:/div[2]/div/div[1]/div/div[2]/div/div[1]/div/span[1]/span/input'  # 筛选项中的职位输入框 相对xpath
SEARCH_PERSON_FILTER_JOB_SELECT_ATTACH_XPATH = r'xpath:/div[2]/div/div[1]/div/div[2]/div/div[2]/div'  # 职位栏中选择框
SEARCH_PERSON_FILTER_COMPANY_INPUT_ATTACH_XPATH = r'xpath:/div[2]/div/div[2]/div/div[2]/div/div[1]/div/span[1]/span/input'  # 筛选项中公司输入框 相对xpath
SEARCH_PERSON_FILTER_COMPANY_SELECT_ATTACH_XPATH = r'xpath:/div[2]/div/div[2]/div/div[2]/div/div[2]/div'  # 公司栏中选择框
SEARCH_PERSON_FILTER_FAST_SEARCH_ATTACH_XPATH_PATTERN = r'xpath:/div[3]/div[1]/div/div/div/div/div/span[{0}]/span[1]'  # 快捷搜索 相对xpath模板 format选中项下标+1
SEARCH_PERSON_FILTER_CURRENT_CITY_ATTACH_XPATH = r'xpath:/div[3]/div[2]/div/div[1]/label[last()]'  # 目前城市 其他 label 相对xpath
SEARCH_PERSON_FILTER_EXPECTATION_CITY_ATTACH_XPATH = r'xpath:/div[3]/div[3]/div/div[1]/label[last()]'  # 期望城市 其他label 相对xpath

SEARCH_PERSON_FILTER_DIALOG_LOCATION = r'@@role=dialog@@aria-modal=true@@class=ant-lpt-modal city-modal'  # 弹出对话框
SEARCH_PERSON_FILTER_SEARCH_CITY_INPUT_LOCATION = r'@@placeholder=搜索城市@@class=ant-lpt-input'  # 搜索城市输入框
SEARCH_PERSON_FILTER_SEARCH_CITY_FIRST_ITEM_ATTACH_XPATH = r'xpath:/div[2]/div/div/div/div/div/ul/li[1]'  # 列表第一个
SEARCH_PERSON_FILTER_DIALOG_CONFIRM_ATTACH_XPATH = r'xpath:/div[2]/div/section/div[2]/div/div/div[2]/button'  # 确认按钮

SEARCH_PERSON_FILTER_DIALOG_INDUSTRY_LOCATION = r'@@role=dialog@@aria-modal=true@@class=ant-lpt-modal'  # 行业选择dialog
SEARCH_PERSON_FILTER_SEARCH_INDUSTRY_INPUT_ATTACH_XPATH = r'xpath:/div[2]/div/div/div[1]/div[2]/span/input'  # 行业输入框
SEARCH_PERSON_FILTER_SEARCH_INDUSTRY_FIRST_ITEM_ATTACH_XPATH = r'xpath:/div[2]/div/div/div[1]/div[2]/div/div/ul/li[1]'  # 列表第一个
SEARCH_PERSON_FILTER_DIALOG_INDUSTRY_CONFIRM_ATTACH_XPATH = r'xpath:/div[2]/div/div/div[2]/div[2]/div[2]/div[2]/button'  # 确认按钮

SEARCH_PERSON_FILTER_DIALOG_FUNCTION_LOCATION = r'@@role=dialog@@aria-modal=true@@class=ant-lpt-modal antd-jobs-modal antd-jobs-modal-tlog'  # 职能dialog
SEARCH_PERSON_FILTER_FUNCTION_INPUT_ATTACH_XPATH = r'xpath:/div[2]/div/section/div[1]/div/div[1]/span/input'  # 职能输入框
SEARCH_PERSON_FILTER_FUNCTION_FIRST_ITEM_ATTACH_XPATH = r'xpath:/div[2]/div/section/div[1]/div/div[2]/div/ul/li[1]'  # 列表第一个
SEARCH_PERSON_FILTER_DIALOG_FUNCTION_CONFIRM_ATTACH_XPATH = r'xpath:/div[2]/div/section/div[4]/div[2]/div[2]/div[2]/button'  # 职能dialog确认按钮

SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_XPATH_PATTERN = r'xpath:/div[3]/div[4]/div/div/label[{0}]'  # 经验筛选项 相对xpath模板 format选中项下标
SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_CUSTOM_LEFT_INPUT_XPATH = r'xpath:/div[3]/div[4]/div/div/div/div[2]/div/span[1]/span/input'  # 自定义经验左侧输入框
SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_CUSTOM_RIGHT_INPUT_XPATH = r'xpath:/div[3]/div[4]/div/div/div/div[2]/div/span[2]/span/input'  # 自定义经验右侧输入框
SEARCH_PERSON_FILTER_EDUCATION_ATTACH_XPATH_PATTERN = r'xpath:/div[3]/div[5]/div/div/label[{0}]'  # 教育经历筛选项 相对xpath模板 format选中项下标+1
SEARCH_PERSON_FILTER_UNIFIED_ATTACH_XPATH = r'xpath:/div[3]/div[5]/div/div/div[2]'  # 统招要求选择框 相对xpath
SEARCH_PERSON_FILTER_UNIVERSITY_ATTACH_XPATH = r'xpath:/div[3]/div[5]/div/div/div[4]'  # 院校要求 相对xpath
SEARCH_PERSON_FILTER_MORE_FILTER_CLASS = r'@class=antlpticon antlpticon-select-down switchIcon--r9Pa9'  # 更多条件筛选项 找不到说明已经打开
SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN = r'xpath:/div[3]/div[6]/div/div/div/div[{0}]'  # 其他筛选选择框模板 相对xpath
# 以下其他筛选项特殊，包含了自定义选项
SEARCH_PERSON_FILTER_AGR_REQUIREMENT_SELECT_ATTACH_XPATH = SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(
    4)  # 年龄要求
SEARCH_PERSON_FILTER_AGE_REQUIREMENT_LEFT_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[4]/div[2]/div/div[2]/div/span[1]/span/input'  # 自定义年龄左侧输入框
SEARCH_PERSON_FILTER_AGE_REQUIREMENT_RIGHT_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[4]/div[2]/div/div[2]/div/span[2]/span/input'  # 自定义年龄右侧输入框

SEARCH_PERSON_FILTER_LANGUAGE_REQUIREMENT_SELECT_ATTACH_XPATH = SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(
    6)  # 语言要求
SEARCH_PERSON_FILTER_LANGUAGE_REQUIREMENT_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[6]/div[2]/div/div[2]/input'  # 语言要求输入框

SEARCH_PERSON_FILTER_CURRENT_INDUSTRY_SELECT_ATTACH_XPATH = SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(
    8)  # 当前行业
SEARCH_PERSON_FILTER_EXPECTATION_INDUSTRY_SELECT_ATTACH_XPATH = SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(
    9)  # 期望行业
SEARCH_PERSON_FILTER_CURRENT_FUNCTION_SELECT_ATTACH_XPATH = SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(
    10)  # 当前职能
SEARCH_PERSON_FILTER_EXPECTATION_FUNCTION_SELECT_ATTACH_XPATH = SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(
    11)  # 期望职能

SEARCH_PERSON_FILTER_SELECT_LIST_ANCHOR_LOCATION = r'@|class=ant-lpt-select-dropdown user-status-down ant-lpt-select-dropdown-placement-bottomLeft @|class=ant-lpt-select-dropdown ant-lpt-select-dropdown-placement-bottomLeft @|class=ant-lpt-select-dropdown list-container-down ant-lpt-select-dropdown-placement-bottomLeft '  # 下拉框激活时的class
SEARCH_PERSON_FILTER_LIST_HOLDER_ATTACH_XPATH = r'xpath:/div/div[2]/div[2]/div'  # scroll bar 相对下拉框xpath

SEARCH_PERSON_FILTER_CURRENT_ANNUAL_SALARY_SELECT_ATTACH_XPATH = SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(
    12)  # 目前年薪
SEARCH_PERSON_FILTER_CURRENT_ANNUAL_SALARY_LEFT_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[12]/div[2]/div/div[2]/div/span[1]/span/input'  # 自定义年薪左侧输入框
SEARCH_PERSON_FILTER_CURRENT_ANNUAL_SALARY_RIGHT_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[12]/div[2]/div/div[2]/div/span[2]/span/input'  # 自定义年薪右侧输入框

SEARCH_PERSON_FILTER_EXPECTATION_ANNUAL_SALARY_SELECT_ATTACH_XPATH = SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(
    13)  # 期望年薪
SEARCH_PERSON_FILTER_EXPECTATION_ANNUAL_SALARY_LEFT_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[13]/div[2]/div/div[2]/div/span[1]/span/input'  # 期望年薪左侧输入框
SEARCH_PERSON_FILTER_EXPECTATION_ANNUAL_SALARY_RIGHT_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[13]/div[2]/div/div[2]/div/span[2]/span/input'  # 期望年薪右侧输入框

SEARCH_PERSON_FILTER_MANAGEMENT_EXPERIENCE_CHECKBOX_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/label[1]/span'  # 管理经验单选框 相对xpath
SEARCH_PERSON_FILTER_WORK_OVERSEAS_CHECKBOX_ATTACH_XPATH = 'xpath:/div[3]/div[6]/div/div/div/label[2]/span'  # 海外工作单选框 相对xpath
SEARCH_PERSON_FILTER_CHECKBOX_FALSE_CLASS = r'ant-lpt-checkbox'  # checkbox未选中的class
SEARCH_PERSON_FILTER_PROFESSIONAL_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[16]/div[2]/input'  # 专业名称 相对xpath
SEARCH_PERSON_FILTER_GRADUATION_UNIVERSITY_INPUT_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/div[17]/div[2]/input'  # 毕业院校名称 相对xpath
SEARCH_PERSON_FILTER_RESET_SEARCH_ATTACH_XPATH = r'xpath:/span'  # 重置条件按钮 相对xpath

SEARCH_PERSON_COMMUNICATION_LIST_ITEM_XPATH_PATTERN = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div[5]/ul/li[{0}]'  # 列表元素xpath模板
SEARCH_PERSON_COMMUNICATION_LIST_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div[5]/ul/*'  # 列表xpath
SEARCH_PERSON_COMMUNICATION_DIALOG_LOCATION = r'@@role=dialog@@aria-modal=true@@class=ant-lpt-modal'  # 沟通dialog
SEARCH_PERSON_COMMUNICATION_DIALOG_SEARCH_INPUT_ATTACH_XPATH = r'xpath:/div[2]/div[2]/div/span/input'  # 沟通dialog中 搜索框 相对xpath
SEARCH_PERSON_COMMUNICATION_DIALOG_LIST_XPATH = r'xpath:/div[2]/div[2]/div/div/div/div/ul/div/*'  # 职位列表 相对xpath模板
SEARCH_PERSON_COMMUNICATION_DIALOG_LIST_ITEM_XPATH_PATTERN = r'xpath:/div[2]/div[2]/div/div/div/div/ul/div/li[{0}]'  # 职位列表 相对xpath模板
SEARCH_PERSON_COMMUNICATION_DIALOG_ITEM_JOB_NAME_ATTACH_XPATH = r'xpath:/p[1]/strong'  # 职位名称 相对列表元素xpath
SEARCH_PERSON_COMMUNICATION_DIALOG_ITEM_JOB_LOC_ATTACH_XPATH = r'xpath:/p[2]/span[1]'  # 职位地点 相对列表元素xpath
SEARCH_PERSON_COMMUNICATION_DIALOG_CONFIRM_ATTACH_XPATH = r'xpath:/div[2]/div[3]/button[2]'  # 确定按钮 相对xpath
SEARCH_PERSON_COMMUNICATION_DIALOG_CANCEL_ATTACH_XPATH = r'xpath:/div[2]/div[3]/button[1]'  # 取消按钮 相对xpath

SEARCH_PERSON_COMMUNICATION_CONTINUE_COMMUNICATION_MASK_LOCATION = r'@class=ant-im-drawer ant-im-drawer-right no-mask ant-im-teno-drawer ant-im-drawer-open'
SEARCH_PERSON_COMMUNICATION_CONTINUE_COMMUNICATION_CLOSE_ATTACH_XPATH = r'xpath:/div[2]/div/div/div[1]/div/button'  # 相对xpath 关闭按钮

SEARCH_PERSON_SEARCHED_COMMUNICATION_STATUS_SELECT_ATTACH_XPATH = r'xpath:/div[4]/section/div[4]/div[1]'  # 沟通状态 相对all-wrap xpath
SEARCH_PERSON_SEARCHED_CONTACT_STATUS_SELECT_ATTACH_XPATH = r'xpath:/div[4]/section/div[4]/div[2]'  # 获取联系方式状态 相对xpath
SEARCH_PERSON_SEARCHED_HIDE_CHECKBOX_ATTACH_XPATH = r'xpath:/div[4]/section/div[4]/label'  # 是否隐藏已经查看 相对xpath
SEARCH_PERSON_SEARCHED_HIDE_CHECKBOX_CHECKED_CLASS = r'ant-lpt-checkbox-wrapper ant-lpt-checkbox-wrapper-checked'  # 选中状态class
SEARCH_PERSON_SEARCHED_MATCH_RECENT_CHECKBOX_ATTACH_XPATH = r'xpath:/div[4]/section/label'  # 是否只匹配最近一段工作
SEARCH_PERSON_SEARCHED_MATCH_RECENT_CHECKBOX_CHECKED_CLASS = r'ant-lpt-checkbox-wrapper ant-lpt-checkbox-wrapper-checked'  # 选中状态class

SEARCH_PERSON_COMMUNICATION_LIST_NEXT_PAGE_LOCATION = r'@@title=下一页@@aria-disabled=false'
# 全局查询
SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION = r'@title={0}'

SEARCH_PERSON_FAST_SEARCH_CLASS = r'@class=ant-lpt-tag ant-lpt-teno-tag ant-lpt-teno-tag-small'
COMMUNICATION_URL = URL_LOGIN + "/chat/im"
COMMUNICATION_NEW_HELLO_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[1]/div[2]/div/div/div/label[2]'
COMMUNICATION_NO_READ_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[2]/aside/div[1]/div[3]/div/label/span[1]'
COMMUNICATION_PERSON_LIST_XPATH_PREFIX = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[2]/aside/div[2]/div[1]/div/div[{0}]'
COMMUNICATION_GET_RESUME_BUTTON_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[2]/div/div[2]/div[3]/div[1]/div[1]/div/div[1]/div/div[3]/span/span'
COMMUNICATION_CONFIRM_RESUME_BUTTON_FILTER = '@@class=ant-im-btn ant-im-btn-primary@@type=button'
COMMUNICATION_MESSAGE_BOX_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[2]/div/div[2]/div[2]/div[1]'

COMMUNICATION_INITIATED_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div/div[1]/div[2]/div/div/div/label[3]'

JOB_MANAGEMENT_LIST_ITEM_XPATH_PATTERN = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div[2]/div/div[2]/div[{0}]'  # 职位管理xpath模板
JOB_MANAGEMENT_LIST_XPATH = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div[2]/div/div[2]/*'  # 职位管理列表下所有元素xpath
JOB_MANAGEMENT_LIST_ITEM_JOB_NAME_ATTACH_XPATH = r'xpath:/div[1]/div[1]/a'  # 职位名称元素
JOB_MANAGEMENT_LIST_ITEM_JOB_NAME_DESC_ATTACH_XPATH = r'xpath:/div[1]/div[2]/span'  # 职位描述 地址
JOB_MANAGEMENT_TOP_CLASS = r'@class=jobCardWrap--YDbfn jobCardWrapTopFlag--D85cx'  # 元素指定class
JOB_MANAGEMENT_AUTO_SCROLL_XPATH_PATTERN = r'xpath://*[@id="main-container"]/section/section/main/div/div[1]/div[2]/div/div[2]/div[{0}]/div[2]'  # 点击，主要为了自动滑动页面
JOB_MANAGEMENT_NEXT_PAGE_LOCATION = r'@@title=下一页@@aria-disabled=false'

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


def _popup_click_ele(page, locator: str):
    """
    点击弹窗中的元素
    :param page:
    :param locator: 目标选择器 会在下拉框元素中搜索
    :return:
    """
    _popup_ele = page.ele(locator=SEARCH_PERSON_FILTER_SELECT_LIST_ANCHOR_LOCATION)  # 获取弹窗
    if _popup_ele:
        _scroll_ele = _popup_ele.ele(locator=SEARCH_PERSON_FILTER_LIST_HOLDER_ATTACH_XPATH, timeout=3)  # 滑动条
        if _scroll_ele:
            for i in range(4):
                _target_ele = _popup_ele.ele(locator=locator, timeout=2)
                if _target_ele:
                    click_element_by_ele(page, _target_ele)
                    break
                else:
                    print('滑动条点击下，未找到目标元素')
                page.actions.hold(_scroll_ele).move(0, 30).release()
        else:
            _target_ele = _popup_ele.ele(locator=locator, timeout=2)
            if _target_ele:
                click_element_by_ele(page, _target_ele)
            else:
                print('无滑动条下，未找到目标元素')


def say_hello(page, job_list):
    """
    搜索牛人中 根据筛选项筛选并沟通
    :param page:
    :param job_list: 职位+地址列表
    :return:
    """
    page.get(URL_SEARCH_PERSON)  # 进入搜索人才界面
    _fast_search_span_list = page.s_eles(locator=SEARCH_PERSON_FAST_SEARCH_CLASS)  # 获取快速搜索span
    _fast_search_txt_list = ['不选择']
    for _fast_search_span in _fast_search_span_list:
        _name_ele = _fast_search_span.ele(locator='xpath:span[1]/span')
        if _name_ele:
            _fast_search_txt_list.append(_name_ele.text)
    _person_say_num = []
    _search_txt = []
    _person_job = []
    _person_job_select = []
    _person_company = []
    _person_company_select = []
    _fast_search = []
    _current_city = []
    _expectation_city = []
    _experience = []
    _custom_experience = []
    _education_experience = []
    _unified_recruitment_requirement = []
    _university_requirement = []
    _active_status = []
    _job_hunting_status = []
    _frequency_of_job_hopping = []
    _age_requirement = []
    _custom_age_requirement = []
    _sex_requirement = []
    _language_requirement = []
    _custom_language_requirement = []
    _graduation_year = []
    _current_industry = []
    _expectation_industry = []
    _current_function = []
    _expectation_function = []
    _current_annual_salary = []
    _custom_current_annual_salary = []
    _expectation_annual_salary = []
    _custom_expectation_annual_salary = []
    _resume_language = []
    _nature_of_the_company = []
    _management_experience = []
    _work_overseas = []
    _professional = []
    _graduation_university = []
    _communication_job = []
    _communication_status = []
    _contact_status = []
    _hide_looked = []
    _match_latest = []
    _all_lists = [
        _person_say_num, _search_txt, _person_job, _person_job_select, _person_company, _person_company_select,
        _fast_search, _current_city, _expectation_city, _experience, _custom_experience,
        _education_experience, _unified_recruitment_requirement, _university_requirement,
        _active_status, _job_hunting_status, _frequency_of_job_hopping, _age_requirement,
        _custom_age_requirement, _sex_requirement, _language_requirement, _custom_language_requirement,
        _graduation_year, _current_industry, _expectation_industry, _current_function,
        _expectation_function, _current_annual_salary, _custom_current_annual_salary,
        _expectation_annual_salary, _custom_expectation_annual_salary, _resume_language,
        _nature_of_the_company, _management_experience, _work_overseas, _professional,
        _graduation_university, _communication_job, _communication_status, _contact_status, _hide_looked,
        _match_latest,
    ]
    _common_select_filter_idx = [[1, 14], [2, 15], [3, 16], [5, 19], [7, 22], [14, 31], [15, 32]]
    _iter_idx = 0
    while True:
        result = safe_gui_call(popup_mixed_inputs, [
            {'type': 'input', 'title': '人数'},
            {'type': 'input', 'title': '搜索框'},
            {'type': 'input', 'title': '职位'},
            {'type': 'select', 'title': '全部/目前/过往职位', 'choices': JOB_SELECT_CHOICES},
            {'type': 'input', 'title': '公司'},
            {'type': 'select', 'title': '全部/目前/过往公司', 'choices': COMPANY_SELECT_CHOICES},
            {'type': 'select', 'title': '快捷搜索', 'choices': _fast_search_txt_list},
            {'type': 'input', 'title': '目前城市(多个用;分隔)'},
            {'type': 'input', 'title': '期望城市(多个用;分隔)'},
            {'type': 'select', 'title': '经验', 'choices': EXPERIENCE_CHOICES},
            {'type': 'input', 'title': '自定义经验(-分隔)'},
            {'type': 'multiselect', 'title': '教育经历', 'choices': EDUCATION_CHOICES},
            {'type': 'select', 'title': '统招要求', 'choices': UNIFIED_RECRUITMENT_REQUIREMENT_CHOICES},
            {'type': 'multiselect', 'title': '院校要求', 'choices': UNIVERSITY_REQUIREMENT_CHOICES},
            {'type': 'select', 'title': '活跃状态', 'choices': ACTIVE_STATUS_CHOICES},
            {'type': 'select', 'title': '求职状态', 'choices': JOB_HUNTING_CHOICES},
            {'type': 'select', 'title': '跳槽频率', 'choices': FREQUENCY_OF_JOB_HOPPING_CHOICES},
            {'type': 'select', 'title': '年龄要求', 'choices': AGE_REQUIREMENT_CHOICES},
            {'type': 'input', 'title': '自定义年龄要求(-分隔)'},
            {'type': 'select', 'title': '性别要求', 'choices': SEX_REQUIREMENT_CHOICES},
            {'type': 'select', 'title': '语言要求', 'choices': LANGUAGE_REQUIREMENT_CHOICES},
            {'type': 'input', 'title': '自定义语言要求'},
            {'type': 'select', 'title': '毕业年份', 'choices': GRADUATION_YEAR_CHOICES},
            {'type': 'input', 'title': '当前行业(多个用;分隔)'},
            {'type': 'input', 'title': '期望行业(多个用;分隔)'},
            {'type': 'input', 'title': '当前职能(多个用;分隔)'},
            {'type': 'input', 'title': '期望职能(多个用;分隔)'},
            {'type': 'select', 'title': '目前年薪', 'choices': CURRENT_ANNUAL_SALARY_CHOICES},
            {'type': 'input', 'title': '自定义目前年薪'},
            {'type': 'select', 'title': '期望年薪', 'choices': EXPECTATION_ANNUAL_SALARY_CHOICES},
            {'type': 'input', 'title': '自定义期望年薪'},
            {'type': 'select', 'title': '简历语言', 'choices': RESUME_LANGUAGE_CHOICES},
            {'type': 'select', 'title': '公司性质', 'choices': NATURE_OF_THE_COMPANY_CHOICES},
            {'type': 'select', 'title': '管理经验', 'choices': CHECKBOX_CHOICES},
            {'type': 'select', 'title': '海外工作', 'choices': CHECKBOX_CHOICES},
            {'type': 'input', 'title': '专业名称'},
            {'type': 'input', 'title': '毕业院校'},
            {'type': 'searchable_select', 'title': '沟通职位', 'choices': job_list},
            {'type': 'select', 'title': '沟通状态', 'choices': COMMUNICATION_STATUS_CHOICES},
            {'type': 'select', 'title': '获取联系方式状态', 'choices': CONTACT_STATUS_CHOICES},
            {'type': 'select', 'title': '隐藏已查看', 'choices': CHECKBOX_CHOICES},
            {'type': 'select', 'title': '只匹配最近一段工作', 'choices': CHECKBOX_CHOICES}
        ], '确认', '停止选择')
        if not result:
            break
        _iter_idx += 1
        for lst, val in zip(_all_lists, result):
            lst.append(val)
    for _idx in range(_iter_idx):
        _all_wrap_ele = page.ele(SEARCH_PERSON_FILTER_WRAP_CLASS)
        _filter_wrap_ele = _all_wrap_ele.ele(
            SEARCH_PERSON_FILTER_CLICK_ATTACH_FILTER_WRAP_XPATH)
        _search_txt_ele = _all_wrap_ele.ele(
            SEARCH_PERSON_FILTER_SEARCH_BOX_ATTACH_XPATH)
        _current_job_parts = _communication_job[_idx].split(',', 1)  # 分割为两部分
        if len(_current_job_parts) != 2:
            print('未选择沟通职位')
            _fix_current_job = safe_gui_call(popup_mixed_inputs, [
                {'type': 'searchable_select', 'title': '沟通职位', 'choices': job_list}
            ])
            _current_job_parts = _fix_current_job[0].split(',', 1)
            if len(_current_job_parts) != 2:
                print('未选择沟通职位')
                continue
        _current_job_name, _current_job_loc = _current_job_parts
        _reset_search_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_RESET_SEARCH_ATTACH_XPATH, timeout=3)
        _is_fast_search = False
        if not _reset_search_ele:
            print('未找到重置条件元素')
            continue
        click_element_by_ele(page, _reset_search_ele)  # 点击重置条件
        # 快捷搜索
        if _fast_search[_idx] != '不选择':
            _fast_idx = _fast_search_txt_list.index(_fast_search[_idx])
            _fast_search_ele = _filter_wrap_ele.ele(
                SEARCH_PERSON_FILTER_FAST_SEARCH_ATTACH_XPATH_PATTERN.format(_fast_idx), timeout=3)
            if not _fast_search_ele:
                print(f'未找到对应快捷搜索项{_fast_search[_idx]}')
                continue
            _is_fast_search = True
            click_element_by_ele(page, _fast_search_ele)
        # 职位
        if _person_job[_idx] != '':
            _job_input_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_JOB_INPUT_ATTACH_XPATH, timeout=3)
            click_element_by_ele(page, _job_input_ele)  # 点击输入框
            page.actions.type(_person_job[_idx])
            if _person_job_select[_idx] != '不选择':
                _job_select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_JOB_SELECT_ATTACH_XPATH, timeout=1)
                click_element_by_ele(page, _job_select_ele)  # 点击选择框
                _target_select_ele = page.ele(
                    SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(_person_job_select[_idx]), timeout=2)
                if _target_select_ele:
                    click_element_by_ele(page, _target_select_ele)  # 只有存在才点击，因为可能是当前选中项，则不需要点击
        # 公司
        if _person_company[_idx] != '':
            _company_input_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_COMPANY_INPUT_ATTACH_XPATH, timeout=3)
            click_element_by_ele(page, _company_input_ele)  # 点击输入框
            page.actions.type(_person_company[_idx])
            if _person_company_select[_idx] != '不选择':
                _company_select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_COMPANY_SELECT_ATTACH_XPATH, timeout=1)
                click_element_by_ele(page, _company_select_ele)  # 点击选择框
                _target_select_ele = page.ele(
                    SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(_person_company_select[_idx]), timeout=2)
                if _target_select_ele:
                    click_element_by_ele(page, _target_select_ele)  # 只有存在才点击，因为可能是当前选中项，则不需要点击
        # 目前城市
        if _current_city[_idx] != '':
            _more_option_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_CURRENT_CITY_ATTACH_XPATH, timeout=3)
            if _more_option_ele:
                click_element_by_ele(page, _more_option_ele)  # 点击其他
                _city_list = _current_city[_idx].split(';')
                _search_city_dialog_ele = page.ele(SEARCH_PERSON_FILTER_DIALOG_LOCATION, timeout=3)
                if _search_city_dialog_ele:
                    for _city in _city_list:
                        _input_ele = _search_city_dialog_ele.ele(
                            SEARCH_PERSON_FILTER_SEARCH_CITY_INPUT_LOCATION)  # 搜索城市输入框
                        click_element_by_ele(page, _input_ele)
                        page.actions.key_down(Keys.CTRL).type('a').key_up(Keys.CTRL).type(_city)
                        time.sleep(1)
                        _item_ele = _search_city_dialog_ele.ele(
                            SEARCH_PERSON_FILTER_SEARCH_CITY_FIRST_ITEM_ATTACH_XPATH)
                        click_element_by_ele(page, _item_ele)
                    _confirm_btn_ele = _search_city_dialog_ele.ele(SEARCH_PERSON_FILTER_DIALOG_CONFIRM_ATTACH_XPATH)
                    if _confirm_btn_ele:
                        click_element_by_ele(page, _confirm_btn_ele)
        # 期望城市
        if _expectation_city[_idx] != '':
            _more_option_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_EXPECTATION_CITY_ATTACH_XPATH, timeout=3)
            if _more_option_ele:
                click_element_by_ele(page, _more_option_ele)  # 点击其他
                _city_list = _expectation_city[_idx].split(';')
                _search_city_dialog_ele = page.ele(SEARCH_PERSON_FILTER_DIALOG_LOCATION, timeout=3)
                if _search_city_dialog_ele:
                    for _city in _city_list:
                        _input_ele = _search_city_dialog_ele.ele(
                            SEARCH_PERSON_FILTER_SEARCH_CITY_INPUT_LOCATION)  # 搜索城市输入框
                        click_element_by_ele(page, _input_ele)
                        page.actions.key_down(Keys.CTRL).type('a').key_up(Keys.CTRL).type(_city)
                        time.sleep(1)
                        _item_ele = _search_city_dialog_ele.ele(
                            SEARCH_PERSON_FILTER_SEARCH_CITY_FIRST_ITEM_ATTACH_XPATH)
                        click_element_by_ele(page, _item_ele)
                    _confirm_btn_ele = _search_city_dialog_ele.ele(SEARCH_PERSON_FILTER_DIALOG_CONFIRM_ATTACH_XPATH)
                    if _confirm_btn_ele:
                        click_element_by_ele(page, _confirm_btn_ele)
        if _experience[_idx] != '不选择':
            _experience_ele = _filter_wrap_ele.ele(
                SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_XPATH_PATTERN.format(
                    EXPERIENCE_CHOICES.index(_experience[_idx])),
                timeout=3)  # 经验筛选项
            # 经验
            if _experience_ele:
                if _experience_ele.attr('class') != 'searchPageFilterItem--S_vZI searchPageFilterItemActive--cW0cC':
                    click_element_by_ele(page, _experience_ele)
                if _experience[_idx] == '自定义':
                    # 需要输入经验
                    _begin, _end = _custom_experience[_idx].split('-')
                    _begin_input_ele = _filter_wrap_ele.ele(
                        SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_CUSTOM_LEFT_INPUT_XPATH,
                        timeout=1)
                    click_element_by_ele(page, _begin_input_ele)
                    page.actions.type(_begin)
                    _end_input_ele = _filter_wrap_ele.ele(
                        SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_CUSTOM_RIGHT_INPUT_XPATH,
                        timeout=1)
                    click_element_by_ele(page, _end_input_ele)
                    page.actions.type(_end)
        # 教育经历
        if _education_experience[_idx] != '' and _education_experience[_idx] != '不选择':
            _education_experience_list = _education_experience[_idx].split(';')
            for _education_experience_item in _education_experience_list:
                _education_experience_ele = _filter_wrap_ele.ele(
                    SEARCH_PERSON_FILTER_EDUCATION_ATTACH_XPATH_PATTERN.format(
                        EDUCATION_CHOICES.index(_education_experience_item)), timeout=2)  # 教育经历筛选项
                if _education_experience_ele:
                    click_element_by_ele(page, _education_experience_ele)
        # 统招要求
        if _unified_recruitment_requirement[_idx] != '不选择':
            _unified_requirement_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_UNIFIED_ATTACH_XPATH,
                                                            timeout=2)  # 统招要求选择框
            if _unified_requirement_ele:
                click_element_by_ele(page, _unified_requirement_ele)  # 点击选择框
                _popup_click_ele(page, SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                    '[object Object]' if _unified_recruitment_requirement[_idx] == '不限' else
                    _unified_recruitment_requirement[_idx]))
        # 院校要求
        if _university_requirement[_idx] != '' and _university_requirement[_idx] != '不选择':
            _university_requirement_list = _university_requirement[_idx].split(';')
            _university_requirement_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_UNIVERSITY_ATTACH_XPATH,
                                                               timeout=2)  # 院校要求选择框
            if _university_requirement_ele:
                click_element_by_ele(page, _university_requirement_ele)  # 点击选择框
                for _item in _university_requirement_list:
                    _popup_click_ele(page, SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                        '[object Object]' if _item == '不限' else _item))
        # 更多条件
        _more_filter_ele = page.ele(SEARCH_PERSON_FILTER_MORE_FILTER_CLASS, timeout=2)
        if _more_filter_ele:
            click_element_by_ele(page, _more_filter_ele)
        # 以下开始更多筛选选择
        for _pair in _common_select_filter_idx:
            _lst_idx = _pair[0]
            _lst = _all_lists[_pair[1]]
            if _lst[_idx] == '不选择': continue
            _select_ele = _filter_wrap_ele.ele(
                SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(_lst_idx), timeout=2)
            if _select_ele:
                click_element_by_ele(page, _select_ele)
                _popup_click_ele(page, SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                    '[object Object]' if _lst[_idx] == '不限' else _lst[_idx]))
        # 有自定义的选项
        # 年龄
        if _age_requirement[_idx] != '' and _age_requirement[_idx] != '不选择':
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_AGR_REQUIREMENT_SELECT_ATTACH_XPATH, timeout=2)
            if _select_ele:
                click_element_by_ele(page, _select_ele)
                _popup_click_ele(page, SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                    '[object Object]' if _age_requirement[_idx] == '不限' else _age_requirement[_idx]))
                if _age_requirement[_idx] == '自定义':
                    # 需要自定义年龄区间
                    _begin, _end = _custom_age_requirement[_idx].split('-')
                    time.sleep(1)
                    _left_input_ele = _filter_wrap_ele.ele(
                        SEARCH_PERSON_FILTER_AGE_REQUIREMENT_LEFT_INPUT_ATTACH_XPATH, timeout=1)
                    click_element_by_ele(page, _left_input_ele)
                    page.actions.type(_begin)
                    _right_input_ele = _filter_wrap_ele.ele(
                        SEARCH_PERSON_FILTER_AGE_REQUIREMENT_RIGHT_INPUT_ATTACH_XPATH, timeout=1)
                    click_element_by_ele(page, _right_input_ele)
                    page.actions.type(_end)
        # 语言
        if _language_requirement[_idx] != '' and _language_requirement[_idx] != '不选择':
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_LANGUAGE_REQUIREMENT_SELECT_ATTACH_XPATH, timeout=2)
            if _select_ele:
                click_element_by_ele(page, _select_ele)
                _popup_click_ele(page, SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                    '[object Object]' if _language_requirement[_idx] == '不限' else _language_requirement[_idx]))
                if _language_requirement[_idx] == '其他':
                    # 需要自定义语言
                    time.sleep(1)
                    _input_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_LANGUAGE_REQUIREMENT_INPUT_ATTACH_XPATH,
                                                      timeout=1)  # 语言输入框
                    click_element_by_ele(page, _input_ele)
                    page.actions.type(_custom_language_requirement[_idx])
        # 当前行业
        if _current_industry[_idx] != '':
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_CURRENT_INDUSTRY_SELECT_ATTACH_XPATH, timeout=2)
            if _select_ele:
                click_element_by_ele(page, _select_ele)
                # 打开dialog
                _search_industry_dialog_ele = page.ele(SEARCH_PERSON_FILTER_DIALOG_INDUSTRY_LOCATION)
                if _search_industry_dialog_ele:
                    _search_bar_ele = _search_industry_dialog_ele.ele(
                        SEARCH_PERSON_FILTER_SEARCH_INDUSTRY_INPUT_ATTACH_XPATH)
                    click_element_by_ele(page, _search_bar_ele)
                    _industry_list = _current_industry[_idx].split(';')
                    for _industry in _industry_list:
                        page.actions.key_down(Keys.CTRL).type('a').key_up(Keys.CTRL).type(_industry)
                        time.sleep(1)
                        _target_select_ele = _search_industry_dialog_ele.ele(
                            SEARCH_PERSON_FILTER_SEARCH_INDUSTRY_FIRST_ITEM_ATTACH_XPATH)
                        if _target_select_ele:
                            click_element_by_ele(page, _target_select_ele)
                    _confirm_btn_ele = _search_industry_dialog_ele.ele(
                        SEARCH_PERSON_FILTER_DIALOG_INDUSTRY_CONFIRM_ATTACH_XPATH)
                    click_element_by_ele(page, _confirm_btn_ele)
        # 期望行业
        if _expectation_industry[_idx] != '':
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_EXPECTATION_INDUSTRY_SELECT_ATTACH_XPATH, timeout=2)
            if _select_ele:
                click_element_by_ele(page, _select_ele)
                # 打开dialog
                _search_industry_dialog_ele = page.ele(SEARCH_PERSON_FILTER_DIALOG_INDUSTRY_LOCATION)
                if _search_industry_dialog_ele:
                    _search_bar_ele = _search_industry_dialog_ele.ele(
                        SEARCH_PERSON_FILTER_SEARCH_INDUSTRY_INPUT_ATTACH_XPATH)
                    click_element_by_ele(page, _search_bar_ele)
                    _industry_list = _expectation_industry[_idx].split(';')
                    for _industry in _industry_list:
                        page.actions.key_down(Keys.CTRL).type('a').key_up(Keys.CTRL).type(_industry)
                        time.sleep(1)
                        _target_select_ele = _search_industry_dialog_ele.ele(
                            SEARCH_PERSON_FILTER_SEARCH_INDUSTRY_FIRST_ITEM_ATTACH_XPATH)
                        if _target_select_ele:
                            click_element_by_ele(page, _target_select_ele)
                    _confirm_btn_ele = _search_industry_dialog_ele.ele(
                        SEARCH_PERSON_FILTER_DIALOG_INDUSTRY_CONFIRM_ATTACH_XPATH)
                    click_element_by_ele(page, _confirm_btn_ele)
        # 当前职能
        if _current_function[_idx] != '':
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_CURRENT_FUNCTION_SELECT_ATTACH_XPATH, timeout=3)
            if _select_ele:
                click_element_by_ele(page, _select_ele)
                # 打开dialog
                _search_function_dialog_ele = page.ele(SEARCH_PERSON_FILTER_DIALOG_FUNCTION_LOCATION)
                if _search_function_dialog_ele:
                    _search_bar_ele = _search_function_dialog_ele.ele(SEARCH_PERSON_FILTER_FUNCTION_INPUT_ATTACH_XPATH,
                                                                      timeout=3)
                    click_element_by_ele(page, _search_bar_ele)
                    _function_list = _current_function[_idx].split(';')
                    for _function in _function_list:
                        page.actions.key_down(Keys.CTRL).type('a').key_up(Keys.CTRL).type(_function)
                        time.sleep(1)
                        _target_select_ele = _search_function_dialog_ele.ele(
                            SEARCH_PERSON_FILTER_FUNCTION_FIRST_ITEM_ATTACH_XPATH, timeout=3)
                        if _target_select_ele:
                            click_element_by_ele(page, _target_select_ele)
                    _confirm_btn_ele = _search_function_dialog_ele.ele(
                        SEARCH_PERSON_FILTER_DIALOG_FUNCTION_CONFIRM_ATTACH_XPATH, timeout=3)
                    click_element_by_ele(page, _confirm_btn_ele)
        # 期望职能
        if _expectation_function[_idx] != '':
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_EXPECTATION_FUNCTION_SELECT_ATTACH_XPATH, timeout=3)
            if _select_ele:
                click_element_by_ele(page, _select_ele)
                # 打开dialog
                _search_function_dialog_ele = page.ele(SEARCH_PERSON_FILTER_DIALOG_FUNCTION_LOCATION)
                if _search_function_dialog_ele:
                    _search_bar_ele = _search_function_dialog_ele.ele(SEARCH_PERSON_FILTER_FUNCTION_INPUT_ATTACH_XPATH,
                                                                      timeout=3)
                    click_element_by_ele(page, _search_bar_ele)
                    _function_list = _expectation_function[_idx].split(';')
                    for _function in _function_list:
                        page.actions.key_down(Keys.CTRL).type('a').key_up(Keys.CTRL).type(_function)
                        time.sleep(1)
                        _target_select_ele = _search_function_dialog_ele.ele(
                            SEARCH_PERSON_FILTER_FUNCTION_FIRST_ITEM_ATTACH_XPATH, timeout=3)
                        if _target_select_ele:
                            click_element_by_ele(page, _target_select_ele)
                    _confirm_btn_ele = _search_function_dialog_ele.ele(
                        SEARCH_PERSON_FILTER_DIALOG_FUNCTION_CONFIRM_ATTACH_XPATH, timeout=3)
                    click_element_by_ele(page, _confirm_btn_ele)
        # 目前年薪
        if _current_annual_salary[_idx] != '' and _current_annual_salary[_idx] != '不选择':
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_CURRENT_ANNUAL_SALARY_SELECT_ATTACH_XPATH,
                                               timeout=3)
            click_element_by_ele(page, _select_ele)
            _popup_click_ele(page, SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                '[object Object]' if _current_annual_salary[_idx] == '不限' else _current_annual_salary[_idx]))
            if _current_annual_salary[_idx] == '自定义':
                _begin, _end = _custom_current_annual_salary[_idx].split('-')
                _left_input_ele = _filter_wrap_ele.ele(
                    SEARCH_PERSON_FILTER_CURRENT_ANNUAL_SALARY_LEFT_INPUT_ATTACH_XPATH, timeout=3)
                click_element_by_ele(page, _left_input_ele)
                page.actions.type(_begin)
                _right_input_ele = _filter_wrap_ele.ele(
                    SEARCH_PERSON_FILTER_CURRENT_ANNUAL_SALARY_RIGHT_INPUT_ATTACH_XPATH, timeout=3)
                click_element_by_ele(page, _right_input_ele)
                page.actions.type(_end)
        # 期望年薪
        if _expectation_annual_salary[_idx] != '' and _expectation_annual_salary[_idx] != '不选择':
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_EXPECTATION_ANNUAL_SALARY_SELECT_ATTACH_XPATH,
                                               timeout=3)
            click_element_by_ele(page, _select_ele)
            _popup_click_ele(page,
                             SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                                 '[object Object]' if _expectation_annual_salary[_idx] == '不限' else
                                 _expectation_annual_salary[_idx]))
            if _expectation_annual_salary[_idx] == '自定义':
                _begin, _end = _custom_expectation_annual_salary[_idx].split('-')
                _left_input_ele = _filter_wrap_ele.ele(
                    SEARCH_PERSON_FILTER_EXPECTATION_ANNUAL_SALARY_LEFT_INPUT_ATTACH_XPATH, timeout=3)
                click_element_by_ele(page, _left_input_ele)
                page.actions.type(_begin)
                _right_input_ele = _filter_wrap_ele.ele(
                    SEARCH_PERSON_FILTER_EXPECTATION_ANNUAL_SALARY_RIGHT_INPUT_ATTACH_XPATH, timeout=3)
                click_element_by_ele(page, _right_input_ele)
                page.actions.type(_end)
        # 勾选单选框
        # 管理经验
        if _management_experience[_idx] != '不选择':
            _management_experience_checkbox_ele = _filter_wrap_ele.ele(
                SEARCH_PERSON_FILTER_MANAGEMENT_EXPERIENCE_CHECKBOX_ATTACH_XPATH, timeout=2)
            if _management_experience_checkbox_ele:
                if _management_experience[_idx] == '是' and _management_experience_checkbox_ele.attr(
                        'class') == SEARCH_PERSON_FILTER_CHECKBOX_FALSE_CLASS:
                    click_element_by_ele(page, _management_experience_checkbox_ele)  # 未选中 且需要选中
                if _management_experience[_idx] == '否' and _management_experience_checkbox_ele.attr(
                        'class') != SEARCH_PERSON_FILTER_CHECKBOX_FALSE_CLASS:
                    click_element_by_ele(page, _management_experience_checkbox_ele)  # 选中 且不需要选中
        if _work_overseas[_idx] != '不选择':
            _work_overseas_checkbox_ele = _filter_wrap_ele.ele(
                SEARCH_PERSON_FILTER_WORK_OVERSEAS_CHECKBOX_ATTACH_XPATH, timeout=2)
            if _work_overseas_checkbox_ele:
                if _work_overseas[_idx] == '是' and _work_overseas_checkbox_ele.attr(
                        'class') == SEARCH_PERSON_FILTER_CHECKBOX_FALSE_CLASS:
                    click_element_by_ele(page, _work_overseas_checkbox_ele)  # 未选中 且需要选中
                if _work_overseas[_idx] == '否' and _work_overseas_checkbox_ele.attr(
                        'class') != SEARCH_PERSON_FILTER_CHECKBOX_FALSE_CLASS:
                    click_element_by_ele(page, _work_overseas_checkbox_ele)  # 选中 且不需要选中
        # 专业
        if _professional[_idx] != '':
            _professional_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_PROFESSIONAL_INPUT_ATTACH_XPATH, timeout=2)
            if _professional_ele:
                click_element_by_ele(page, _professional_ele)
                page.actions.type(_professional[_idx])
        # 毕业院校
        if _graduation_university[_idx] != '':
            _graduation_university_ele = _filter_wrap_ele.ele(
                SEARCH_PERSON_FILTER_GRADUATION_UNIVERSITY_INPUT_ATTACH_XPATH,
                timeout=2)
            if _graduation_university_ele:
                click_element_by_ele(page, _graduation_university_ele)
                page.actions.type(_graduation_university[_idx])
        # 搜索框 有快捷搜索则不需要通过输入框
        if not _is_fast_search:
            print('点击搜索框')
            click_element_by_ele(page, _search_txt_ele)
            if _search_txt[_idx] != '':
                page.actions.type(_search_txt[_idx])
            page.actions.type('\n')
            time.sleep(1)  # 等待搜索完成
        # 完成搜索后的筛选
        if _communication_status[_idx] != '不选择':
            _communication_status_ele = _all_wrap_ele.ele(
                SEARCH_PERSON_SEARCHED_COMMUNICATION_STATUS_SELECT_ATTACH_XPATH, timeout=3)  # 获取沟通状态元素
            if _communication_status_ele:
                click_element_by_ele(page, _communication_status_ele)  # 点击沟通状态
                _popup_click_ele(page, SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                    _communication_status[_idx]))  # 点击目标
        if _contact_status[_idx] != '不选择':
            _contact_status_ele = _all_wrap_ele.ele(SEARCH_PERSON_SEARCHED_CONTACT_STATUS_SELECT_ATTACH_XPATH,
                                                    timeout=3)  # 获取联系状态元素
            if _contact_status_ele:
                click_element_by_ele(page, _contact_status_ele)  # 点击联系状态
                _popup_click_ele(page,
                                 SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(_contact_status[_idx]))  # 点击目标
        if _hide_looked[_idx] != '不选择':
            _hide_looked_ele = _all_wrap_ele.ele(SEARCH_PERSON_SEARCHED_HIDE_CHECKBOX_ATTACH_XPATH, timeout=2)
            if _hide_looked_ele:
                if _hide_looked[_idx] == '是' and _hide_looked_ele.attr(
                        'class') != SEARCH_PERSON_SEARCHED_HIDE_CHECKBOX_CHECKED_CLASS:
                    click_element_by_ele(page, _hide_looked_ele)  # 未选中 且需要选中
                if _hide_looked[_idx] == '否' and _hide_looked_ele.attr(
                        'class') == SEARCH_PERSON_SEARCHED_HIDE_CHECKBOX_CHECKED_CLASS:
                    click_element_by_ele(page, _hide_looked_ele)  # 选中 且不需要选中
        if _match_latest[_idx] != '不选择':
            _match_latest_ele = _all_wrap_ele.ele(SEARCH_PERSON_SEARCHED_MATCH_RECENT_CHECKBOX_ATTACH_XPATH, timeout=2)
            if _match_latest_ele:
                if _match_latest[_idx] == '是' and _match_latest_ele.attr(
                        'class') != SEARCH_PERSON_SEARCHED_MATCH_RECENT_CHECKBOX_CHECKED_CLASS:
                    click_element_by_ele(page, _match_latest_ele)  # 未选中 且需要选中
                if _match_latest[_idx] == '否' and _match_latest_ele.attr(
                        'class') == SEARCH_PERSON_SEARCHED_MATCH_RECENT_CHECKBOX_CHECKED_CLASS:
                    click_element_by_ele(page, _match_latest_ele)  # 选中 且不需要选中
        _now_person_num = 0
        _need_person_num = int(_person_say_num[_idx])
        while True:
            _person_item_list = page.s_eles(SEARCH_PERSON_COMMUNICATION_LIST_XPATH, timeout=3)
            if not _person_item_list:
                print('列表不存在')
                break
            for _list_idx, _person_item in enumerate(_person_item_list):
                if _now_person_num >= _need_person_num:
                    print(f'当前{_current_job_name}打招呼完成，共{_now_person_num}个')
                    break
                _now_communication_ele = _person_item.ele('立即沟通')
                if _now_communication_ele:
                    _truth_person_item_ele = page.ele(
                        SEARCH_PERSON_COMMUNICATION_LIST_ITEM_XPATH_PATTERN.format(_list_idx + 1), timeout=3)
                    _truth_now_communication_ele = _truth_person_item_ele.ele('立即沟通')
                    if not _truth_now_communication_ele:
                        print('未找到立即沟通按钮')
                        continue
                    click_element_by_ele(page, _truth_person_item_ele.ele('立即沟通'))
                    # 解决可能出现的 立即沟通和继续沟通未同步导致的状态错误 弹出对话框
                    _check_continue_dialog_ele = page.ele(
                        SEARCH_PERSON_COMMUNICATION_CONTINUE_COMMUNICATION_MASK_LOCATION,
                        timeout=2)
                    if _check_continue_dialog_ele:
                        _close_btn_ele = _check_continue_dialog_ele.ele(
                            SEARCH_PERSON_COMMUNICATION_CONTINUE_COMMUNICATION_CLOSE_ATTACH_XPATH, timeout=3)
                        click_element_by_ele(page, _close_btn_ele)
                        continue
                    # 选择沟通职位
                    _communication_dialog_ele = page.ele(SEARCH_PERSON_COMMUNICATION_DIALOG_LOCATION, timeout=3)
                    if _communication_dialog_ele:
                        _search_input_ele = _communication_dialog_ele.ele(
                            SEARCH_PERSON_COMMUNICATION_DIALOG_SEARCH_INPUT_ATTACH_XPATH, timeout=3)  # 获取搜索框
                        click_element_by_ele(page, _search_input_ele)
                        page.actions.type(_current_job_name)  # 输入当前职位名称
                        time.sleep(1)
                        _item_ele_list = _communication_dialog_ele.s_eles(SEARCH_PERSON_COMMUNICATION_DIALOG_LIST_XPATH,
                                                                          timeout=3)
                        _job_idx = 1
                        for i, _ele in enumerate(_item_ele_list):
                            _job_name_ele = _ele.ele(SEARCH_PERSON_COMMUNICATION_DIALOG_ITEM_JOB_NAME_ATTACH_XPATH,
                                                     timeout=3)
                            _job_loc_ele = _ele.ele(SEARCH_PERSON_COMMUNICATION_DIALOG_ITEM_JOB_LOC_ATTACH_XPATH,
                                                    timeout=3)
                            if _job_name_ele and _job_loc_ele:
                                _job_name = _job_name_ele.text.strip('"\'')
                                _job_loc = _job_loc_ele.text.strip('"\'')
                                if _job_name == _current_job_name and _job_loc == _current_job_loc:
                                    _job_idx = i + 1
                                    break
                        _click_item_ele = _communication_dialog_ele.ele(
                            SEARCH_PERSON_COMMUNICATION_DIALOG_LIST_ITEM_XPATH_PATTERN.format(_job_idx), timeout=3)
                        click_element_by_ele(page, _click_item_ele)
                        _confirm_btn_ele = _communication_dialog_ele.ele(
                            SEARCH_PERSON_COMMUNICATION_DIALOG_CONFIRM_ATTACH_XPATH, timeout=3)
                        if _confirm_btn_ele:
                            click_element_by_ele(page, _confirm_btn_ele)
                            _now_person_num += 1
                            print(f'当前{_current_job_name}打招呼进度：{_now_person_num}/{_need_person_num}')
                    else:
                        print('未获取到沟通职位对话框')
                else:
                    print('未找到立即沟通按钮')
            if _now_person_num >= _need_person_num:
                break
            # 翻页
            _next_page_ele = page.ele(SEARCH_PERSON_COMMUNICATION_LIST_NEXT_PAGE_LOCATION, timeout=3)
            if _next_page_ele:
                click_element_by_ele(page, _next_page_ele)
            else:
                print('没有下一页')
                break


def load_industry_cache(page, need_load):
    """
    初始化职位
    :param page:
    :param need_load:
    :return:
    """
    # 先判断是否有缓存文件
    if getattr(sys, 'frozen', False):
        job_file_path = os.path.join(os.path.dirname(sys.executable), 'job_list.txt')
    else:
        job_file_path = os.path.join(os.path.dirname(__file__), 'job_list.txt')
    job_list = []
    need_save = False
    if os.path.exists(job_file_path):
        try:
            with open(job_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                job_list = [line.strip() for line in lines if line.strip()]
        except Exception as e:
            print(f'读取职位列表文件失败:{e}')
    if need_load:
        page.get(URL_JOB_MANAGEMENT)  # 前往职位管理界面
        time.sleep(2)
        while True:
            _job_item_ele_list = page.s_eles(JOB_MANAGEMENT_LIST_XPATH, timeout=3)
            for _job_item_ele in _job_item_ele_list:
                _job_name_ele = _job_item_ele.ele(JOB_MANAGEMENT_LIST_ITEM_JOB_NAME_ATTACH_XPATH, timeout=3)
                _job_loc_ele = _job_item_ele.ele(JOB_MANAGEMENT_LIST_ITEM_JOB_NAME_DESC_ATTACH_XPATH, timeout=3)
                if not _job_name_ele or not _job_loc_ele:
                    print('当前职位未匹配到名称或地址')
                    continue
                _job_name = _job_name_ele.attr('title')
                _job_loc = _job_loc_ele.text
                _job_info = _job_name + ',' + _job_loc
                _end_flag = _job_item_ele.attr('class') == JOB_MANAGEMENT_TOP_CLASS  # 当前是否是置顶职位
                _have_flag = _job_info in job_list  # 职位是否已经存在
                if _have_flag and not _end_flag:
                    break  # 当前非置顶职位且列表中有该职位，说明已经遍历过新增职位了
                if not _have_flag:
                    print(f'添加新职位{_job_info}')
                    job_list.append(_job_info)  # 保存职位
                    need_save = True
            _next_page_ele = page.ele(JOB_MANAGEMENT_NEXT_PAGE_LOCATION, timeout=3)
            if _next_page_ele:
                click_element_by_ele(page, _next_page_ele)
                continue
            else:
                print('未找到职位列表翻页元素')
                break
    if need_save:
        try:
            with open(job_file_path, 'w', encoding='utf-8') as f:
                for job in job_list:
                    f.write(job + '\n')
        except Exception as e:
            print(f'保存职位列表文件失败:{e}')
    return job_list


def do_chain(page, need_load):
    say_hello(page, load_industry_cache(page, need_load))
    while True:
        proactive_resume(page)
        passive_resume(page)


@deadline_decorator
def run(_deadline_time: str, _need_load: bool):
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
    do_chain(page, _need_load)


def prepare_run():
    _deadline_time, _need_load = safe_gui_call(popup_mixed_inputs, [
        {'type': 'input', 'title': '自动终止时间(24小时制),不填默认20:00:00'},
        {'type': 'select', 'title': '是否加载职位', 'choices': ['否', '是']}
    ])
    run(_deadline_time, True if _need_load == '是' else False)


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
