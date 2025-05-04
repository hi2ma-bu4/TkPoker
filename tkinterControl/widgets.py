# coding: utf-8
"""
tkinterのwidgetを簡単に操作出来るようにしたやつ
"""

from typing import Any, Dict, Tuple, List, Callable, Union, Optional, Literal, TypeVar, cast, Final, overload

import tkinter.ttk as ttk
import tkinter.font as font

from .variable import _Tkc_Variable, tk, ta_val, ta_type
from .canvas import _Tkc_Canvas, ta_cusImageTk as _ta_cusImageTk
from lib.calc2d import Vector2, classControl, ta_pos
from lib.stringLib import listFind

# type aliases
ta_opInt = Optional[int]

ta_opPos = Union[Literal[True], ta_pos]

ta_tkttk = Literal["tk", "ttk"]
ta_com = Optional[Callable[..., Any]]

ta_cusFont = Union[font.Font, str]

ta_cusImageTk = Optional[_ta_cusImageTk]

ta_side = Literal["left", "right", "top", "bottom"]
ta_fill = Literal["none", "x", "y", "both"]

ta_anchor = Literal["nw", "n", "ne", "w", "c", "e", "sw", "s", "se"]
ta_justify = Literal["left", "right", "center"]

ta_sc_orient = Literal["horizontal", "vertical"]

ta_btn_state = Literal["normal", "disabled"]
ta_inp_state = Union[ta_btn_state, Literal["readonly"]]

ta_lb_select = Literal["single", "browse", "multiple"]
ta_lb_activestyle = Literal["dot", "underline", "none"]

ta_tr_show = List[Literal["tree", "headings"]]

ta_pro_mode = Literal["determinate", "indeterminate"]

ta_wrap = Literal["none", "char", "word"]
# ここまで


