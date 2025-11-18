import queue
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

_gui_queue = queue.Queue()
root = None


class SingleInputDialog(simpledialog.Dialog):
    def __init__(self, parent, title, ok_text='确定', cancel_text='取消'):
        self.entry = None
        self._title = title
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        super().__init__(parent, title='输入')

    def body(self, master):
        tk.Label(master, text=self._title).pack()
        self.entry = tk.Entry(master)
        self.entry.pack()
        return self.entry

    def buttonbox(self):
        """创建自定义文本的按钮"""
        box = tk.Frame(self)

        w = tk.Button(box, text=self.ok_text, width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=self.cancel_text, width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def apply(self):
        self.result = self.entry.get()


class MultiInputDialog(simpledialog.Dialog):
    def __init__(self, parent, titles, ok_text='确定', cancel_text='取消'):
        self.titles = titles  # 输入框标题列表
        self.entries = []
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        super().__init__(parent, title="多输入框")

    def body(self, master):
        for i, title in enumerate(self.titles):
            tk.Label(master, text=title).grid(row=i, column=0)
            entry = tk.Entry(master)
            entry.grid(row=i, column=1)
            self.entries.append(entry)
        return self.entries[0]  # 初始焦点设在第一个输入框

    def buttonbox(self):
        """创建自定义文本的按钮"""
        box = tk.Frame(self)

        w = tk.Button(box, text=self.ok_text, width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=self.cancel_text, width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

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


class MixedInputDialog(simpledialog.Dialog):
    def __init__(self, parent, config_list, ok_text="确定", cancel_text="取消"):
        """
        config_list: 包含配置字典的列表，每个字典定义一个控件
        字典格式:
        - {'type': 'input', 'title': '输入框标题'}
        - {'type': 'multiselect', 'title': '多选框标题', 'choices': ['选项1', '选项2']}
        """
        self.config_list = config_list
        self.controls = []
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        super().__init__(parent, title="混合输入对话框")

    def body(self, master):
        for i, config in enumerate(self.config_list):
            # 创建标题标签
            tk.Label(master, text=config['title']).grid(row=i, column=0, sticky="w", padx=5, pady=2)

            if config['type'] == 'input':
                # 创建输入框
                entry = tk.Entry(master, width=60)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                self.controls.append(entry)
            elif config['type'] == 'multiselect':
                # 创建多选列表框
                listbox = tk.Listbox(master, selectmode=tk.MULTIPLE, width=60, height=6, exportselection=0)
                for choice in config['choices']:
                    listbox.insert(tk.END, choice)
                listbox.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                self.controls.append(listbox)

            master.columnconfigure(1, weight=1)

        return self.controls[0] if self.controls else None

    def buttonbox(self):
        """创建自定义文本的按钮"""
        box = tk.Frame(self)

        w = tk.Button(box, text=self.ok_text, width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=self.cancel_text, width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def apply(self):
        self.result = []
        for i, config in enumerate(self.config_list):
            control = self.controls[i]
            if config['type'] == 'input':
                self.result.append(control.get())
            elif config['type'] == 'multiselect':
                selections = [control.get(j) for j in control.curselection()]
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
    user_input = SingleInputDialog(root, prompt)
    return user_input.result if hasattr(user_input, 'result') else None


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


def popup_mixed_inputs(config_list: list[dict], ok_text: str = "确定", cancel_text: str = "取消") -> list[str] | None:
    """
    弹出包含多种类型控件的对话框

    Args:
        config_list: 控件配置列表
        ok_text:
        cancel_text
    Returns:
        list[str] | None: 用户输入或选择的结果列表

    示例：
    >>> result = popup_mixed_inputs([
            {'type': 'input', 'title': '自定义职位名称:'},
            {'type': 'multiselect', 'title': '选择筛选条件:', 'choices': ['男', '女', '应届生']}
        ])
    >>> print(result)
    """
    dialog = MixedInputDialog(root, config_list, ok_text, cancel_text)
    return dialog.result if hasattr(dialog, 'result') else None
