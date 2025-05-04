# coding: utf-8
"""
トランプライブラリ
"""

from typing import List, Tuple, Dict, Literal, Optional, Union, Callable, ClassVar, Type, cast, Final, final
import random
import os
import asyncio
from itertools import combinations
from concurrent import futures
import time


# type alias
ta_suit_char = Literal["s", "h", "d", "c"]
ta_suit_mark = Literal["♠", "♥", "♦", "♣"]
ta_rank_char = Literal[
    1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13
]
ta_rank_mark = Literal[
    "A", "2", "3", "4", "5", "6", "7",
    "8", "9", "10", "J", "Q", "K"
]
ta_joker = Literal["Joker"]

ta_judge_bool = Union[List["Card"], Literal[False]]
ta_judgement = Tuple[
    Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    List["Card"]
]


class Card:
    """
    カードデータ
    """

    # スート(判定用)
    _SUIT_CHAR_TYPE: Final[Tuple[
        Literal["s"], Literal["h"], Literal["d"], Literal["c"]
    ]] = ("s", "h", "d", "c")

    # スート(マーク)
    _SUIT_MARK_TYPE: Final[Dict[
        ta_suit_char, ta_suit_mark
    ]] = {
        "s": "♠", "h": "♥", "d": "♦", "c": "♣"
    }

    _SUIT_POWER: Final[Dict[
        Union[ta_suit_char, ta_joker], int
    ]] = {
        "s": 4, "h": 3, "d": 2, "c": 1,
        "Joker": 10
    }

    # ランク(表示用)
    _RANK_MARK_TYPE: Final[Tuple[
        Literal["A"], Literal["2"], Literal["3"], Literal["4"], Literal["5"],
        Literal["6"], Literal["7"], Literal["8"], Literal["9"], Literal["10"],
        Literal["J"], Literal["Q"], Literal["K"]
    ]] = (
        "A", "2", "3", "4", "5", "6", "7",
        "8", "9", "10", "J", "Q", "K"
    )

    def __init__(self, suit: ta_suit_char = "s", rank: ta_rank_char = 1, *, isJoker: bool = False) -> None:
        self.__suit: Final[ta_suit_char] = suit
        self.__rank: Final[ta_rank_char] = rank

        self.__isJoker: Final[bool] = isJoker

    def __str__(self) -> str:
        if self.__isJoker:
            return "Joker"
        return f"{self.suitMark}{self.rankMark}"

    def __bool__(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        if self.__isJoker or other.__isJoker:
            return True
        return self.rank == other.rank

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        if self.rank == other.rank:
            return self.rank == "Joker"
        jg = self._joker_gt(other)
        if jg is not None:
            return jg
        rg = self._rank_gt(other)
        if rg is None:
            return False
        return rg

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        if self.rank == other.rank:
            return self.rank == "Joker"
        jg = other._joker_gt(self)
        if jg is not None:
            return jg
        rg = other._rank_gt(self)
        if rg is None:
            return False
        return rg

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        if self.rank == other.rank:
            return True
        jg = self._joker_gt(other)
        if jg is not None:
            return jg
        rg = self._rank_gt(other)
        if rg is None:
            return False
        return rg

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False
        if self.rank == other.rank:
            return True
        jg = other._joker_gt(self)
        if jg is not None:
            return jg
        rg = other._rank_gt(self)
        if rg is None:
            return False
        return rg

    def _joker_gt(self, other: "Card") -> Optional[bool]:
        if self.rank == "Joker":
            if other.rank == "Joker":
                return False
            return True
        if other.rank == "Joker":
            return False
        return None

    def _rank_gt(self, other: "Card") -> Optional[bool]:
        sr = self.rank
        or_ = other.rank
        if sr == "Joker" or or_ == "Joker":
            return None
        if sr == 1:
            sr = 14
        if or_ == 1:
            or_ = 14
        return sr > or_

    def suit_eq(self, other: "Card") -> bool:
        if self.__isJoker or other.__isJoker:
            return True
        return self.suit == other.suit

    def suit_gt(self, other: "Card") -> Optional[bool]:
        return self._SUIT_POWER[self.suit] > self._SUIT_POWER[other.suit]

    def suit_lt(self, other: "Card") -> Optional[bool]:
        return self._SUIT_POWER[self.suit] < self._SUIT_POWER[other.suit]

    @classmethod
    def convert(cls, s: str) -> "Card":
        if s == "Joker":
            return cls(isJoker=True)
        if s[0] not in cls._SUIT_CHAR_TYPE:
            raise ValueError(f"Invalid suit: {s[0]}")
        n = s[1:]
        if not n.isdigit():
            raise ValueError(f"Invalid rank: {s[1]}")
        n = int(n)
        if 1 <= n <= 13:
            r = cast(ta_rank_char, n)
            return cls(suit=s[0], rank=r)
        raise ValueError(f"Invalid rank: {s[1]}")

    @final
    @property
    def suit_power(self) -> int:
        """
        スートの数値
        """
        return self._SUIT_POWER[self.__suit]

    @final
    @property
    def suit(self) -> Union[ta_suit_char, ta_joker]:
        """
        スート判定文字出力
        """
        if self.__isJoker:
            return "Joker"
        return self.__suit

    @final
    @property
    def rank(self) -> Union[ta_rank_char, ta_joker]:
        """
        ランク判定文字出力
        """
        if self.__isJoker:
            return "Joker"
        return self.__rank

    @final
    @property
    def suitMark(self) -> Union[ta_suit_mark, ta_joker]:
        """
        スートマーク出力
        """
        if self.__isJoker:
            return "Joker"
        return self._SUIT_MARK_TYPE[self.__suit]

    @final
    @property
    def rankMark(self) -> Union[ta_rank_mark, ta_joker]:
        """
        ランクマーク出力
        """
        if self.__isJoker:
            return "Joker"
        return self._RANK_MARK_TYPE[self.__rank-1]

    @final
    @property
    def judgeStr(self) -> str:
        """
        判定用文字出力
        """
        if self.__isJoker:
            return "Joker"
        return f"{self.suit}{self.rank}"


class CardDeck:
    """
    カードデッキ
    """

    def __init__(self, trump: "Trump", cardList: List[Card]) -> None:
        self.__base: Trump = trump
        self.__cardList: List[Card] = cardList

        self._isThrowDeck = len(self.__cardList) == 0

    def __str__(self) -> str:
        s = ""
        for card in self.__cardList:
            s += str(card) + ", "
        return f"[{s[:-2]}]"

    def __len__(self) -> int:
        return len(self.__cardList)

    def copy(self) -> "CardDeck":
        """
        複製
        """
        return CardDeck(self.__base, self.__cardList.copy())

    def reset(self, cardList: List[Card]) -> None:
        """
        リセット
        """
        self.__cardList = cardList

    def sort(self) -> None:
        """
        ソート
        (並びはポーカーでの強さ順)
        """
        self.__cardList.sort(key=lambda x: x.suit_power, reverse=True)
        self.__cardList.sort()

    def add(self, card: Card) -> None:
        """
        カード追加
        """
        self.__cardList.append(card)

    def get(self, index: int = 0) -> Card:
        """
        カード取得
        """
        return self.__cardList[index]

    def pop(self, index: int = 0, moveThrowDeck: bool = True) -> Card:
        """
        カード取得(削除)
        """
        c = self.__cardList.pop(index)
        if moveThrowDeck and not self._isThrowDeck:
            self.__base.throwDeck.add(c)
        return c

    def remove(self, name: str, moveThrowDeck: bool = True) -> None:
        """
        カード削除
        (先頭一致)
        """
        for i, c in enumerate(self.__cardList):
            if c.judgeStr == name:
                if moveThrowDeck and not self._isThrowDeck:
                    self.__base.throwDeck.add(c)
                self.__cardList.pop(i)
                return
        raise ValueError(f"{name}は見つかりません")

    def getIndex(self, card: Union[Card, str]) -> int:
        """
        カードのインデックス取得
        """
        if isinstance(card, str):
            for i, c in enumerate(self.__cardList):
                if c.judgeStr == card:
                    return i
            return -1
        elif isinstance(card, Card):
            return self.__cardList.index(card)
        raise ValueError(f"{card}は見つかりません")

    @property
    def cardList(self) -> List[Card]:
        """
        カードリスト
        """
        return self.__cardList


class Trump:
    """
    トランプデータの管理
    """

    Card_: ClassVar[Type[Card]] = Card
    CardDeck_: ClassVar[Type[CardDeck]] = CardDeck

    def __init__(
        self,
        useJokerCou: Literal[0, 1, 2] = 1,
        useSuitType: List[ta_suit_char] = ["s", "c", "d", "h"],
        useRankType: List[ta_rank_char] = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
        ]
    ) -> None:
        self.__useJokerCou: Final[Literal[0, 1, 2]] = useJokerCou
        self.__useSuitType: Final[List[ta_suit_char]] = useSuitType
        self.__useRankType: Final[List[ta_rank_char]] = useRankType

        self.__cardList: List[Card] = []

        self.__deckList: List[CardDeck] = []

        self.__throwDeck: CardDeck = CardDeck(self, [])

        self.reset()

    def __len__(self) -> int:
        return len(self.__cardList)

    def __str__(self) -> str:
        s = ""
        for card in self.__cardList:
            s += str(card) + ", "
        return f"[{s[:-2]}]"

    def reset(self) -> None:
        """
        リセット
        """
        self.__cardList.clear()
        for suit in self.__useSuitType:
            for rank in self.__useRankType:
                self.__cardList.append(Card(suit, rank))

        for _ in range(self.__useJokerCou):
            self.__cardList.append(Card(isJoker=True))

    def shuffle(self) -> None:
        """
        シャッフル
        """
        self.reset()
        random.shuffle(self.__cardList)

    def distribution(self, num: int) -> None:
        """
        均等に人数分配

        (完全分配)
        """
        lst = []
        cl = len(self)
        cn = cl//num
        for i in range(num):
            lst.append([])
            for card in self.__cardList[i*cn:(i+1)*cn]:
                lst[-1].append(card)

        rl = [*range(num-1)]
        random.shuffle(rl)

        for i in range(cl % num):
            lst[rl.pop()].append(self.__cardList[cn*num+i])

        # デッキ設定
        self.__deckList.clear()
        for i in range(num):
            self.__deckList.append(CardDeck(self, lst[i]))

    def distribute(self, num: int, max_: int) -> None:
        """
        人数分配

        (固定分配)
        """
        if num * max_ > len(self.__cardList):
            raise ValueError("人数分配失敗")
        # デッキ設定
        self.__deckList.clear()

        cou = 0
        for i in range(num):
            self.__deckList.append(
                CardDeck(self, self.__cardList[cou:cou+max_])
            )
            cou += max_

        self.__throwDeck.reset(self.__cardList[cou:])

    @property
    def cardList(self) -> List[Card]:
        """
        カードリスト
        """
        return self.__cardList

    @property
    def deckList(self) -> List[CardDeck]:
        """
        カードデッキリスト
        """
        return self.__deckList

    @property
    def throwDeck(self) -> CardDeck:
        """
        山札
        """
        return self.__throwDeck


