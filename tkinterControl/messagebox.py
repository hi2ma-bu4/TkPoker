# coding: utf-8
"""
tkinterのmessageboxを簡単に操作出来るようにしたやつ
"""

from typing import Optional, Literal, cast
from tkinter import messagebox


# type aliases
ta_showOpt = Literal[
    "info", "error", "warning", "question",
    "okcancel", "yesno", "yesnocancel",
    "retrycancel"
]
ta_showIcon = Literal["info", "warning", "error", "question"]
ta_showType = Literal[
    "ok", "okcancel",
    "yesno", "yesnocancel",
    "retrycancel", "abortretryignore"
]
ta_showDefault = Literal[
    "ok", "cancel",
    "yes", "no",
    "retry", "abort", "ignore"
]

# ここまで


class _Tkc_Messagebox:
    """
    メッセージボックス管理クラス
    """

    def __init__(self) -> None:
        pass

    def show(self, type: ta_showOpt = "info", message: str = "", title: str = "", *, detail: Optional[str] = None) -> Literal[1, 0, -1]:
        ret = -1
        if type == "info":
            messagebox.showinfo(title, message, detail=detail)
            ret = 1
        elif type == "error":
            messagebox.showerror(title, message, detail=detail)
            ret = 1
        elif type == "warning":
            messagebox.showwarning(title, message, detail=detail)
            ret = 1
        elif type == "question":
            ret = messagebox.askquestion(title, message, detail=detail)
            ret = 1 if ret == "yes" else 0
        elif type == "okcancel":
            ret = messagebox.askokcancel(title, message, detail=detail)
            ret = +ret
        elif type == "yesno":
            ret = messagebox.askyesno(title, message, detail=detail)
            ret = +ret
        elif type == "yesnocancel":
            ret = messagebox.askyesnocancel(title, message, detail=detail)
            ret = -1 if ret is None else +ret
        elif type == "retrycancel":
            ret = messagebox.askretrycancel(title, message, detail=detail)
            ret = +ret
        return cast(Literal[1, 0, -1], ret)

    def showCustom(self, message: str = "", title: str = "", *, detail: Optional[str] = None, icon: ta_showIcon = "info", type: ta_showType = "ok", default: ta_showDefault = "ok") -> ta_showDefault:
        return cast(ta_showDefault, messagebox.askquestion(title, message, detail=detail, icon=icon, type=type, default=default))
