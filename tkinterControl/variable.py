# coding: utf-8
"""
tkinterのvariableを簡単に操作出来るようにしたやつ
"""

from typing import Dict, List, Type, Union, Optional, TypeVar, cast, Final
import tkinter as tk

from lib.calc2d import classControl

# type aliases
ta_val = Union[str, float, int, bool, List[str], List[List[str]]]

ta_type = TypeVar(
    "ta_type",
    str, float, int, bool, list
)

# ここまで


class _Tkc_Variable:
    def __init__(self, names: List[str]) -> None:
        self._vars: Final[Dict[str, tk.Variable]] = {}
        self._name = names[0]

        if len(names) > 1:
            self._parent = names[1:]
        else:
            self._parent = []

    def __str__(self) -> str:
        ret = ""
        for p in reversed(self._parent):
            ret += f"Frame({p}):"
        return classControl.formatOrthop(f"{ret}Frame({self._name}):Variable", f"cou:{len(self._vars)}")

    def __len__(self) -> int:
        return len(self._vars)

    def _setVariable(self, name: str, var: tk.Variable) -> None:
        """
        変数を設定
        (存在しない場合作成)
        """
        self._vars[name] = var

    def updateValue(self, name: str, val: ta_type) -> bool:
        """
        変数を更新
        (存在しない場合作成しない)
        """
        if name not in self._vars:
            return False

        self._vars[name].set(val)
        return True

    def getVariable(self, name: str) -> tk.Variable:
        """
        変数を取得
        """
        if name not in self._vars:
            raise ValueError(f"変数「{name}」が存在しません")
        return self._vars[name]

    def getValue(self, name: str) -> ta_val:
        """
        変数の値を取得
        """
        return self.getVariable(name).get()

    def isVariable(self, name: str) -> bool:
        """
        変数の存在確認
        """
        return name in self._vars

    def toggleBool(self, name: str) -> bool:
        """
        BooleanVarを反転
        """
        var = not self.getValue(name)
        self.updateValue(name, var)
        return var

    def setAuto(self, name: str, val: ta_type) -> Type[ta_type]:
        """
        変数を設定
        (型は自動設定)
        """
        if isinstance(val, str):
            self.setString(name, val)
            return str
        elif isinstance(val, int):
            self.setInt(name, val)
            return int
        elif isinstance(val, float):
            self.setFloat(name, val)
            return float
        elif isinstance(val, bool):
            self.setBool(name, val)
            return bool
        elif isinstance(val, list):
            self.setString(name, val)
            return list
        else:
            raise ValueError("対応していない型です")

    def setSerialAutoNumber(self, name: str, val: ta_type) -> str:
        """
        システムで自動的に変数を作成する際に
        重複しない名称を自動設定し変数を作成
        """
        mx = 0
        for v in self._vars.keys():
            if "-" in v:
                sp = v.split("-")
                if name == sp[0] \
                        and len(sp) == 2 \
                        and sp[1].isdigit():
                    mx = max(mx, int(sp[1]))
        mx += 1
        newName = f"{name}-{mx}"
        self.setAuto(newName, val)
        return newName

    def setString(self, name: str, val: Union[str, List[str], List[List[str]]] = "") -> None:
        """
        StringVarを設定
        """
        # ゴリ押し
        val = cast(str, val)
        self._setVariable(name, tk.StringVar(value=val))

    def setInt(self, name: str, val: int = 0) -> None:
        """
        IntVarを設定
        """
        self._setVariable(name, tk.IntVar(value=val))

    def setFloat(self, name: str, val: float = 0) -> None:
        """
        DoubleVarを設定
        """
        self._setVariable(name, tk.DoubleVar(value=val))

    def setBool(self, name: str, val: bool = False) -> None:
        """
        BooleanVarを設定
        """
        self._setVariable(name, tk.BooleanVar(value=val))

    def getAllVariablesName(self) -> List[str]:
        """
        変数名を全て取得
        """
        return list(self._vars.keys())

    def getVariableName(self, var: tk.Variable) -> Optional[str]:
        """
        変数名を取得
        """
        for k, v in self._vars.items():
            if v == var:
                return k
        return None
