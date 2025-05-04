# coding: utf-8
"""
tkinterのcanvasを簡単に操作出来るようにしたやつ
"""


from typing import Any, Tuple, Union, Optional, Callable, Literal, ClassVar, Type, Final, final
from dataclasses import dataclass
from tkinter import Canvas, Event

from .photo import _Tkc_Photo, ta_imageTk
from lib.calc2d import Vector2, ta_pos

# type aliases
ta_anchor = Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"]
ta_com = Callable[..., Any]

ta_cusImageTk = Union[str, ta_imageTk]

ta_tuple_color = Tuple[int, int, int]
ta_color = Union[ta_tuple_color, str]

# ここまで


class _Tkc_CanvasObject:
    """
    canvas上に設置されているオブジェクト
    """

    def __init__(self, cvs: Canvas, item: int, name: str) -> None:
        self._cvs: Final[Canvas] = cvs
        self._item: Final[int] = item
        self._name: Final[str] = name

        self._isDestroyed: bool = False

    def __str__(self) -> str:
        return f"<canvasObj [name:{self._name},id:{self._item}]>"

    def move(self, pos: ta_pos) -> None:
        """
        座標移動
        (相対座標)
        """
        p = Vector2.convert(pos)
        self._cvs.move(self._item, p.x, p.y)

    def setPos(self, pos: ta_pos) -> None:
        """
        座標設定
        (絶対座標)
        """
        p = Vector2.convert(pos)
        self._cvs.coords(self._item, p.x, p.y)

    def getPos(self) -> Vector2:
        """
        座標取得
        """
        p = self._cvs.coords(self._item)
        return Vector2(int(p[0]), int(p[1]))

    def topmost(self) -> None:
        """
        最前面に
        """
        self._cvs.tag_raise(self._item)

    def bottommost(self) -> None:
        """
        最背面に
        """
        self._cvs.tag_lower(self._item)

    def destroy(self) -> None:
        """
        削除
        """
        self._isDestroyed = True
        self._cvs.delete(self._item)

    @property
    def item(self) -> int:
        return self._item

    @property
    def name(self) -> str:
        return self._name


