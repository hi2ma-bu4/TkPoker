# coding: utf-8
"""
lenとかljust,rjust,centerを全角に対応させる
"""

from unicodedata import east_asian_width
from re import compile as _re_compile

_winCode = _re_compile("\033\\[\\d+(;\\d+)*[A-DHJKhmsu]")


def slen(text: str) -> int:
    """
    全角半角文字幅取得
    """
    cou = 0
    tmp = _winCode.sub("", text)
    for c in tmp:
        if east_asian_width(c) in 'FWA':
            cou += 2
        else:
            cou += 1
    return cou


def _s(s: str, width: int) -> int:
    return max(width - slen(s), 0)


def ljust(s: str, width: int, fillchar: str = ' ') -> str:
    """
    左揃え
    """
    return s + fillchar * _s(s, width)


def rjust(s: str, width: int, fillchar: str = ' ') -> str:
    """
    右揃え
    """
    return fillchar * _s(s, width) + s


def center(s: str, width: int, fillchar: str = ' ') -> str:
    """
    中央揃え
    """
    space = _s(s, width)
    r = space // 2
    L = space - r
    return fillchar * L + s + fillchar * r


def sslice(s: str, start: int = 0, end: int = -1) -> str:
    """
    全角・半角を区別して文字列を切り詰める
    """
    if end == -1:
        end = slen(s)
    sliced_text = ''
    old_sliced_text = ''
    old_count = -1
    overCou = 10
    a = ""
    for i in range(start, len(s)):
        count = slen(s[:i+1])

        # lenと同じ長さになったときに抽出完了
        if end < count:
            if old_count == -1:
                old_count = count
                old_sliced_text = sliced_text
            elif old_count == count:
                old_sliced_text = sliced_text
                overCou = 10
            elif overCou <= 0:
                break
            else:
                overCou -= 1
        if start <= count:
            sliced_text += s[i]

    if old_sliced_text == "":
        return sliced_text
    return old_sliced_text
