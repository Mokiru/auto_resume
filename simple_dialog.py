import tkinter as tk
from tkinter import simpledialog, messagebox


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


def popup_multiple_inputs(prompts: list[str]) -> list[str] | None:
    """
    弹出包含多个输入框的对话框，返回字符串列表或 None（点取消）
    示例：
    >>> inputs = popup_multiple_inputs(["姓名:", "年龄:"])
    >>> print(inputs)
    ['张三', '25']
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.resizable(False, False)
    root.attributes('-topmost', True)  # 置顶

    dialog = MultiInputDialog(root, prompts)
    root.destroy()
    return dialog.result if hasattr(dialog, 'result') else None


def popup_input(prompt: str = "请输入值") -> str | None:
    """弹出输入框，返回字符串或 None（点取消）"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.resizable(False, False)

    root.attributes('-topmost', True)  # 置顶
    user_input = simpledialog.askstring("输入", prompt, parent=root)
    root.destroy()
    return user_input


def show_warning_dialog(message: str, title: str = "警告"):
    """显示警告消息弹窗"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes('-topmost', True)  # 置顶显示
    messagebox.showwarning(title, message)
    root.destroy()
