# coding: utf-8
"""
tkinterを簡単に操作出来るようにしたやつ
(本体)
"""

from typing import Any, Dict, List, Tuple, Callable, Literal, Union, Optional, ClassVar, Type, cast, Final, final, overload
import platform
import ctypes

from .widgets import _Tkc_Widgets, classControl, _Tkc_Canvas, tk, ttk, font, Vector2, ta_pos
from .variable import _Tkc_Variable
from .photo import _Tkc_Photo
from .messagebox import _Tkc_Messagebox

# type aliases
ta_opStr = Optional[str]
ta_opInt = Optional[int]

ta_poss = Tuple[Union[int, Literal["max"]], Union[int, Literal["max"]]]

ta_establishment = Literal["pack", "grid", "place"]

ta_anchor = Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"]
ta_fill = Literal["none", "x", "y", "both"]
ta_side = Literal["top", "bottom", "left", "right"]

ta_font = Union[
    Tuple[str, int],
    Tuple[str, int, str],
    Tuple[str, int, str, str]
]
ta_ft_weight = Literal["normal", "bold"]
ta_ft_slant = Literal["roman", "italic"]
ta_relief = Literal["flat", "raised", "sunken", "ridge", "solid", "groove"]

# ここまで


class Tkc:
    """
    tkinterControl (本体)
    """

    tk = tk
    ttk = ttk
    Tkc_Canvas: ClassVar[Type[_Tkc_Canvas]] = _Tkc_Canvas

    def __init__(
            self, title: str = "",
            windowSize: ta_poss = (200, 200),
            windowPos: Optional[ta_poss] = None,
            resizable: Optional[Tuple[bool, bool]] = None,
            *,
            minSize: Optional[Tuple[int, int]] = None,
            maxSize: Optional[Tuple[int, int]] = None) -> None:

        self._base = _Tkc_Base()
        self._base.root.title(title)
        self._windowSizeStr = ""

        self.winMaxX = self._base.root.winfo_screenwidth()-10
        self.winMaxY = self._base.root.winfo_screenheight()-30

        # maxの場合画面サイズを当てはめる
        windowSize = self._maxSizeSet(windowSize)

        if windowPos is None:
            self._windowSizeStr = f"{windowSize[0]}x{windowSize[1]}"
        else:
            if windowPos[0] == "max":
                windowPos = (self.winMaxX-windowSize[0], windowPos[1])
            if windowPos[1] == "max":
                windowPos = (windowPos[0], self.winMaxY-windowSize[1])
            self._windowSizeStr = f"{windowSize[0]}x{windowSize[1]}+{windowPos[0]}+{windowPos[1]}"

        self._base.root.geometry(self._windowSizeStr)

        if minSize is not None:
            minSize = self._maxSizeSet(minSize)
            self._base.root.wm_minsize(width=minSize[0], height=minSize[1])
        if maxSize is not None:
            maxSize = self._maxSizeSet(maxSize)
            self._base.root.wm_maxsize(width=maxSize[0], height=maxSize[1])

        if resizable is None:
            resizable = (True, True)
        self._base.root.resizable(*resizable)
        self._base.root.protocol("WM_DELETE_WINDOW", self.drawEnd)

        # 拡張ウェジット設定
        self._style = ttk.Style(self._base.root)
        self._style.configure("Placeholder.TEntry", foreground="#959595")
        # ここまで

        # windowが生きているか
        self._alive = True

        self.frames: Final[_Tkc_Frames] = self._base._frames
        self.frames._currentChangeEventSetter(self._currentChangeEvent)
        self.widgets: _Tkc_Widgets
        self.variable: _Tkc_Variable
        self.messagebox: Final[_Tkc_Messagebox] = _Tkc_Messagebox()

        # 一応初期値(下地)を設定
        try:
            self.frames.add("_base")
        except Exception:
            print("初期値フレーム_baseの作成に失敗しました")

    def __str__(self) -> str:
        return classControl.formatOrthop(f"Tkc", self._windowSizeStr)

    def windowDpiAutoSet(self) -> bool:
        """
        文字等がぼやける場合に実行

        ※fullscreenのサイズが正常に実行されない場合あり
        """
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
            return True
        except:
            pass
        return False

    def drawStart(self) -> None:
        """
        描画開始
        (mainloop)
        """
        if self._alive:
            self._base.isDrawStart = True
            self.widgets._setFirstFocus()
            self._base.root.mainloop()

    def drawEnd(self, event: Optional[tk.Event] = None) -> None:
        """
        描画終了
        (window削除)
        """
        if self._alive:
            self._base.root.destroy()
            self._base.root.quit()

    def attributes(self, option: str, value: Any) -> None:
        """
        tkinterウィンドウ設定
        """
        self._base.root.attributes(option, value)

    def fullscreen(self, flag: bool = True) -> None:
        self.attributes("-fullscreen", flag)

    def maximize(self, flag: bool = True) -> None:
        self._base.root.state(flag and "zoomed" or "normal")

    def minimized(self, flag: bool = True) -> None:
        if flag:
            self._base.root.iconify()
        else:
            self._base.root.deiconify()

    def bind(self, event: str, func: Callable[..., Any], add: bool = True) -> None:
        self._base.root.bind(event, func, add)

    def bind_all(self, event: str, func: Callable[..., Any], add: bool = True) -> None:
        self._base.root.bind_all(event, func, add)

    def after(self, ms: Union[int, Literal["idle"]], func: Callable[..., Any], *args) -> None:
        self._base.root.after(ms, func, *args)

    def createFont(self, name: str, family: str, size: int, weight: ta_ft_weight = "normal", slant: ta_ft_slant = "roman", underline: bool = False, overstrike: bool = False, **kwargs) -> font.Font:
        if name in self._base.fontDict:
            raise ValueError(f"フォント設定「{name}」はすでに存在します")

        f = font.Font(name=name, family=family, size=size, weight=weight,
                      slant=slant, underline=underline, overstrike=overstrike, **kwargs)

        self._base.fontDict[name] = f
        return f

    def getFont(self, name: str) -> Optional[font.Font]:
        if name not in self._base.fontDict:
            return None
        return self._base.fontDict[name]

    def createStyle(
        self, name: str,
        font: Optional[ta_font] = None,
        fg: ta_opStr = None, bg: ta_opStr = None,
        bordercolor: ta_opStr = None, troughcolor: ta_opStr = None,
        darkcolor: ta_opStr = None, lightcolor: ta_opStr = None,
        padding: Optional[Tuple[float, ...]] = None,
        borderwidth: Optional[int] = None,
        relief: Optional[ta_relief] = None,
        rowheight: Optional[int] = None,
        **kwargs
    ) -> ttk.Style:
        styleDict: Dict[str, Any] = kwargs.copy()
        self._addDict(styleDict, "font", font)
        self._addDict(styleDict, "foreground", fg)
        self._addDict(styleDict, "background", bg)
        self._addDict(styleDict, "bordercolor", bordercolor)
        self._addDict(styleDict, "troughcolor", troughcolor)
        self._addDict(styleDict, "darkcolor", darkcolor)
        self._addDict(styleDict, "lightcolor", lightcolor)
        self._addDict(styleDict, "padding", padding)
        self._addDict(styleDict, "borderwidth", borderwidth)
        self._addDict(styleDict, "relief", relief)
        self._addDict(styleDict, "rowheight", rowheight)

        style = ttk.Style(self._base.root)
        style.configure(name, **styleDict)

        return style

    def useTheme(self, name: str) -> bool:
        style = ttk.Style(self._base.root)
        if name in style.theme_names():
            style.theme_use(name)
            return True
        return False

    def getThemeList(self) -> Tuple[str, ...]:
        style = ttk.Style(self._base.root)
        return style.theme_names()

    def msgErr(self, text: str, title: str) -> None:
        self.messagebox.show("error", text, title)

    @staticmethod
    def _addDict(dict_: Dict, key: str, value: Any) -> None:
        if value is None:
            return
        dict_[key] = value

    def _currentChangeEvent(self, name: str) -> None:
        self.widgets = self._base.wholeData[name].widgets
        if len(self.widgets._list) > 0:
            if self._base.isDrawStart:
                self.widgets._setFirstFocus()
        self.variable = self.widgets._variable

    def _maxSizeSet(self, tup: ta_poss) -> Tuple[int, int]:
        if tup[0] == "max":
            tup = (self.winMaxX, tup[1])
        if tup[1] == "max":
            tup = (tup[0], self.winMaxY)
        return cast(Tuple[int, int], tup)

    @final
    @property
    def root(self) -> tk.Tk:
        """
        tkinterのルートウェジット
        """
        return self._base.root

    @final
    @property
    def image(self) -> _Tkc_Photo:
        """
        PILのImage管理
        """
        return self._base._photos

    @final
    @property
    def systemName(self) -> str:
        """
        端末名
        """
        return self._base.systemName

    @property
    def fra(self) -> "_Tkc_Frames":
        """
        tkc.framesの短縮表記
        """
        return self.frames

    @property
    def wid(self) -> _Tkc_Widgets:
        """
        tkc.widgetsの短縮表記
        """
        return self.widgets

    @property
    def var(self) -> _Tkc_Variable:
        """
        tkc.variableの短縮表記
        """
        return self.variable

    @property
    def msgbox(self) -> _Tkc_Messagebox:
        """
        tkc.messageboxの短縮表記
        """
        return self.messagebox

    @property
    def img(self) -> _Tkc_Photo:
        """
        tkc.imageの短縮表記
        """
        return self._base._photos


