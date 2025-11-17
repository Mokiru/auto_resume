import queue
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

_gui_queue = queue.Queue()
root = None


class MultiInputDialog(simpledialog.Dialog):
    def __init__(self, parent, titles):
        self.titles = titles  # 输入框标题列表
        self.entries = []
        super().__init__(parent, title="多输入框")

    def body(self, master):
        for i, title in enumerate(self.titles):
            tk.Label(master, text=title).grid(row=i, column=0)
            entry = tk.Entry(master)
            entry.grid(row=i, column=1)
            self.entries.append(entry)
        return self.entries[0]  # 初始焦点设在第一个输入框

    def apply(self):
        self.result = [entry.get() for entry in self.entries]


class MultiSelectDialog(simpledialog.Dialog):
    def __init__(self, parent, titles, choices_list):
        self.titles = titles
        self.choices_list = choices_list
        self.listboxes = []
        super().__init__(parent, title="多选下拉框")

    def body(self, master):
        for i, (title, choices) in enumerate(zip(self.titles, self.choices_list)):
            # 创建标题标签
            tk.Label(master, text=title).grid(row=i, column=0, sticky="w", padx=5, pady=2)

            # 创建支持多选的列表框，禁用自动清除选择
            listbox = tk.Listbox(master, selectmode=tk.MULTIPLE, width=60, height=10, exportselection=0)
            for choice in choices:
                listbox.insert(tk.END, choice)
            listbox.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            self.listboxes.append(listbox)

            # 配置列权重使列表框可伸缩
            master.columnconfigure(1, weight=1)

        return self.listboxes[0]  # 设置初始焦点

    def apply(self):
        # 将每个列表框的选择结果转换为分号分隔的字符串
        self.result = []
        for listbox in self.listboxes:
            selections = [listbox.get(i) for i in listbox.curselection()]
            self.result.append(';'.join(selections))


def popup_multiple_inputs(prompts: list[str]) -> list[str] | None:
    """
    弹出包含多个输入框的对话框，返回字符串列表或 None（点取消）
    示例：
    >>> inputs = popup_multiple_inputs(["姓名:", "年龄:"])
    >>> print(inputs)
    ['张三', '25']
    """
    dialog = MultiInputDialog(root, prompts)
    return dialog.result if hasattr(dialog, 'result') else None


def popup_multiple_multiselect(titles: list[str], choices_list: list[list[str]]) -> list[str] | None:
    """
    弹出包含多个多选下拉框的对话框，返回分号分隔的字符串列表或 None（点取消）

    Args:
        titles: 每个多选框的标题列表
        choices_list: 每个多选框对应的选项列表的列表

    Returns:
        list[str] | None: 每个选择结果都是分号分隔的字符串

    示例：
    >>> results = popup_multiple_multiselect(
        ["选择职位", "选择经验要求"],
        [["产品经理", "开发工程师", "设计师"], ["1-3年", "3-5年", "5年以上"]]
    )
    >>> print(results)
    ['产品经理;开发工程师', '3-5年;5年以上']
    """
    dialog = MultiSelectDialog(root, titles, choices_list)
    return dialog.result if hasattr(dialog, 'result') else None


def popup_input(prompt: str = "请输入值") -> str | None:
    """弹出输入框，返回字符串或 None（点取消）"""
    user_input = simpledialog.askstring("输入", prompt, parent=root)
    return user_input


def show_warning_dialog(message: str, title: str = "警告"):
    """显示警告消息弹窗"""
    messagebox.showwarning(title, message)


def get_global_root():
    """获取全局 Tk 实例"""
    global root
    if root is None:
        root = tk.Tk()
        root.withdraw()
        root.resizable(False, False)
        root.attributes('-topmost', True)

        # 注册定期检查队列的回调
        def check_queue():
            try:
                while True:
                    func, args, kwargs, result_queue = _gui_queue.get_nowait()
                    try:
                        result = func(*args, **kwargs)
                        if result_queue:
                            result_queue.put(('success', result))
                    except Exception as e:
                        if result_queue:
                            result_queue.put(('error', e))
            except queue.Empty:
                pass
            # 定期重新调度自己
            root.after(100, check_queue)  # 每100ms检查一次

        root.after(100, check_queue)
    return root


def safe_gui_call(func, *args, **kwargs):
    """线程安全的 GUI 调用"""
    if threading.current_thread() is threading.main_thread():
        return func(*args, **kwargs)
    else:
        result_queue = queue.Queue()
        _gui_queue.put((func, args, kwargs, result_queue))
        status, result = result_queue.get()
        if status == 'error':
            raise result
        return result