class _Tkc_Widgets:
    """
    ウェジット管理クラス
    """

    def __init__(self, _base, frame: tk.Frame, names: List[str], *, tabTraversal: str = "", useVariable: Optional[_Tkc_Variable] = None) -> None:
        self._base = _base

        self._frame: Final[tk.Frame] = frame
        self._name: Final[str] = names[0]

        if len(names) > 1:
            self._parent = names[1:]
        else:
            self._parent = []

        self._list: Final[List[tk.Widget]] = []
        self._nameIndDict: Final[Dict[str, int]] = {}

        self._focusList: Final[List[Dict[str, Any]]] = []
        self._firstFocus: Optional[tk.Widget] = None

        self._tabTraversal: Final[str] = tabTraversal

        uv = useVariable
        if uv is None:
            uv = _Tkc_Variable(names)
        self._variable: Final[_Tkc_Variable] = uv

        # キャッシュ
        self._lastPos: Vector2 = Vector2()
        self._diffPos: Vector2 = Vector2()

        self._lastVarDict: Final[Dict[str, tk.Variable]] = {}

    def __str__(self) -> str:
        ret = ""
        for p in reversed(self._parent):
            ret += f"Frame({p}):"
        return classControl.formatOrthop(f"{ret}Frame({self._name}):Widgets", f"cou:{len(self._list)}")

    def __len__(self) -> int:
        return len(self._list)

    def _packOrPlace(
            self, wid: tk.Widget,
            side: ta_side, fill: ta_fill,
            pos: ta_pos, diffPos: ta_opPos,
            rc: Tuple[ta_opInt, ta_opInt, int, int, str], pad: Tuple[int, int, int, int],
            *args, **kwargs) -> None:
        """
        packとplace、gridを自動振り分け
        """
        if diffPos is not None:
            if diffPos == True:
                diffPos = self._diffPos
            else:
                diffPos = Vector2.convert(diffPos)
                self._diffPos = diffPos
            pos = self._lastPos.copy()
            pos += diffPos

        if rc[0] is not None and rc[1] is not None:
            wid.grid(
                row=rc[0], column=rc[1],
                rowspan=rc[2], columnspan=rc[3],
                sticky=rc[4],
                padx=pad[0], pady=pad[1], ipadx=pad[2], ipady=pad[3],
                *args, **kwargs)
        elif pos is None:
            wid.pack(
                side=side, fill=fill,
                padx=pad[0], pady=pad[1], ipadx=pad[2], ipady=pad[3],
                *args, **kwargs)
        else:
            pos = Vector2.convert(pos)
            self._lastPos = pos.copy()
            wid.place(x=pos.x, y=pos.y, *args, **kwargs)

    def _setName(self, name: str) -> None:
        """
        名前を設定する
        """
        if name is None or name == "":
            return
        if name in self._nameIndDict:
            raise ValueError(f"既に同名のウェジット「{name}」が存在します")

        self._nameIndDict[name] = len(self._list)

    def bind(self, name: str, event: str, func: Callable[..., Any], add: bool = False) -> None:
        """
        ウェジットにイベントをつける
        """
        if name not in self._nameIndDict:
            raise ValueError(f"ウェジット「{name}」は存在しません")
        self._list[self._nameIndDict[name]].bind(event, func, add=add)

    def bind_all(self, event: str, func: Callable[..., Any], add: bool = False) -> None:
        """
        すべてのウェジットにイベントをつける
        """
        for wid in self._list:
            wid.bind(event, func, add=add)

    @overload
    def addLabel(
            self, text: str, anchor: ta_anchor = "nw", justify: ta_justify = "left",
            image: ta_cusImageTk = None, *,
            type: Literal["tk"] = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", **kwargs) -> tk.Label:
        pass

    @overload
    def addLabel(
            self, text: str, anchor: ta_anchor = "nw", justify: ta_justify = "left",
            image: ta_cusImageTk = None, *,
            type: Literal["ttk"] = "ttk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            eow: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", style: str = "", **kwargs) -> ttk.Label:
        pass

    def addLabel(
            self, text: str, anchor: ta_anchor = "nw", justify: ta_justify = "left",
            image: ta_cusImageTk = None, *,
            type: ta_tkttk = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", style: str = "", **kwargs) -> Any:
        """
        ラベルを追加する
        """
        sv = self._setAutoVariable("__Label", name, text)
        if type == "ttk" or style != "":
            wid = ttk.Label(self._frame, name=name, style=style, **kwargs)
        else:
            wid = tk.Label(self._frame, name=name, **kwargs)
        if image is not None:
            wid["image"] = self._base._photos.getImageTk(image)
        wid["textvariable"] = sv
        wid["anchor"] = anchor
        wid["justify"] = justify
        wid["font"] = self.getFont(font)

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    @overload
    def addButton(
            self, text: str,
            image: ta_cusImageTk = None, *,
            type: Literal["tk"] = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_btn_state = "normal", font: ta_cusFont = "",
            com: ta_com = None, isReturn: bool = True, **kwargs) -> tk.Button:
        pass

    @overload
    def addButton(
            self, text: str,
            image: ta_cusImageTk = None, *,
            type: Literal["ttk"] = "ttk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_btn_state = "normal", font: ta_cusFont = "", style: str = "",
            com: ta_com = None, isReturn: bool = True, **kwargs) -> ttk.Button:
        pass

    def addButton(
            self, text: str,
            image: ta_cusImageTk = None, *,
            type: ta_tkttk = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_btn_state = "normal", font: ta_cusFont = "", style: str = "",
            com: ta_com = None, isReturn: bool = True, **kwargs) -> Any:
        """
        ボタンを追加する
        """
        sv = self._setAutoVariable("__Button", name, text)
        if type == "ttk" or style != "":
            wid = ttk.Button(self._frame, name=name, style=style, **kwargs)
        else:
            wid = tk.Button(self._frame, name=name, **kwargs)
        if image is not None:
            wid["image"] = self._base._photos.getImageTk(image)
        wid["textvariable"] = sv
        wid["takefocus"] = takefocus
        wid["state"] = state
        wid["font"] = self.getFont(font)
        wid["command"] = com

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        if isReturn:
            if com is not None:
                if com.__code__.co_argcount == 0:
                    wid.bind("<Return>", lambda e: com())
                else:
                    wid.bind("<Return>", com)
        wid.bind("<Up>", self.focusPrev)
        wid.bind("<Down>", self.focusNext)
        wid.bind("<Button-1>", self._clickFocus)
        return wid

    @overload
    def addEntry(
            self, text: str = "", *,
            type: Literal["tk"] = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_inp_state = "normal", font: ta_cusFont = "", **kwargs) -> tk.Entry:
        pass

    @overload
    def addEntry(
            self, text: str = "", *,
            type: Literal["ttk"] = "ttk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_inp_state = "normal", font: ta_cusFont = "", style: str = "", **kwargs) -> ttk.Entry:
        pass

    def addEntry(
            self, text: str = "", *,
            type: ta_tkttk = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_inp_state = "normal", font: ta_cusFont = "", style: str = "", **kwargs) -> Any:
        """
        入力欄を追加する
        """
        sv = self._setAutoVariable("__Entry", name, text)
        if type == "ttk" or style != "":
            wid = ttk.Entry(self._frame, name=name, style=style, **kwargs)
        else:
            wid = tk.Entry(self._frame, name=name, **kwargs)
        wid["textvariable"] = sv
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)
        wid["state"] = state

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        wid.bind("<Return>", self.focusNext)
        wid.bind("<Shift-Return>", self.focusPrev)
        wid.bind("<Up>", self.focusPrev)
        wid.bind("<Down>", self.focusNext)
        wid.bind("<Button-1>", self._clickFocus)
        return wid

    def addPlaceholderEntry(
            self, text: str = "", placeholder: str = "", *,
            name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, font: ta_cusFont = "", **kwargs) -> "_PlaceholderEntry":
        """
        入力欄を追加する
        (プレースホルダ付き)
        """
        sv = self._setAutoVariable("__Placeholder", name, text)
        wid = _PlaceholderEntry(
            self._frame, name=name, textvariable=sv, placeholder=placeholder, **kwargs
        )
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        wid.bind("<Return>", self.focusNext)
        wid.bind("<Shift-Return>", self.focusPrev)
        wid.bind("<Up>", self.focusPrev)
        wid.bind("<Down>", self.focusNext)
        wid.bind("<Button-1>", self._clickFocus)
        return wid

    def addListbox(
            self, list_: List[str] = [], selectmode: ta_lb_select = "browse", activestyle: ta_lb_activestyle = "underline", *,
            name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_btn_state = "normal", font: ta_cusFont = "", **kwargs) -> tk.Listbox:
        """
        リストボックスを追加する
        """
        sv = self._setAutoVariable("__Listbox", name, list_)
        wid = tk.Listbox(self._frame, name=name, **kwargs)
        wid["listvariable"] = sv
        wid["selectmode"] = selectmode
        wid["activestyle"] = activestyle
        wid["takefocus"] = takefocus
        wid["state"] = state
        wid["font"] = self.getFont(font)

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    def addTreeview(
            self, dict_: Optional[Dict[str, Any]] = None,
            columns: List[Union[str, int]] = [], displaycolumns: Optional[List[str]] = None, headings: List[str] = [],
            show: ta_tr_show = ["tree", "headings"], selectmode: ta_lb_select = "browse", allOpen: bool = False, *,
            name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, style: str = "",
            **kwargs) -> ttk.Treeview:
        """
        ツリービューを追加する
        (テーブルでもある)
        """

        wid = ttk.Treeview(self._frame, name=name, style=style, **kwargs)
        wid["show"] = show
        if len(columns) > 0:
            wid["columns"] = columns
        if displaycolumns is not None:
            wid["displaycolumns"] = displaycolumns
        wid["selectmode"] = selectmode

        if len(headings) > 0:
            if "headings" in show:
                for i, c in enumerate(["#0"] + columns):
                    wid.heading(str(c), text=headings[i])

        if dict_ is not None:
            self._searchTreeDict(wid, "", dict_, allOpen)

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    def _searchTreeDict(self, tree: ttk.Treeview, par: str = "", dic: Optional[Union[Dict[str, Any], List[Any]]] = None, allOpen: bool = False, nowPath: str = "") -> None:
        """
        ツリービューの中身を設定する
        """
        isOpen = False
        nowPath += "/"
        if isinstance(dic, dict):
            for k, v in dic.items():
                openFlag = allOpen
                if k == "_isOpen":
                    continue
                if isinstance(v, dict):
                    if "_isOpen" in v and v["_isOpen"]:
                        isOpen = True
                        openFlag = openFlag or isOpen
                elif isinstance(v, list):
                    if "_isOpen" in v:
                        isOpen = True
                        openFlag = openFlag or isOpen
                ch = tree.insert(
                    par, "end", text=k,
                    open=openFlag, tags=["parent", nowPath + k + "/"]
                )
                self._searchTreeDict(
                    tree, ch, v, allOpen=allOpen, nowPath=nowPath + k
                )
        elif isinstance(dic, list):
            for v in dic:
                if v == "_isOpen":
                    continue
                tree.insert(par, "end", text=v, tags=["child", nowPath + v])
        elif dic is None:
            pass
        else:
            raise ValueError("対応していない型です")

    @overload
    def addCheckbutton(
            self, text: str, varName: Union[str, Literal[True]] = "", value: bool = False,
            image: ta_cusImageTk = None, *,
            type: Literal["tk"] = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, font: ta_cusFont = "",
            com: ta_com = None, **kwargs) -> tk.Checkbutton:
        pass

    @overload
    def addCheckbutton(
            self, text: str, varName: Union[str, Literal[True]] = "", value: bool = False,
            image: ta_cusImageTk = None, *,
            type: Literal["ttk"] = "ttk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> ttk.Checkbutton:
        pass

    def addCheckbutton(
            self, text: str, varName: Union[str, Literal[True]] = "", value: bool = False,
            image: ta_cusImageTk = None, *,
            type: ta_tkttk = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> Any:
        """
        チェックボタンを追加する
        """
        sv = None
        if varName == True:
            if self._lastVarDict["checkbutton"] is not None:
                sv = self._lastVarDict["checkbutton"]
            varName = ""

        if sv is None:
            if varName == "":
                sv = self._setAutoVariable("__Checkbutton", name, value)
            else:
                if not self._variable.isVariable(varName):
                    self._variable.setBool(varName, value)
                sv = self._variable.getVariable(varName)
            self._lastVarDict["checkbutton"] = sv
        vn = self._variable.getVariableName(sv)
        if vn is None:
            vn = varName

        if type == "ttk" or style != "":
            wid = ttk.Checkbutton(
                self._frame, name=name,
                style=style, **kwargs
            )
        else:
            wid = tk.Checkbutton(self._frame, name=name, **kwargs)
        if image is not None:
            wid["image"] = self._base._photos.getImageTk(image)
        wid["text"] = text
        wid["variable"] = sv
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)
        wid["command"] = com

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        wid.bind("<Return>", lambda e: self._variable.toggleBool(vn))
        wid.bind("<Up>", self.focusPrev)
        wid.bind("<Down>", self.focusNext)
        wid.bind("<Button-1>", self._clickFocus)
        return wid

    @overload
    def addRadiobutton(
            self, text: str, value: Union[int, float, str], varName: Union[str, Literal[True]] = "",
            image: ta_cusImageTk = None, *,
            type: Literal["tk"] = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, font: ta_cusFont = "",
            com: ta_com = None, **kwargs) -> tk.Radiobutton:
        pass

    @overload
    def addRadiobutton(
            self, text: str, value: Union[int, float, str], varName: Union[str, Literal[True]] = "",
            image: ta_cusImageTk = None, *,
            type: Literal["ttk"] = "ttk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> ttk.Radiobutton:
        pass

    def addRadiobutton(
            self, text: str, value: Union[int, float, str], varName: Union[str, Literal[True]] = "",
            image: ta_cusImageTk = None, *,
            type: ta_tkttk = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> Any:
        """
        ラジオボタンを追加する
        """
        sv = None
        if varName == True:
            if self._lastVarDict["radiobutton"] is not None:
                sv = self._lastVarDict["radiobutton"]
            varName = ""

        if sv is None:
            if varName == "":
                sv = self._setAutoVariable(
                    "__Radiobutton", name, value  # type: ignore
                )
            else:
                if not self._variable.isVariable(varName):
                    self._variable.setAuto(varName, value)  # type: ignore
                sv = self._variable.getVariable(varName)
            self._lastVarDict["radiobutton"] = sv
        vn = self._variable.getVariableName(sv)
        if vn is None:
            vn = varName

        if type == "ttk" or style != "":
            wid = ttk.Radiobutton(
                self._frame, name=name,
                style=style, **kwargs
            )
        else:
            wid = tk.Radiobutton(self._frame, name=name, **kwargs)
        if image is not None:
            wid["image"] = self._base._photos.getImageTk(image)
        wid["text"] = text
        wid["value"] = value
        wid["variable"] = sv
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)
        wid["command"] = com

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        wid.bind("<Return>", lambda e: self._variable.updateValue(
            vn, value))  # type: ignore
        wid.bind("<Up>", self.focusPrev)
        wid.bind("<Down>", self.focusNext)
        wid.bind("<Button-1>", self._clickFocus)
        return wid

    @overload
    def addScale(
            self, value: float = 0,
            from_: int = 0, to: int = 100, orient: ta_sc_orient = "vertical", *,
            type: Literal["tk"] = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "",
            com: ta_com = None, **kwargs) -> tk.Scale:
        pass

    @overload
    def addScale(
            self, value: float = 0,
            from_: int = 0, to: int = 100, orient: ta_sc_orient = "vertical", *,
            type: Literal["ttk"] = "ttk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> ttk.Scale:
        pass

    def addScale(
            self, value: float = 0,
            from_: int = 0, to: int = 100, orient: ta_sc_orient = "vertical", *,
            type: ta_tkttk = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> Any:
        """
        スケールボタンを追加する
        (スライドバー)
        """

        sv = self._setAutoVariable("__Scale", name, value)

        if type == "ttk" or style != "":
            wid = ttk.Scale(self._frame, name=name, style=style, **kwargs)
        else:
            wid = tk.Scale(self._frame, name=name, **kwargs)
        wid["from_"] = from_
        wid["to"] = to
        wid["variable"] = sv
        wid["orient"] = orient
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)
        wid["command"] = com

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    @overload
    def addScrollbar(
            self, target: Union[str, int] = "", orient: ta_sc_orient = "vertical", *,
            type: Literal["tk"] = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "",
            com: ta_com = None, **kwargs) -> tk.Scrollbar:
        pass

    @overload
    def addScrollbar(
            self, target: Union[str, int] = "", orient: ta_sc_orient = "vertical", *,
            type: Literal["ttk"] = "ttk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> ttk.Scrollbar:
        pass

    def addScrollbar(
            self, target: Union[str, int] = "", orient: ta_sc_orient = "vertical", *,
            type: ta_tkttk = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> Any:
        """
        スクロールバーを追加する
        """
        w = None
        if target != "":
            w = self.getWidget(target)
            if w is not None:
                w = cast(tk.Listbox, w)

        if type == "ttk" or style != "":
            wid = ttk.Scrollbar(self._frame, name=name, style=style, **kwargs)
        else:
            wid = tk.Scrollbar(self._frame, name=name, **kwargs)
        if w is None:
            wid["command"] = com
        else:
            if orient == "horizontal":
                wid["command"] = w.xview
                w["xscrollcommand"] = wid.set
            else:
                wid["command"] = w.yview
                w["yscrollcommand"] = wid.set
        wid["orient"] = orient
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    def addMessage(
            self, text: str, *,
            name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", **kwargs) -> tk.Message:
        """
        メッセージを追加する
        (複数行のlabelのようなもの)
        """
        wid = tk.Message(self._frame, name=name, **kwargs)
        wid["text"] = text
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    def addCombobox(
            self, *,
            name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, font: ta_cusFont = "", style: str = "", **kwargs) -> ttk.Combobox:
        """
        コンボボックスを追加する
        """
        wid = ttk.Combobox(self._frame, name=name, style=style, **kwargs)
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    def addProgressbar(
            self, mode: ta_pro_mode = "determinate", value: float = 0.0, varName: str = "", maximum: float = 100, *,
            name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, font: ta_cusFont = "", style: str = "", **kwargs) -> ttk.Progressbar:
        """
        プログレスバーを追加する
        """
        wid = ttk.Progressbar(self._frame, name=name, style=style, **kwargs)
        wid["mode"] = mode
        wid["maximum"] = maximum
        wid["takefocus"] = takefocus
        wid["font"] = self.getFont(font)

        if mode == "determinate":
            sv = None
            if varName == "":
                sv = self._setAutoVariable("__Progressbar", name, value)
            else:
                if not self._variable.isVariable(varName):
                    self._variable.setAuto(varName, value)
                sv = self._variable.getVariable(varName)
            wid["variable"] = sv

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    @overload
    def addSpinbox(
            self, value: float = 0, format_="%.0f", from_: float = 0, increment: float = 1, to: float = 1e10, *,
            type: Literal["tk"] = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_inp_state = "normal", font: ta_cusFont = "", com: ta_com = None, **kwargs) -> tk.Spinbox:
        pass

    @overload
    def addSpinbox(
            self, value: float = 0, format_="%.0f", from_: float = 0, increment: float = 1, to: float = 1e10, *,
            type: Literal["ttk"] = "ttk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_inp_state = "normal", font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> ttk.Spinbox:
        pass

    def addSpinbox(
            self, value: float = 0, format_="%.0f", from_: float = 0, increment: float = 1, to: float = 1e10, *,
            type: ta_tkttk = "tk", name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_inp_state = "normal", font: ta_cusFont = "", style: str = "",
            com: ta_com = None, **kwargs) -> Any:
        """
        入力欄(数値のみ)を追加する
        """
        sv = self._setAutoVariable("__Spinbox", name, value)

        if type == "ttk" or style != "":
            wid = ttk.Spinbox(self._frame, name=name, style=style, **kwargs)
        else:
            wid = tk.Spinbox(self._frame, name=name, **kwargs)
        wid["format"] = format_
        wid["textvariable"] = sv
        wid["from_"] = from_
        wid["to"] = to
        wid["increment"] = increment
        wid["takefocus"] = takefocus
        wid["state"] = state
        wid["font"] = self.getFont(font)
        wid["command"] = com

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        wid.bind("<Return>", self.focusNext)
        wid.bind("<Shift-Return>", self.focusPrev)
        wid.bind("<Button-1>", self._clickFocus)
        return wid

    def addText(
            self, wrap: ta_wrap = "none", undo: bool = True, maxundo: int = 0, *,
            name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = True, state: ta_inp_state = "normal", font: ta_cusFont = "", **kwargs) -> tk.Text:
        """
        テキストエディタを追加する
        """
        wid = tk.Text(self._frame, name=name, **kwargs)
        wid["wrap"] = wrap
        wid["undo"] = undo
        wid["maxundo"] = maxundo
        wid["takefocus"] = takefocus
        wid["state"] = state
        wid["font"] = self.getFont(font)

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return wid

    def addCanvas(
            self, *,
            name: str = "",
            side: ta_side = "top", fill: ta_fill = "none",
            pos: ta_pos = None, diffPos: ta_opPos = None,
            row: ta_opInt = None, column: ta_opInt = None, rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            takefocus: bool = False, state: ta_inp_state = "normal", **kwargs) -> _Tkc_Canvas:
        """
        キャンバスを追加する
        """
        wid = tk.Canvas(self._frame, name=name, **kwargs)
        wid["takefocus"] = takefocus
        wid["state"] = state

        self._packOrPlace(
            wid, side, fill,
            pos, diffPos,
            (row, column, rowspan, columnspan, sticky),
            (padx, pady, ipadx, ipady)
        )
        self._setName(name)
        self._list.append(wid)
        self._setFirstFocus(wid, takefocus)
        return _Tkc_Canvas(self._base, wid)

    def getLength(self) -> int:
        """
        フレーム上の要素数を返却する
        """
        return len(self._list)

    def getWidget(self, key: Union[str, int]) -> Optional[tk.Widget]:
        """
        フレーム上の要素を返却する

        int : 登録順のid(通し番号)[-も可]

        str : 登録時の名前
        """
        if isinstance(key, int):
            l = len(self._list)
            if -l <= key < l:
                return self._list[key]
            return None
        if key in self._nameIndDict:
            return self._list[self._nameIndDict[key]]
        return None

    def getIndex(self, widget: tk.Widget) -> int:
        """
        widgetのindexを返却する
        """
        return listFind(self._list, widget)

    def getName(self, widget: tk.Widget) -> Optional[str]:
        """
        widgetの名前を返却する
        """
        it = self._nameIndDict.items()
        for k, v in it:
            if v == widget:
                return k
        return None

    def getValue(self, name: str) -> Optional[ta_val]:
        """
        変数の値を取得

        (tkc.variable.getValue()を使用する事を推奨)
        """
        wid = self.getWidget(name)
        if wid is None:
            return None
        if hasattr(wid, "get"):
            return cast(tk.Entry, wid).get()
        return None

    def getFont(self, font: ta_cusFont) -> Optional[font.Font]:
        """
        フォントを取得
        """
        if isinstance(font, str):
            if font in self._base.fontDict:
                return self._base.fontDict[font]
            return None
        return font

    def _setFirstFocus(self, wid: Optional[tk.Widget] = None, takefocus: bool = False) -> None:
        """
        最初のwidgetをフォーカスする
        (システム管理用)
        """
        if wid is None:
            if self._firstFocus is not None:
                self._firstFocus.focus_set()
            return

        if self._firstFocus is None:
            if takefocus:
                if self._base.isDrawStart:
                    wid.focus_set()
                self._firstFocus = wid
        self._focusList.append({
            "widget": wid,
            "takefocus": takefocus
        })

    def isFocus(self, wid: tk.Widget) -> bool:
        """
        widgetがフォーカス可能かを返却する
        """
        for f in self._focusList:
            if f["widget"] == wid:
                return f["takefocus"]
        return False

    def getFocusIndex(self, wid: tk.Widget) -> int:
        """
        widgetのindexを返却する
        """
        cou = -1
        for f in self._focusList:
            if f["takefocus"]:
                cou += 1
                if f["widget"] == wid:
                    return cou
        return -1

    def getFocusLength(self) -> int:
        """
        フォーカス可能なwidgetの数を返却する
        """
        cou = 0
        for f in self._focusList:
            if f["takefocus"]:
                cou += 1
        return cou

    def getFocusWidget(self, ind: int = -1) -> Optional[tk.Widget]:
        """
        現在フォーカスされているwidgetを返却する

        引数が存在する場合は引数のindexのwidgetを返却する
        (-は不可,+は溢れ可)
        """
        if len(self._focusList) <= 0:
            return None

        if ind >= 0:
            fl = self.getFocusLength()
            if ind >= fl:
                ind %= fl
            cou = -1
            for f in self._focusList:
                if f["takefocus"]:
                    cou += 1
                    if cou == ind:
                        return f["widget"]
            return None

        f = cast(tk.Widget, self._focusList[0]["widget"]).focus_get()
        if f is None:
            return None
        f = str(f)
        for fl in self._focusList:
            if f == str(fl["widget"]):
                return fl["widget"]
        return None

    def moveFocus(self, add: int) -> bool:
        """
        現在の位置から差分の位置のwidgetをフォーカスする
        """
        if add == 0:
            return True
        wid = self.getFocusWidget()
        if wid is None:
            ind = 0
        else:
            ind = self.getFocusIndex(wid)
            if ind == -1:
                # フォーカス不可のウェジットにフォーカスしている場合
                self._setFirstFocus()
                return False
        diff = ind + add
        fl = self.getFocusLength()
        t = False
        if diff < 0:
            t = self._traversalFrameFocus(-1)
        elif diff >= fl:
            t = self._traversalFrameFocus(1)

        if t:
            return True

        if diff < 0:
            diff = fl + (diff % fl)

        diff %= fl
        f = self.getFocusWidget(diff)
        if f is not None:
            f.focus_set()
            return True
        return False

    def focusNext(self, event: Optional[tk.Event] = None) -> bool:
        """
        次のwidgetをフォーカスする
        """
        return self.moveFocus(1)

    def focusPrev(self, event: Optional[tk.Event] = None) -> bool:
        """
        前のwidgetをフォーカスする
        """
        return self.moveFocus(-1)

    def _clickFocus(self, event: tk.Event) -> None:
        event.widget.focus_set()

    def _traversalFrameFocus(self, add: Literal[1, -1]) -> bool:
        """
        同じ名前空間の別フレームにフォーカスする
        """
        if self._tabTraversal is None:
            return False

        cl: List[str] = [self._tabTraversal] + self._base._frames.getChildList(
            self._tabTraversal, True
        )

        useName = ""
        if len(cl) <= 0:
            useName = self._name
        else:
            tl = []
            for fs in cl:
                if fs == self._name:
                    tl.append(fs)
                elif self._base.wholeData[fs].tabTraversal == self._tabTraversal:
                    if self._base.wholeData[fs].widgets.getFocusLength() > 0:
                        tl.append(fs)

            if len(tl) <= 0:
                useName = self._name
            else:
                endF = False
                for fs in tl:
                    if fs == self._name:
                        if add == -1:
                            break
                        useName = ""
                        endF = True
                        continue
                    useName = fs
                    if endF:
                        break

            if useName == "":
                if add == 1:
                    useName = tl[0]
                else:
                    useName = tl[-1]

        w: _Tkc_Widgets = self._base.wholeData[useName].widgets
        if add == 1:
            if w._firstFocus is not None:
                w._firstFocus.focus_set()
                return True
        else:
            fl = w.getFocusLength()
            f = w.getFocusWidget(fl - 1)
            if f is not None:
                f.focus_set()
                return True

        return False

    def _setAutoVariable(self, baseName: str, name: str, val: ta_type) -> tk.Variable:
        svn = ""
        if name != "":
            if self._variable.isVariable(name):
                name = ""
            else:
                svn = name
        if name == "":
            svn = self._variable.setSerialAutoNumber(baseName, val)
        else:
            self._variable.setAuto(name, val)

        return self._variable.getVariable(svn)


class _PlaceholderEntry(ttk.Entry):
    def __init__(self, container, textvariable: tk.Variable, placeholder="", *args, style: str = "", **kwargs) -> None:
        super().__init__(container, *args, style="Placeholder.TEntry", **kwargs)
        self.placeholder = placeholder

        self.insert("0", self.placeholder)
        if textvariable.get() != "":
            self.delete("0", "end")
            self["style"] = "TEntry"
            self.insert("0", textvariable.get())
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e) -> None:
        if self["style"] == "Placeholder.TEntry":
            self.delete("0", "end")
            self["style"] = "TEntry"

    def _add_placeholder(self, e) -> None:
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = "Placeholder.TEntry"