class _Tkc_Base:
    """
    全体管理クラス
    """

    def __init__(self) -> None:
        self.root: Final[tk.Tk] = tk.Tk()

        self._frames: Final[_Tkc_Frames] = _Tkc_Frames(self)

        self._photos: Final[_Tkc_Photo] = _Tkc_Photo()

        self.wholeData: Final[Dict[str, "_Tkc_Data"]] = {}

        self.fontDict: Final[Dict[str, font.Font]] = {}

        self.systemName: Final[str] = platform.system()

        # 描画開始したか
        self.isDrawStart: bool = False


class _Tkc_Data:
    """
    データ管理クラス
    (json方式管理用)
    """

    def __init__(
            self, _base: _Tkc_Base, frame: tk.Frame, name: str, *,
            establishment: ta_establishment = "pack", establishData: Dict[str, Any] = {},
            parent: Optional[List[str]] = None,
            tabTraversal: str = "", useParentVariable: str = "") -> None:
        # フレーム設定
        self.frame: Final[tk.Frame] = frame

        self._establishment = establishment
        self._establishData = establishData

        # 親子関係設定
        par = None
        if parent is not None:
            par = parent[0]
            parent = [name] + parent
        else:
            parent = [name]
        self.parent: Final[Optional[str]] = par

        # 使用タブ連続 空間
        tt = name
        if tabTraversal != "":
            tt = tabTraversal
        self.tabTraversal: Final[str] = tt

        # 使用変数名前空間
        upv = name
        if useParentVariable != "":
            upv = useParentVariable
        self.useVariable: Final[str] = upv

        # ウェジット関係
        uv = None
        if name != upv:
            uv = _base.wholeData[upv].widgets._variable
        self.widgets: Final[_Tkc_Widgets] = _Tkc_Widgets(
            _base, self.frame, parent,
            tabTraversal=tt,
            useVariable=uv,
        )