class _Tkc_Canvas:
    """
    canvas管理クラス
    """

    CanvasItem: ClassVar[Type[_Tkc_CanvasObject]] = _Tkc_CanvasObject

    def __init__(self, _base, canvas: Canvas) -> None:
        self._base: Final = _base
        self._photos: Final[_Tkc_Photo] = self._base._photos
        self._cvs: Final[Canvas] = canvas

        self._clickEventFunc = None
        self._itemTmpIdDict = {}

        self._initBind()

    def __len__(self) -> int:
        return len(self._itemTmpIdDict)

    def _initBind(self) -> None:
        self._cvs.bind("<Button-1>", self._onClick)

    def _onClick(self, event: Event) -> None:
        x, y = self._cvs.canvasx(event.x), self._cvs.canvasy(event.y)

        start_clicked = [
            self._cvs.itemcget(obj, 'tags')
            for obj in self._cvs.find_overlapping(x, y, x, y)
        ]

        cur = None
        lst = []
        for tag in start_clicked:
            spTag = tag.split(" ")
            if "current" in spTag:
                spTag.remove("current")
                cur = self.getItem(spTag[0])
            lst.append(self.getItem(spTag[0]))

        if self._clickEventFunc is not None:
            self._clickEventFunc(event, x, y, cur, lst)

    def _setSerialAutoNumber(self, name: str) -> str:
        """
        システムで自動的に名前を作成する際に
        重複しない名称を自動作成
        """
        mx = 0
        for v in self._itemTmpIdDict.keys():
            if "-" in v:
                sp = v.split("-")
                if name == sp[0] \
                        and len(sp) == 2 \
                        and sp[1].isdigit():
                    mx = max(mx, int(sp[1]))
        mx += 1
        newName = f"{name}-{mx}"
        return newName

    def getClickEvent(self, func: ta_com) -> None:
        """
        コールバック関数を指定

        コールバック関数引数
        * event [tk.Event]: イベント
        * x [int]: canvas x座標
        * y [int]: canvas y座標
        * current [itemObj | None]: 選択されたオブジェクト(最上面)
        * clicked [List[itemObj]]: 選択されたオブジェクト
        """
        self._clickEventFunc = func

    def bind(self, event: str, func: ta_com, add: bool = False) -> None:
        """
        イベントを設定
        """
        if event in ["<Button-1>", "<ButtonPress-1>", "<1>"]:
            add = True
        self._cvs.bind(event, func, add)

    def clear(self) -> None:
        """
        キャンバスをクリア
        """
        self._cvs.delete("all")
        self._itemTmpIdDict.clear()

    def drawSquare(
            self, pos: ta_pos = (0, 0),
            size: ta_pos = (100, 100),
            color: ta_color = "white",
            bd_color: Optional[ta_color] = None, *,
            name: str = "") -> _Tkc_CanvasObject:
        """
        四角形描画
        """
        p = Vector2.convert(pos)
        s = Vector2.convert(size)
        if name == "":
            name = self._setSerialAutoNumber("__Square")
        if name in self._itemTmpIdDict:
            raise ValueError(f"{name}はすでに使用されています")

        if bd_color is None:
            bd_color = color

        item = self._cvs.create_rectangle(
            p.x, p.y, p.x + s.x, p.y + s.y,
            fill=Colors.auto_hex(color),
            outline=Colors.auto_hex(bd_color),
            tags=name
        )

        co = _Tkc_CanvasObject(self._cvs, item, name)
        self._itemTmpIdDict[name] = co
        return co

    def drawCircle(
            self, pos: ta_pos = (0, 0),
            size: ta_pos = (100, 100),
            color: ta_color = "white",
            bd_color: Optional[ta_color] = None, *,
            name: str = "") -> _Tkc_CanvasObject:
        """
        円形描画
        """
        p = Vector2.convert(pos)
        s = Vector2.convert(size)
        if name == "":
            name = self._setSerialAutoNumber("__Circle")
        if name in self._itemTmpIdDict:
            raise ValueError(f"{name}はすでに使用されています")

        if bd_color is None:
            bd_color = color

        item = self._cvs.create_oval(
            p.x, p.y, p.x + s.x, p.y + s.y,
            fill=Colors.auto_hex(color),
            outline=Colors.auto_hex(bd_color),
            tags=name
        )

        co = _Tkc_CanvasObject(self._cvs, item, name)
        self._itemTmpIdDict[name] = co
        return co

    def drawText(
            self, text: str,
            font: Tuple[str, int] = ("Arial", 12),
            pos: ta_pos = (0, 0), anchor: ta_anchor = "nw",
            color: ta_color = "black", *,
            name: str = "") -> _Tkc_CanvasObject:
        """
        テキスト描画
        """
        p = Vector2.convert(pos)
        if name == "":
            name = self._setSerialAutoNumber("__Text")
        if name in self._itemTmpIdDict:
            raise ValueError(f"{name}はすでに使用されています")

        item = self._cvs.create_text(
            p.x, p.y, text=text,
            font=font,
            fill=Colors.auto_hex(color),
            anchor=anchor, tags=name
        )

        co = _Tkc_CanvasObject(self._cvs, item, name)
        self._itemTmpIdDict[name] = co
        return co

    def drawImage(
            self, imageName: ta_cusImageTk,
            pos: ta_pos = (0, 0), anchor: ta_anchor = "nw", *,
            name: str = "") -> _Tkc_CanvasObject:
        """
        画像描画
        """
        im = self._photos.getImageTk(imageName)
        p = Vector2.convert(pos)
        if name == "":
            name = self._setSerialAutoNumber("__Image")
        if name in self._itemTmpIdDict:
            raise ValueError(f"{name}はすでに使用されています")

        item = self._cvs.create_image(
            p.x, p.y, image=im, anchor=anchor, tag=name
        )

        co = _Tkc_CanvasObject(self._cvs, item, name)
        self._itemTmpIdDict[name] = co
        return co

    def update(self) -> None:
        """
        画面更新
        """
        self._cvs.update()

    def getItem(self, name: Union[str, int]) -> Optional[_Tkc_CanvasObject]:
        """
        itemを取得
        """
        if isinstance(name, str):
            if name not in self._itemTmpIdDict:
                return None
            iti = self._itemTmpIdDict[name]
            if iti._isDestroyed:
                del self._itemTmpIdDict[name]
                return None
            return iti
        elif isinstance(name, int):
            for v in self._itemTmpIdDict.values():
                if v.item == name:
                    if v._isDestroyed:
                        del self._itemTmpIdDict[v._name]
                        return None
                    return v
            return None
        return None

    @final
    @property
    def canvas(self) -> Canvas:
        return self._cvs


@dataclass
class Colors:
    """
    色定義
    """

    WHITE: Final[ta_tuple_color] = (255, 255, 255)
    GRAY: Final[ta_tuple_color] = (128, 128, 128)
    BLACK: Final[ta_tuple_color] = (0, 0, 0)
    RED: Final[ta_tuple_color] = (255, 0, 0)
    GREEN: Final[ta_tuple_color] = (0, 255, 0)
    BLUE: Final[ta_tuple_color] = (0, 0, 255)

    @final
    @classmethod
    def auto_tuple(cls, obj: ta_color) -> Tuple[int, int, int]:
        """
        自動で色コード(hex)をTupleに変換する
        """
        if isinstance(obj, str):
            return cls.hex2Tuple(obj)
        elif isinstance(obj, tuple):
            return obj
        raise ValueError(f"{obj}は正しくありません")

    @final
    @classmethod
    def auto_hex(cls, obj: ta_color) -> str:
        """
        自動で色コード(Tuple)をhexに変換する
        """
        if isinstance(obj, tuple):
            return cls.tuple2Hex(obj)
        elif isinstance(obj, str):
            return obj
        raise ValueError(f"{obj}は正しくありません")

    @final
    @staticmethod
    def hex2Tuple(hex: str) -> Tuple[int, int, int]:
        """
        カラーコードをタプルに
        """

        if hex[0] == "#":
            hex = hex[1:]

        # 16進数を10進数に
        try:
            return (int(hex[0:2], 16), int(hex[2:4], 16), int(hex[4:6], 16))
        except:
            return (0, 0, 0)

    @final
    @staticmethod
    def tuple2Hex(tup: Tuple[int, int, int]) -> str:
        """
        タプルをカラーコードに
        """

        # 10進数を16進数に
        try:
            return f"#{hex(tup[0])}{hex(tup[1])}{hex(tup[2])}".upper()
        except:
            return "#000000"
