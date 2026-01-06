import os
import threading
import time
import traceback

from base_operates import open_browser, click_element, click_element_by_ele
from simple_dialog import get_global_root, safe_gui_call, popup_input, popup_mixed_inputs
from timer_function_decorator import deadline_decorator

# 筛选项
JOB_SELECT_CHOICES = ['全部职位', '目前职位', '过往职位']
COMPANY_SELECT_CHOICES = ['全部公司', '目前公司', '过往公司']
EXPERIENCE_CHOICES = ['不限', '在校/应届', '1-3年', '3-5年', '5-10年', '自定义']
EDUCATION_CHOICES = ['不限', '本科', '硕士', '博士/博士后', '大专', '中专/中技', '高中及以下']
UNIFIED_RECRUITMENT_REQUIREMENT_CHOICES = ['不限', '统招本科', '统招硕士', '统招博士', '统招大专']
UNIVERSITY_REQUIREMENT_CHOICES = ['不限', '211', '985', '双一流', '海外留学']
ACTIVE_STATUS_CHOICES = ['不限', '今天活跃', '3天内活跃', '7天内活跃', '30天内活跃', '最近三个月活跃', '最近半年活跃']
JOB_HUNTING_CHOICES = ['不限', '离职，正在找工作', '在职，急寻新工作', '在职，看看新机会', '在职，暂无跳槽打算']
FREQUENCY_OF_JOB_HOPPING_CHOICES = ['不限', '近5年不超过3段', '近3年不超过2段', '近2段均不低于2年']
AGE_REQUIREMENT_CHOICES = ['不限', '20-25岁', '25-30岁', '30-35岁', '35-40岁', '40岁以上']
SEX_REQUIREMENT_CHOICES = ['不限', '男', '女']
LANGUAGE_REQUIREMENT_CHOICES = ['不限', '英语', '日语', '粤语']
GRADUATION_YEAR_CHOICES = ['不限', '2025年毕业', '2026年毕业', '2027年毕业', '2028年毕业', '2029年毕业', '2030年毕业']
CURRENT_ANNUAL_SALARY_CHOICES = ['不限', '5万以下', '5-10万', '10-20万', '20-30万', '30-40万', '40-50万', '50-65万',
                                 '65-80万',
                                 '80-100万', '100万以上']
EXPECTATION_ANNUAL_SALARY_CHOICES = ['不限', '5万以下', '5-10万', '10-20万', '20-30万', '30-40万', '40-50万', '50-65万',
                                     '65-80万',
                                     '80-100万', '100万以上']
RESUME_LANGUAGE_CHOICES = ['不限', '中文简历', '英文简历']
NATURE_OF_THE_COMPANY_CHOICES = ['不限', '外商独资/外企办事处', '中外合营(合资/合作)', '私营/民营企业', '国有企业',
                                 '国内上市公司', '政府机关／非盈利机构', '事业单位', '其他']

URL_LOGIN = 'https://lpt.liepin.com'
URL_SEARCH_PERSON = 'https://lpt.liepin.com/search'
SEARCH_PERSON_FILTER_WRAP_CLASS = r'@class=wrap--bbDaK'  # 筛选栏class
SEARCH_PERSON_FILTER_CLICK_ATTACH_FILTER_WRAP_XPATH = r'xpath:/div[3]'  # 在筛选栏中的筛选项wrap 相对xpath
# 以下相对xpath都是基于SEARCH_PERSON_FILTER_CLICK_ATTACH_FILTER_WRAP_XPATH
SEARCH_PERSON_FILTER_JOB_INPUT_ATTACH_XPATH = r'xpath:/div[2]/div/div[1]/div/div[2]/div/div[1]/div/span[1]/span/input'  # 筛选项中的职位输入框 相对xpath
SEARCH_PERSON_FILTER_JOB_SELECT_ATTACH_XPATH = r'xpath:/div[2]/div/div[1]/div/div[2]/div/div[2]/div'  # 职位栏中选择框
SEARCH_PERSON_FILTER_COMPANY_INPUT_ATTACH_XPATH = r'xpath:/div[2]/div/div[2]/div/div[2]/div/div[1]/div/span[1]/span/input'  # 筛选项中公司输入框 相对xpath
SEARCH_PERSON_FILTER_COMPANY_SELECT_ATTACH_XPATH = r'xpath:/div[2]/div/div[2]/div/div[2]/div/div[2]/div'  # 公司栏中选择框
SEARCH_PERSON_FILTER_FAST_SEARCH_ATTACH_XPATH_PATTERN = r'xpath:/div[3]/div[1]/div/div/div/div/div/span[{0}]'  # 快捷搜索 相对xpath模板 format选中项下标+1

SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_XPATH_PATTERN = r'xpath:/div[3]/div[4]/div/div/label[{0}]'  # 经验筛选项 相对xpath模板 format选中项下标 + 1
SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_CUSTOM_LEFT_INPUT_XPATH = r'xpath:/div[3]/div[4]/div/div/div/div[2]/div/span[1]/span/input'  # 自定义经验左侧输入框
SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_CUSTOM_RIGHT_INPUT_XPATH = r'xpath:/div[3]/div[4]/div/div/div/div[2]/div/span[2]/span/input'  # 自定义经验右侧输入框
SEARCH_PERSON_FILTER_EDUCATION_ATTACH_XPATH_PATTERN = r'xpath:/div[3]/div[5]/div/div/label[{0}]'  # 教育经历筛选项 相对xpath模板 format选中项下标+1
SEARCH_PERSON_FILTER_UNIFIED_ATTACH_XPATH = r'xpath:/div[3]/div[5]/div/div/div[2]'  # 统招要求选择框 相对xpath
SEARCH_PERSON_FILTER_UNIVERSITY_ATTACH_XPATH = r'xpath:/div[3]/div[5]/div/div/div[4]'  # 院校要求 相对xpath

SEARCH_PERSON_FILTER_MORE_FILTER_CLASS = r'@class=antlpticon antlpticon-select-down switchIcon--r9Pa9'  # 更多条件筛选项 找不到说明已经打开
SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN = r'xapth:/div[3]/div[6]/div/div/div/div[{0}]'  # 活跃状态选择框 相对xpath
SEARCH_PERSON_FILTER_MANAGEMENT_EXPERIENCE_LABEL_ATTACH_XPATH = r'xpath:/div[3]/div[6]/div/div/div/label[1]'  # 管理经验单选框 相对xpath
SEARCH_PERSON_FILTER_WORK_OVERSEAS_LABEL_ATTACH_XPATH = 'xpath:/div[3]/div[6]/div/div/div/label[2]'  # 海外工作单选框 相对xpath

SEARCH_PERSON_FILTER_RESET_SEARCH_ATTACH_XPATH = r'xpath:/span'  # 重置条件按钮 相对xpath
# 全局查询
SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION = r'@@class=ant-lpt-select-item ant-lpt-select-item-option@@title={0}'

SEARCH_PERSON_FAST_SEARCH_CLASS = r'@class=ant-lpt-tag ant-lpt-teno-tag ant-lpt-teno-tag-small'
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