class _Tkc_Frames:
    """
    フレーム管理クラス
    """

    def __init__(self, _base: _Tkc_Base) -> None:
        self._base = _base

        self._currentBaseFrame: Optional[tk.Frame] = None
        self._currentBaseFrameName: Optional[str] = None

        self._currentFrame: Optional[tk.Frame] = None
        self._currentFrameName: Optional[str] = None

    def __str__(self) -> str:
        return classControl.formatOrthop(f"Frames", f"cou:{len(self._base.wholeData)}")

    def __len__(self) -> int:
        return len(self._base.wholeData)

    def _currentChangeEventSetter(self, func: Callable[[str], None]) -> None:
        self._currentChange = func

    def _currentChangeEvent(self, name: str) -> None:
        p = self.getTopParentName(name)

        if p is not None and (p == name or p != self._currentBaseFrameName):
            # 親(or 別の親の子)
            if self._currentBaseFrame is not None:
                self._currentBaseFrame.pack_forget()

            self._currentBaseFrame = self._base.wholeData[p].frame
            self._currentBaseFrameName = p
            self._currentBaseFrame.pack(fill=tk.BOTH, expand=True)
        else:
            # 子
            pass

        self._currentFrame = self._base.wholeData[name].frame
        self._currentFrameName = name

        self._currentChange(name)

    def create(self, name: str, **kwargs) -> tk.Frame:
        """
        フレームを作成する
        """
        if name in self._base.wholeData:
            raise ValueError(f"既に同名のフレーム「{name}」が存在します")

        frame = tk.Frame(self._base.root, name=name, **kwargs)

        self._base.wholeData[name] = _Tkc_Data(
            self._base, frame, name
        )

        return frame

    def add(self, name: str, **kwargs) -> tk.Frame:
        """
        フレームを作成し追加する
        """
        frame = self.create(name, **kwargs)

        self._currentChangeEvent(name)

        return frame

    def createChild(
            self, name: str,
            tabTraversal: bool = True, useParentVariable: bool = False,
            establishment: ta_establishment = "pack", establishData: Dict[str, Any] = {},
            **kwargs) -> tk.Frame:
        """
        子フレームを作成する
        """
        if name in self._base.wholeData:
            raise ValueError(f"既に同名のフレーム「{name}」が存在します")

        frame = tk.Frame(
            self._currentFrame,
            name=name,
            **kwargs
        )

        par = self.getParentList()
        uv = ""
        tt = ""
        if len(par) >= 0:
            if useParentVariable:
                uv = self._base.wholeData[par[0]].useVariable
            if tabTraversal:
                tt = self._base.wholeData[par[0]].tabTraversal

        self._base.wholeData[name] = _Tkc_Data(
            self._base,
            frame, name,
            establishment=establishment,
            establishData=establishData,
            parent=par,
            tabTraversal=tt,
            useParentVariable=uv,
        )

        return frame

    @overload
    def addChild(
        self, name: str, *,
            pos: ta_pos = None, width: int = 0, height: int = 0,
            anchor: ta_anchor = "center",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            tabTraversal: bool = True, useParentVariable: bool = False,
            **kwargs
    ) -> tk.Frame:
        pass

    @overload
    def addChild(
        self, name: str, *,
            anchor: ta_anchor = "center", expand: bool = False, fill: ta_fill = "both", side: ta_side = "top",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            tabTraversal: bool = True, useParentVariable: bool = False,
            **kwargs
    ) -> tk.Frame:
        pass

    @overload
    def addChild(
            self, name: str, *,
            row: ta_opInt = None, column: ta_opInt = None,
            rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            tabTraversal: bool = True, useParentVariable: bool = False,
            **kwargs) -> tk.Frame:
        pass

    def addChild(
            self, name: str, *,
            pos: ta_pos = None, width: int = 0, height: int = 0,
            anchor: ta_anchor = "center", expand: bool = False, fill: ta_fill = "both", side: ta_side = "top",
            row: ta_opInt = None, column: ta_opInt = None,
            rowspan: int = 1, columnspan: int = 1,
            sticky: str = "",
            padx: int = 0, pady: int = 0, ipadx: int = 0, ipady: int = 0,
            tabTraversal: bool = True, useParentVariable: bool = False,
            **kwargs) -> tk.Frame:
        """
        子フレームを作成し追加する
        """

        establishment = ""
        establishData: Dict[str, Any] = {
            "padx": padx,
            "pady": pady,
            "ipadx": ipadx,
            "ipady": ipady,
        }
        if row is None or column is None:
            establishData["anchor"] = anchor
            if pos is None:
                establishment = "pack"
                establishData["expand"] = expand
                establishData["fill"] = fill
                establishData["side"] = side
            else:
                pos = Vector2.convert(pos)
                establishment = "place"
                establishData["x"] = pos.x
                establishData["y"] = pos.y
                establishData["width"] = width
                establishData["height"] = height
        else:
            establishment = "grid"
            establishData["row"] = row
            establishData["column"] = column
            establishData["rowspan"] = rowspan
            establishData["columnspan"] = columnspan
            establishData["sticky"] = sticky

        frame = self.createChild(
            name,
            tabTraversal, useParentVariable,
            establishment, establishData,
            **kwargs
        )

        self._currentChangeEvent(name)

        if establishment == "pack":
            frame.pack(
                anchor=anchor, expand=expand, fill=fill, side=side,
                padx=padx, pady=pady, ipadx=ipadx, ipady=ipady
            )
        elif establishment == "place":
            pos = Vector2.convert(pos)
            frame.place(
                x=pos.x, y=pos.y,
                anchor=anchor, width=width, height=height,
                padx=padx, pady=pady, ipadx=ipadx, ipady=ipady
            )
        elif establishment == "grid":
            if row is not None and column is not None:
                frame.grid(
                    row=row, column=column,
                    rowspan=rowspan, columnspan=columnspan,
                    sticky=sticky,
                    padx=padx, pady=pady, ipadx=ipadx, ipady=ipady
                )

        return frame

    def get(self, name: str) -> tk.Frame:
        """
        フレームを取得する
        """
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")
        return self._base.wholeData[name].frame

    def call(self, name: str) -> tk.Frame:
        """
        フレームを呼び出す
        (フレームをカレントフレームに設定する)
        """
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")

        self._currentChangeEvent(name)
        return self.get(name)

    def forget(self, name: str) -> None:
        """
        フレームを非表示にする
        """
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")
        d = self._base.wholeData[name]
        e = d._establishment
        if e == "pack":
            d.frame.pack_forget()
        elif e == "place":
            d.frame.place_forget()
        elif e == "grid":
            d.frame.grid_forget()

    def recall(self, name: str):
        """
        フレームを表示する
        """
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")
        d = self._base.wholeData[name]
        e = d._establishment
        if e == "pack":
            d.frame.pack(**d._establishData)
        elif e == "place":
            d.frame.place(**d._establishData)
        elif e == "grid":
            d.frame.grid(**d._establishData)

    def getParentName(self, name: str = "") -> Optional[str]:
        """
        親フレーム名取得
        """
        if name == "":
            if self._currentFrameName is None:
                return None
            name = self._currentFrameName

        if name not in self._base.wholeData:
            return None

        return self._base.wholeData[name].parent

    def getTopParentName(self, name: str = "") -> Optional[str]:
        """
        最上位の親フレーム名取得
        """
        n = name
        while 1:
            f = self.getParentName(n)
            if f is None:
                return n
            n = f

    def getParentList(self, name: str = "") -> List[str]:
        """
        親フレームリスト取得
        """
        if name == "":
            if self._currentFrameName is None:
                return []
            name = self._currentFrameName
        n = name
        ret = [n]
        while 1:
            f = self.getParentName(n)
            if f is None:
                break
            n = f
            ret.append(n)
        return ret

    def getCurrentName(self) -> Optional[str]:
        """
        カレントフレーム名取得
        """
        return self._currentFrameName

    def getFrameWidgets(self, name: str) -> _Tkc_Widgets:
        """
        フレームウェジット取得
        """
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")
        return self._base.wholeData[name].widgets

    def getFrameVariable(self, name: str) -> _Tkc_Variable:
        """
        フレーム変数取得
        """
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")
        upv = self._callUseVariableName(name)
        return self._base.wholeData[upv].widgets._variable

    def getParentFrameVariable(self, name: str) -> _Tkc_Variable:
        """
        親フレーム変数取得
        """
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")
        p = self.getParentName(name)
        if p is None:
            return self.getFrameVariable(name)
        upv = self._callUseVariableName(p)
        return self._base.wholeData[upv].widgets._variable

    def _callUseVariableName(self, name: str) -> str:
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")
        return self._base.wholeData[name].useVariable

    def getChildList(self, name: str, isNest: bool = False) -> List[str]:
        """
        子フレームリスト取得
        """
        if name not in self._base.wholeData:
            raise ValueError(f"フレーム「{name}」が存在しません")

        ret: List[str] = []
        for k, v in self._base.wholeData.items():
            if v.parent == name and k != name:
                ret.append(k)
                if isNest:
                    ret += self.getChildList(k, isNest)
        return ret

    def gridConfigure(self, type: Literal["row", "column"], index: int, weight: int = 1, pad: int = 0) -> None:
        """"
        グリッドの配置設定
        """
        if self._currentFrame is None:
            raise ValueError("カレントフレームが存在しません")
        if type == "row":
            self._currentFrame.rowconfigure(index, weight=weight, pad=pad)
        elif type == "column":
            self._currentFrame.columnconfigure(index, weight=weight, pad=pad)

    def allGridConfigure(self, type: Literal["row", "column"], max_: int = 10, weight: int = 1, pad: int = 0) -> None:
        """"
        すべてのグリッドの配置設定
        """
        if self._currentFrame is None:
            raise ValueError("カレントフレームが存在しません")
        if type == "row":
            f = self._currentFrame.rowconfigure
        elif type == "column":
            f = self._currentFrame.columnconfigure

        for i in range(max_):
            f(i, weight=weight, pad=pad)