class Poker:
    """
    ポーカーの判定、処理クラス

    (ジョーカーは1枚までしか対応していません)
    """

    _TRANS_DICT: Dict[int, str] = {
        0: "ハイカード",
        2: "ワンペア",
        3: "ツーペア",
        5: "スリーカード",
        7: "ストレート",
        9: "フラッシュ",
        11: "フルハウス",
        13: "フォーカード",
        15: "ストレートフラッシュ",
        17: "ロイヤルストレートフラッシュ",
        19: "ファイブカード"
    }

    @classmethod
    def get_trans(cls, transId: int) -> Tuple[str, str]:
        """
        役名取得
        """

        if transId in cls._TRANS_DICT:
            if transId == 0:
                return cls._TRANS_DICT[0], "(ブタ)"
            return cls._TRANS_DICT[transId], ""
        transId += 1
        if transId in cls._TRANS_DICT:
            return cls._TRANS_DICT[transId], "(Joker)"
        return "不明", "(Error)"

    @classmethod
    def confrontation(cls, cardDeck1: CardDeck, cardDeck2: CardDeck) -> Tuple[Literal[1, 0, -1], int, int]:
        """
        ポーカー勝負
        * 1: (引数)左の勝利
        * 0: 引き分け
        * -1: (引数)右の勝利
        """
        judge1 = cls.judgement(cardDeck1)
        judge2 = cls.judgement(cardDeck2)

        p1 = judge1[0]
        p2 = judge2[0]

        if p1 > p2:
            # 左の勝ち
            return 1, p1, p2
        elif p1 < p2:
            # 右の勝ち
            return -1, p1, p2
        else:
            # 引き分け
            p1 = judge1[1][0]
            p2 = judge2[1][0]

            if judge1[0] == 17:
                # ロイヤルストレートフラッシュの場合
                if p1.suit_power > p2.suit_power:
                    # 左の勝ち
                    return 1, judge1[0], judge2[0]
                elif p1.suit_power < p2.suit_power:
                    # 右の勝ち
                    return -1, judge1[0], judge2[0]
                raise ValueError("ロイヤルストレートフラッシュの勝敗判定に失敗しました")

            if p1 > p2:
                # 左の勝ち
                return 1, judge1[0], judge2[0]
            elif p1 < p2:
                # 右の勝ち
                return -1, judge1[0], judge2[0]
            else:
                # 引き分け
                return 0, judge1[0], judge2[0]

    @classmethod
    def judgement(cls, cardDeck: CardDeck) -> ta_judgement:
        """
        役判定
        * 0: ハイカード(ブタ)
        * 2: ワンペア
        * 3: ツーペア
        * 5: スリーカード
        * 7: ストレート
        * 9: フラッシュ
        * 11: フルハウス
        * 13: フォーカード
        * 15: ストレートフラッシュ
        * 17: ロイヤルストレートフラッシュ
        * 18: ファイブカード(Joker)

        ※ジョーカー混入時は(判定-1)を返却
        """
        tmpDeck = cardDeck.copy()
        tmpDeck.sort()

        # ジョーカー混入判定
        inJoker: Literal[0, 1] = 0
        for card in tmpDeck.cardList:
            if card.rank == "Joker":
                inJoker = 1
                break

        # ファイブカード
        if inJoker:
            if r := cls.judge_five_of_a_kind(tmpDeck):
                return 18, r

        # ロイヤルストレートフラッシュ
        if r := cls.judge_royal_straight_flush(tmpDeck):
            return 17-inJoker, r
        # ストレートフラッシュ
        if r := cls.judge_straight_flush(tmpDeck):
            return 15-inJoker, r
        # フォーカード
        if r := cls.judge_four_of_a_kind(tmpDeck):
            return 13-inJoker, r
        # フルハウス
        if r := cls.judge_full_house(tmpDeck):
            return 11-inJoker, r
        # フラッシュ
        if r := cls.judge_flush(tmpDeck):
            return 9-inJoker, r
        # ストレート
        if r := cls.judge_straight(tmpDeck):
            return 7-inJoker, r
        # スリーカード
        if r := cls.judge_three_of_a_kind(tmpDeck):
            return 5-inJoker, r
        # ツーペア
        if r := cls.judge_two_pair(tmpDeck):
            return 3, r
        # ワンペア
        if r := cls.judge_one_pair(tmpDeck):
            return 2-inJoker, r

        # ハイカード
        return 0, cls._getReverseMinCardList(tmpDeck)

    @staticmethod
    def card2bool(card: Union[Card, bool]) -> bool:
        """
        カードをbool値に変換
        """
        if isinstance(card, Card):
            return True
        return card

    @classmethod
    def judge_royal_straight_flush(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        ロイヤルストレートフラッシュ
        """
        r = cls.judge_straight_flush(cardDeck)
        if r:
            if len(r) == 5 and r[0].rank == 1:
                return r
            if len(r) == 4:
                if r[0].rank == 1 or r[3].rank == 10:
                    return r
        return False

    @classmethod
    def judge_straight_flush(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        ストレートフラッシュ
        """
        r = cls.judge_flush(cardDeck)
        if cls.judge_straight(cardDeck) and r:
            return r
        return False

    @classmethod
    def judge_flush(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        フラッシュ
        """
        t = cardDeck.get(0).suit
        if t == "Joker":
            t = cardDeck.get(1).suit
        for c in cardDeck.cardList:
            if c.suit != t and c.suit != "Joker":
                return False

        t = cardDeck.get(4).rank
        if t == "Joker":
            return cls._getReverseMinCardList(cardDeck, 3)
        return cls._getReverseMinCardList(cardDeck, 4)

    @classmethod
    def judge_straight(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        ストレート
        """
        jFlag = False
        usJoker = False

        tList = []
        for i in range(len(cardDeck)):
            if cardDeck.get(i).rank == "Joker":
                jFlag = True
                usJoker = True
            else:
                rnk = cardDeck.get(i).rank
                if rnk == 1:
                    rnk = 14
                tList.append(rnk)

        for i in range(2+(not jFlag)):
            if tList[i+1] - tList[i] != 1:
                if usJoker:
                    if tList[i+1] - tList[i] == 2:
                        usJoker = False
                        continue
                return False

        # ジョーカー混入時
        if jFlag:
            t = tList[3] - tList[2]
            # ジョーカー未使用
            if usJoker:
                if t != 1:
                    if t != 2 and t != 10:
                        # 2,3,4,6,J
                        # 2,3,4,14,J
                        return False
                else:
                    if tList[3] == 5:
                        # 2,3,4,5,J
                        pass
                return cls._getReverseMinCardList(cardDeck, 3)

            # 使用済
            # 2,3,5,6,J
            # 2,3,5,14,J
            if t == 1 or t == 9:
                return cls._getReverseMinCardList(cardDeck, 3)
            return False

        # 通常判定
        t = tList[4] - tList[3]
        if t == 1 or t == 9:
            return cls._getReverseMinCardList(cardDeck, 4)
        return False

    @classmethod
    def judge_one_pair(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        ワンペア
        """
        r = cls._countSameRankLine(cardDeck)
        if r[0] == 1:
            return r[1]
        return False

    @classmethod
    def judge_two_pair(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        ツーペア
        """
        r = cls._countSameRankLine(cardDeck)
        if r[0] == 2:
            return r[1]
        return False

    @classmethod
    def judge_three_of_a_kind(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        スリーカード
        """
        r = cls._countSameRankLine(cardDeck)
        if r[0] == 3:
            return r[1]
        return False

    @classmethod
    def judge_full_house(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        フルハウス
        """
        r = cls._countSameRankLine(cardDeck)
        if r[0] == 4:
            return r[1]
        return False

    @classmethod
    def judge_four_of_a_kind(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        フォーカード
        """
        r = cls._countSameRankLine(cardDeck)
        if r[0] == 6:
            return r[1]
        return False

    @classmethod
    def judge_five_of_a_kind(cls, cardDeck: CardDeck) -> ta_judge_bool:
        """
        ファイブカード
        """
        r = cls._countSameRankLine(cardDeck)
        if r[0] == 10:
            return r[1]
        return False

    @classmethod
    def _countSameRankLine(cls, cardDeck: CardDeck) -> Tuple[int, List[Card]]:
        """
        同じランクのカードの数
        * 0: ハイカード(ブタ)
        * 1: ワンペア
        * 2: ツーペア
        * 3: スリーカード
        * 4: フルハウス
        * 6: フォーカード
        * 10: ファイブカード(ジョーカー混入時)
        """
        dic = {}
        jFlag = False
        for c in cardDeck.cardList:
            if c.rank == "Joker":
                jFlag = True
                break
            if c.rank in dic:
                dic[c.rank] += 1
            else:
                dic[c.rank] = 1

        dl = len(dic)
        # ジョーカー混入時
        if jFlag:
            if dl == 1:
                # ファイブカード分岐
                return 10, [cardDeck.get(0)]
            if dl == 2:
                # 役分岐
                t = False
                for k, v in dic.items():
                    if v == 2:
                        t = True
                        break
                if t:
                    # フルハウス昇格
                    return 4, [
                        cardDeck.get(2),
                        cardDeck.get(0)
                    ]
                else:
                    # フォーカード昇格
                    c1 = cardDeck.get(0)
                    c2 = cardDeck.get(1)
                    c3 = cardDeck.get(3)
                    if c1.rank == c2.rank:
                        return 6, [c1, c3]
                    if c2.rank == c3.rank:
                        return 6, [c2, c1]
            if dl == 3:
                # スリーカード昇格
                b = None
                for c in cardDeck.cardList:
                    if dic[c.rank] == 2:
                        b = c
                        break
                if b is None:
                    b = cardDeck.get(0)
                r = [b]
                for i in range(3, -1, -1):
                    c = cardDeck.get(i)
                    if c.rank != b.rank:
                        r.append(c)
                return 3, r
            if dl == 4:
                # ワンペア昇格
                return 1, cls._getReverseMinCardList(cardDeck, 3)
            raise ValueError(f"不正なカード数: {dl}")

        if dl == 2:
            # 役分岐
            t = False
            for k, v in dic.items():
                if v == 2:
                    t = True
                    break
            if t:
                # フルハウス
                b = cardDeck.get(2)
                c = cardDeck.get(0)
                if b.rank == c.rank:
                    # 1,1,1,2,2
                    return 4, [
                        c,
                        cardDeck.get(3)
                    ]
                else:
                    # 1,1,2,2,2
                    return 4, [b, c]
            else:
                # フォーカード
                b = cardDeck.get(1)
                c = cardDeck.get(0)
                if b.rank == c.rank:
                    # 1,1,1,1,2
                    return 6, [
                        c,
                        cardDeck.get(4)
                    ]
                else:
                    # 1,2,2,2,2
                    return 6, [b, c]
        if dl == 3:
            # 役分岐
            t = False
            for k, v in dic.items():
                if v == 2:
                    t = True
                    break
            if t:
                # ツーペア
                r = []
                t = None
                f = False
                for c in reversed(cardDeck.cardList):
                    if dic[c.rank] == 2:
                        if f:
                            r.append(c)
                        f = not f
                        continue
                    t = c
                    f = False
                r.append(t)
                return 2, r
            else:
                # スリーカード
                c = cardDeck.cardList
                if c[1].rank == c[3].rank:
                    # 1,2,2,2,3
                    return 3, [
                        c[1],
                        c[4],
                        c[0],
                    ]
                elif c[0].rank == c[2].rank:
                    # 1,1,1,2,3
                    return 3, [
                        c[0],
                        c[4],
                        c[3],
                    ]
                elif c[2].rank == c[4].rank:
                    # 1,2,3,3,3
                    return 3, cls._getReverseMinCardList(cardDeck, 2)
                raise ValueError(f"不正なカード分布: {c}")
        if dl == 4:
            # ワンペア
            b = None
            for c in cardDeck.cardList:
                if dic[c.rank] == 2:
                    b = c
                    break
            if b is None:
                b = cardDeck.get(0)
            r = [b]
            for i in range(4, -1, -1):
                c = cardDeck.get(i)
                if c.rank != b.rank:
                    r.append(c)
            return 1, r
        if dl == 5:
            # ハイカード(ブタ)
            return 0, cls._getReverseMinCardList(cardDeck, 4)
        raise ValueError(f"不正なカード数: {dl}")

    @staticmethod
    def _getReverseMinCardList(cardDeck: CardDeck, min_: Literal[0, 1, 2, 3, 4] = 4) -> List[Card]:
        """
        カードリストを逆順にしたもの
        """
        r = []
        for i in range(min_, -1, -1):
            r.append(cardDeck.get(i))
        return r

    @classmethod
    def asyncBestHand(cls, trump: Trump, cardDeck: CardDeck, callback: Callable[[List[Literal[0, 1, 2, 3, 4]]], None]) -> None:
        """
        現在の手からの最善手の計算

        非同期バージョン
        (計算に非常に時間がかかるため)
        """
        asyncio.new_event_loop().run_in_executor(
            None,
            lambda: callback(cls.bestHand(trump, cardDeck))
        )

    @classmethod
    def bestHand(cls, trump: Trump, cardDeck: CardDeck) -> List[Literal[0, 1, 2, 3, 4]]:
        """
        現在の手からの最善手の計算
        """
        bestMax = 0
        bHand: Optional[CardDeck] = None

        cardList: List[str] = []
        for c in trump.cardList:
            cardList.append(c.judgeStr)

        cl = cardDeck.cardList

        start_time = time.perf_counter_ns()

        tcv = cl[4].judgeStr
        if tcv in cardList:
            cardList.remove(tcv)
        if "Joker" in cardList:
            cardList.remove("Joker")

        os_cpuCou = os.cpu_count()
        if os_cpuCou is None:
            os_cpuCou = 1
        elif os_cpuCou > 1:
            os_cpuCou -= 1

        _iters = list(combinations(cardList, 4))
        itLen = len(_iters)
        iters = []
        for v in range(0, itLen, itLen//os_cpuCou):
            iters.append(_iters[v:v+itLen//os_cpuCou])

        future_list = []
        with futures.ProcessPoolExecutor(max_workers=os_cpuCou) as executor:
            for iter_ in iters:
                future = executor.submit(
                    fn=cls._iterBestHand, trump=trump, cl=cl, co=iter_, tcv=tcv
                )
                future_list.append(future)
        fl = futures.as_completed(fs=future_list)
        for f in fl:
            r, cd = f.result()
            if r >= bestMax:
                bestMax = r
                bHand = cd

        if bHand is None:
            return []

        bHand.sort()

        # print(cardDeck, bHand)
        print(f"{(time.perf_counter_ns() - start_time)//1e6} ms")

        ret = []
        for i in range(5):
            f = True
            for n in bHand.cardList:
                if cl[i].judgeStr == n.judgeStr:
                    f = False
                    break
            if f:
                ret.append(i)
        return ret

    @classmethod
    def _iterBestHand(cls, trump: Trump, cl: List[Card], co, tcv: str) -> Tuple[int, Optional[CardDeck]]:
        """
        最善手の計算の並列計算用
        """
        bestMax = 0
        bHand: Optional[CardDeck] = None

        for v in co:
            s = set(v+(tcv, ))
            if len(s) != 5:
                continue
            cd = CardDeck(trump, [Card.convert(i) for i in s])
            j, h = cls.judgement(cd)
            if j <= 2:
                continue
            r = 5 - cls._checkHand(cl, cd.cardList)

            r = 100 - r * 20 + j
            if j <= 5:
                # ツーペア
                # スリーカード
                hr = h[2].rank
                if hr == 1 or hr == "Joker":
                    hr = 14
                r -= 14 - hr
            elif j == 12 or j == 13:
                # フォーカード
                hr = h[1].rank
                if hr == 1 or hr == "Joker":
                    hr = 14
                r -= 14 - hr

            if r >= bestMax:
                bestMax = r
                bHand = cd

        return bestMax, bHand

    @staticmethod
    def _checkHand(oHand: List[Card], nHand: List[Card]) -> int:
        """
        どれくらい現在の手に一致しているか
        """
        cou = 0
        for o in oHand:
            for n in nHand:
                if o.judgeStr == n.judgeStr:
                    cou += 1
                    break
        return cou
