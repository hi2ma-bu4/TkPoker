# coding: utf-8
"""
文字計算ライブラリ
"""

from typing import Any, List, Literal, Union

from .eastAsianWidthOverride import slen, ljust, rjust, center, sslice


def a_join(l: List[str]) -> str:
    """
    文字列リストを結合
    """
    if not len(l):
        return ""
    return "".join(l)


def listFind(l: List[Any], x: Any) -> int:
    """
    String専用のfindをlistでも使用出来るようにした関数
    """
    if x in l:
        return l.index(x)
    else:
        return -1


def autoReturn(s: str, m: int, sep="\n") -> str:
    if len(s) <= 0:
        return ""
    if len(s) == m:
        return s
    return "\n".join(
        [sslice(s, i, i+m-1) for i in range(0, slen(s), m)]
    )


class Base:
    """
    進数計算
    """

    def __init__(self, char: str = "0123456789abcdef") -> None:
        """
        初期化
        """
        self._char = char
        self._cLen = len(self._char)
        self._cDic = {self._char[i]: i for i in range(self._cLen)}

    def dec2n(self, dec: int, n: int) -> Union[str, Literal[-1]]:
        """
        10進数をn進数に変換
        """
        d, n = int(dec), int(n)

        if 2 <= n <= self._cLen:
            ans = ""
            while d:
                r = d % n
                ans = self._char[r] + ans
                d = d // n
            if ans == "":
                ans = self._char[0]
            return ans
        else:
            return -1

    def n2dec(self, n: int, dec: str) -> int:
        """
        n進数を10進数に変換
        """
        n, dec = int(n), str(dec)
        if 2 <= n <= self._cLen:
            ans = 0
            for figure in dec:
                ans = ans * n + self._cDic[figure]
            return ans
        else:
            return -1

    def n2m(self, n, dec, m) -> Union[str, Literal[-1]]:
        tmp = self.n2dec(n, dec)
        if tmp == -1:
            return -1
        return self.dec2n(tmp, m)
