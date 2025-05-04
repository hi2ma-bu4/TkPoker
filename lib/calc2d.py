# coding: utf-8
"""
ただの2次元計算
"""

from typing import Any, List, Tuple, Union, Optional, final
from dataclasses import dataclass

from copy import deepcopy

# type aliases
ta_opInt = Optional[int]
ta_pos = Optional[Union["Vector2", Union[Tuple[int, int], List[int]]]]

# ここまで


@final
@dataclass
class classControl:
    @staticmethod
    def formatOrthop(name: str, *args: Any) -> str:
        """
        classデバッグ用format出力
        """
        return f"<{name} [{', '.join(map(str, args))}]>"

    @staticmethod
    def typeofError(val: Any, _type: type, valName: str) -> None:
        """
        型チェック
        (エラーで停止)
        """
        if type(val) is not _type:
            raise TypeError(f"{valName} must be {_type.__name__}")


class Vector2:
    """
    2d上での座標情報
    """

    def __init__(self, x: int = 0, y: int = 0, maxX: ta_opInt = None, minX: ta_opInt = None, maxY: ta_opInt = None, minY: ta_opInt = None) -> None:
        self._x = x
        self._y = y
        self._max_x = maxX
        self._min_x = minX
        self._max_y = maxY
        self._min_y = minY

        self._overCheck()

    def update(self, x: ta_opInt = None, y: ta_opInt = None, maxX: Union[ta_opInt, str] = "", minX: Union[ta_opInt, str] = "", maxY: Union[ta_opInt, str] = "", minY: Union[ta_opInt, str] = "") -> "Vector2":
        """
        座標更新
        """
        if x != None:
            self._x = x
        if y != None:
            self._y = y

        if not isinstance(maxX, str):
            self._max_x = maxX
        if not isinstance(minX, str):
            self._min_x = minX
        if not isinstance(maxY, str):
            self._max_y = maxY
        if not isinstance(minY, str):
            self._min_y = minY

        self._overCheck()
        return self

    def add(self, x: ta_opInt = None, y: ta_opInt = None) -> "Vector2":
        """
        座標の増分
        """
        if x != None:
            self._x += x
        if y != None:
            self._y += y

        self._overCheck()
        return self

    def pos(self) -> Tuple[int, int]:
        """
        座標返却(x, y)
        """
        return (self.x, self.y)

    def copy(self) -> "Vector2":
        """
        座標位置等deepCopy
        """
        return deepcopy(self)

    def reverse(self) -> "Vector2":
        return Vector2(self.y, self.x, self._max_y, self._min_y, self._max_x, self._min_x)

    @staticmethod
    def convert(pos: ta_pos) -> "Vector2":
        if isinstance(pos, Vector2):
            return pos
        elif pos == None:
            return Vector2()
        else:
            if 1 <= len(pos) <= 6:
                return Vector2(*pos)
        return Vector2()

    def __eq__(self, oth: ta_pos) -> bool:
        v = self.convert(oth)
        return self.x == v.x and self.y == v.y

    def __add__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        return Vector2(self.x + v.x, self.y + v.y)

    def __iadd__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        return self.add(v.x, v.y)

    def __sub__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        return Vector2(self.x - v.x, self.y - v.y)

    def __isub__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        return self.add(-v.x, -v.y)

    def __mul__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        return Vector2(self.x * v.x, self.y * v.y)

    def __imul__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        self._x *= v.x
        self._y *= v.y
        self._overCheck()
        return self

    def __truediv__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        return Vector2(self._x // v._x, self._y // v._y)

    def __itruediv__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        self._x //= v.x
        self._y //= v.y
        self._overCheck()
        return self

    def __floordiv__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        return Vector2(self._x // v._x, self._y // v._y)

    def __ifloordiv__(self, oth: Union[ta_pos, int]) -> "Vector2":
        if isinstance(oth, int):
            v = Vector2(oth, oth)
        else:
            v = self.convert(oth)
        self._x //= v.x
        self._y //= v.y
        self._overCheck()
        return self

    def __abs__(self) -> "Vector2":
        return Vector2(abs(self._x), abs(self._y))

    def __format__(self, spec: str) -> str:
        if spec == "x":
            return str(self._x)
        if spec == "y":
            return str(self._x)
        return classControl.formatOrthop("Vector2", self._x, self._y)

    def __str__(self) -> str:
        return classControl.formatOrthop("Vector2", self._x, self._y)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __call__(self) -> Tuple[int, int]:
        """
        座標取得(x,y)
        """
        return self.pos()

    def _overCheck(self) -> None:
        """
        座標位置を正常に
        """
        if self._max_x != None and self._x > self._max_x:
            self._x = self._max_x
        if self._min_x != None and self._x < self._min_x:
            self._x = self._min_x
        if self._max_y != None and self._y > self._max_y:
            self._y = self._max_y
        if self._min_y != None and self._y < self._min_y:
            self._y = self._min_y

    @final
    @property
    def x(self) -> int:
        return self._x

    @final
    @x.setter
    def x(self, val: int) -> None:
        classControl.typeofError(val, int, "Vector2.x")
        self._x = val
        self._overCheck()

    @final
    @property
    def y(self) -> int:
        return self._y

    @final
    @y.setter
    def y(self, val: int) -> None:
        classControl.typeofError(val, int, "Vector2.y")
        self._y = val
        self._overCheck()
