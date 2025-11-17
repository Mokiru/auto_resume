import tkinter as tk
from tkinter import simpledialog, messagebox


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