def say_hello(page):
    """
    搜索牛人中 根据筛选项筛选并沟通
    :param page:
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
    _all_lists = [
        _person_say_num, _person_job, _person_job_select, _person_company, _person_company_select,
        _fast_search, _current_city, _expectation_city, _experience, _custom_experience,
        _education_experience, _unified_recruitment_requirement, _university_requirement,
        _active_status, _job_hunting_status, _frequency_of_job_hopping, _age_requirement,
        _custom_age_requirement, _sex_requirement, _language_requirement, _custom_language_requirement,
        _graduation_year, _current_industry, _expectation_industry, _current_function,
        _expectation_function, _current_annual_salary, _custom_current_annual_salary,
        _expectation_annual_salary, _custom_expectation_annual_salary, _resume_language,
        _nature_of_the_company, _management_experience, _work_overseas, _professional,
        _graduation_university
    ]
    _more_filter_list_start_idx = 13
    _more_filter_list_end_idx = 32
    _iter_idx = 0
    while True:
        result = safe_gui_call(popup_mixed_inputs, [
            {'type': 'input', 'title': '人数'},
            {'type': 'input', 'title': '职位'},
            {'type': 'select', 'title': '全部/目前/过往职位',
             'choices': JOB_SELECT_CHOICES},
            {'type': 'input', 'title': '公司'},
            {'type': 'select', 'title': '全部/目前/过往公司',
             'choices': COMPANY_SELECT_CHOICES},
            {'type': 'select', 'title': '快捷搜索', 'choices': _fast_search_txt_list},
            {'type': 'input', 'title': '目前城市(多个用;分隔)'},
            {'type': 'input', 'title': '期望城市(多个用;分隔)'},
            {'type': 'select', 'title': '经验', 'choices': EXPERIENCE_CHOICES},
            {'type': 'input', 'title': '自定义经验(-分隔)'},
            {'type': 'multiselect', 'title': '教育经历', 'choices': EDUCATION_CHOICES},
            {'type': 'select', 'title': '统招要求', 'choices': UNIFIED_RECRUITMENT_REQUIREMENT_CHOICES},
            {'type': 'select', 'title': '院校要求', 'choices': UNIVERSITY_REQUIREMENT_CHOICES},
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
            {'type': 'checkbox', 'title': '', 'text': '管理经验'},
            {'type': 'checkbox', 'title': '', 'text': '海外工作'},
            {'type': 'input', 'title': '专业名称'},
            {'type': 'input', 'title': '毕业院校'},
        ], '确认', '停止选择')
        if not result:
            break
        _iter_idx += 1
        for lst, val in zip(_all_lists, result):
            lst.append(val)
    _filter_wrap_ele = page.ele(SEARCH_PERSON_FILTER_WRAP_CLASS).ele(
        SEARCH_PERSON_FILTER_CLICK_ATTACH_FILTER_WRAP_XPATH)
    for _idx in range(_iter_idx):
        _reset_search_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_RESET_SEARCH_ATTACH_XPATH, timeout=3)
        if not _reset_search_ele:
            print('未找到重置条件元素')
            continue
        click_element_by_ele(page, _reset_search_ele)  # 点击重置条件
        if _fast_search[_idx] != '不选择':
            _fast_idx = _fast_search_txt_list.index(_fast_search[_idx]) + 1
            _fast_search_ele = _filter_wrap_ele.ele(
                SEARCH_PERSON_FILTER_FAST_SEARCH_ATTACH_XPATH_PATTERN.format(_fast_idx), timeout=3)
            if not _fast_search_ele:
                print(f'未找到对应快捷搜索项{_fast_search[_idx]}')
                continue
            click_element_by_ele(page, _fast_search_ele)
        if _person_job[_idx] != '':
            _job_input_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_JOB_INPUT_ATTACH_XPATH, timeout=3)
            click_element_by_ele(page, _job_input_ele)  # 点击输入框
            page.actions.type(_person_job[_idx])
            _job_select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_JOB_SELECT_ATTACH_XPATH, timeout=3)
            click_element_by_ele(page, _job_select_ele)  # 点击选择框
            _target_select_ele = page.ele(
                SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(_person_job_select[_idx]))
            if _target_select_ele:
                click_element_by_ele(page, _target_select_ele)  # 只有存在才点击，因为可能是当前选中项，则不需要点击
        if _person_company[_idx] != '':
            _company_input_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_COMPANY_INPUT_ATTACH_XPATH, timeout=3)
            click_element_by_ele(page, _company_input_ele)  # 点击输入框
            page.actions.type(_person_company[_idx])
            _company_select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_COMPANY_SELECT_ATTACH_XPATH, timeout=3)
            click_element_by_ele(page, _company_select_ele)  # 点击选择框
            _target_select_ele = page.ele(
                SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(_person_company_select[_idx]))
            if _target_select_ele:
                click_element_by_ele(page, _target_select_ele)  # 只有存在才点击，因为可能是当前选中项，则不需要点击
        # if _current_city[_idx] != '':
        _experience_ele = _filter_wrap_ele.ele(
            SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_XPATH_PATTERN.format(
                EXPERIENCE_CHOICES.index(_experience[_idx]) + 1),
            timeout=3)  # 经验筛选项
        if _experience_ele:
            click_element_by_ele(page, _experience_ele)
            if _experience[_idx] == '自定义':
                # 需要输入经验
                _begin, _end = _custom_experience[_idx].split('-')
                _begin_input_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_CUSTOM_LEFT_INPUT_XPATH,
                                                        timeout=1)
                click_element_by_ele(page, _begin_input_ele)
                page.actions.type(_begin)
                _end_input_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_EXPERIENCE_ATTACH_CUSTOM_RIGHT_INPUT_XPATH,
                                                      timeout=1)
                click_element_by_ele(page, _end_input_ele)
                page.actions.type(_end)
        if _education_experience[_idx] != '':
            _education_experience_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_EDUCATION_ATTACH_XPATH_PATTERN.format(
                EDUCATION_CHOICES.index(_education_experience[_idx]) + 1), timeout=2)  # 教育经历筛选项
            if _education_experience_ele:
                click_element_by_ele(page, _education_experience_ele)
        _unified_requirement_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_UNIFIED_ATTACH_XPATH, timeout=2)  # 统招要求选择框
        if _unified_requirement_ele:
            click_element_by_ele(page, _unified_requirement_ele)  # 点击选择框
            _target_select_ele = page.ele(SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                '[object Object]' if _unified_recruitment_requirement[_idx] == '不限' else
                _unified_recruitment_requirement[_idx]))
            if _target_select_ele:
                click_element_by_ele(page, _target_select_ele)
        _university_requirement_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_UNIVERSITY_ATTACH_XPATH,
                                                           timeout=2)  # 院校要求选择框
        if _university_requirement_ele:
            click_element_by_ele(page, _university_requirement_ele)  # 点击选择框
            _target_select_ele = page.ele(SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format(
                '[object Object]' if _university_requirement[_idx] == '不限' else _university_requirement[_idx],
                timeout=2))
            if _target_select_ele:
                click_element_by_ele(page, _target_select_ele)
        _more_filter_ele = page.ele(SEARCH_PERSON_FILTER_MORE_FILTER_CLASS, timeout=2)
        if _more_filter_ele:
            click_element_by_ele(page, _more_filter_ele)
        # 以下开始更多筛选选择
        for _lst_idx, _lst in enumerate(_all_lists[_more_filter_list_start_idx:_more_filter_list_end_idx]):
            _select_ele = _filter_wrap_ele.ele(SEARCH_PERSON_FILTER_MORE_FILTER_SELECT_ATTACH_XPATH_PATTERN.format(_lst_idx + 1), timeout=2)
            if _select_ele:
                click_element_by_ele(page, _select_ele)
                _target_select_ele = page.ele(SEARCH_PERSON_FILTER_SELECT_PATTERN_LOCATION.format('[object Object]' if _lst[_idx] == '不限' else _lst[_idx]))
                if _target_select_ele:
                    click_element_by_ele(page, _target_select_ele)
        # 勾选单选框



def do_chain(page):
    say_hello(page)
    # while True:
    #     proactive_resume(page)
    #     passive_resume(page)


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
