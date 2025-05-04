# coding: utf-8

from typing import List
import os
import random as rnd

from tkinterControl import Tkc
from lib.trump import Trump, Poker
from lib.calc2d import Vector2

IMG_PATH = "img/"


def main() -> None:

    trump = Trump(1)

    # 本体
    tkc = Tkc(
        title="ポーカー(ファイブカードドロー)",
        windowSize=(600, 300),
        windowPos=(0, 0)
    )
    tkc.windowDpiAutoSet()
    tkc.fullscreen()

    tkc.createFont("card", "メイリオ", 8, "bold")

    # ==================================================
    # リソース読み込み
    cardSize = (712//5, 1008//5)  # (712, 1008)
    for s in "shdc":
        tkc.img.add(s, f"{IMG_PATH}{s}.png")
        for r in range(1, 14):
            n = f"{s}{r}"
            tkc.img.add(n, f"{IMG_PATH}{s}{r}.png")
            tkc.img.thumbnail(n, cardSize, 3)
    tkc.img.add("Joker", f"{IMG_PATH}joker.png")
    tkc.img.thumbnail("Joker", cardSize, 3)
    tkc.img.add("back", f"{IMG_PATH}card_back.png")
    tkc.img.thumbnail("back", cardSize, 3)

    tkc.img.add("決定", f"{IMG_PATH}決定.png")

    # ==================================================
    # キーバインド

    tkc.bind("<Escape>", tkc.drawEnd)

    # ==================================================
    # Widget設置

    tkc.fra.gridConfigure("row", 0)
    tkc.fra.gridConfigure("column", 0)

    canvas = tkc.wid.addCanvas(
        row=0, column=0, sticky="nsew", bg="green"
    )

    # ==================================================
    # ターン処理

    pad = 10

    diffX = tkc.winMaxX//2 - ((cardSize[0]+pad)*5-pad)//2

    playBasePos = Vector2(diffX, tkc.winMaxY-cardSize[1]-5)
    cpBasePos = Vector2(diffX, 5)

    class g:
        isNotClick = True
        animTurn = False

        loopCou = 0
        loopMax = 2  # カード交換回数

        playAnim = False
        playAminCou = 0

        plData = []
        cpuData = []
        animRateProgression = 0
        cpCalcWait = False

        vd: tuple = (0,)*3

    def init() -> None:
        trump.shuffle()
        trump.distribute(2, 5)

        for d in trump.deckList:
            d.sort()

        g.cpCalcWait = True
        Poker.asyncBestHand(trump, trump.deckList[1], abh)

        initDraw()
        g.isNotClick = False
        g.playAnim = False

        g.loopCou = 0

        g.animRateProgression = 0

    def turn() -> None:

        drawTurn()
        if not g.playAnim:
            g.playAminCou = 0
            if g.animTurn:
                tkc.after(200, turn)
            else:
                g.isNotClick = False
                g.animRateProgression = 0

    # ==================================================
    # canvas描画

    def initDraw() -> None:
        canvas.clear()

        # 自分描画
        for i, c in enumerate(trump.deckList[0].cardList):
            canvas.drawImage(
                c.judgeStr,
                playBasePos+((cardSize[0]+pad)*i, 0),
                name=c.judgeStr
            )

        # 相手描画
        for i in range(5):
            canvas.drawImage(
                "back",
                cpBasePos+((cardSize[0]+pad)*i, 0),
                name=f"back{i}"
            )

        # 山札描画
        for i in range(10):
            canvas.drawImage(
                "back",
                (
                    tkc.winMaxX-cardSize[0]-20,
                    tkc.winMaxY//2-cardSize[1]//2-(i-5)*5
                ),
                name=f"mountain{i}"
            )

        # ui表示
        canvas.drawImage(
            "決定",
            playBasePos+((cardSize[0]+pad)*5+10, cardSize[1]-50),
            name="決定ボタン"
        )

    def drawTurn() -> None:

        if g.animRateProgression == 0:
            g.animRateProgression = 1
        elif g.animRateProgression == 1:
            # cpuの出す手を決定
            cpuCalc(0)
        elif g.animRateProgression == 2:
            # cpuの出すカード開示
            cpuCalc(1)
        elif g.animRateProgression == 3:
            # 自分の出すカードを捨てる
            for l in g.plData:
                if l[1].getPos().y == playBasePos.y - 20:
                    l[1].setPos(
                        (
                            tkc.winMaxX//2-cardSize[0]//2 +
                            rnd.randint(-10, 10)*10,
                            tkc.winMaxY//2-cardSize[1]//2+rnd.randint(-3, 3)*10
                        )
                    )
                    return
            g.animRateProgression = 4
        elif g.animRateProgression == 4:
            # cpuの出すカードを捨てる
            cpuCalc(2)
        elif g.animRateProgression == 5:
            # 自分のカードを補充
            for l in g.plData:
                if l[1].getPos().y != playBasePos.y:
                    c = trump.throwDeck.pop(0)
                    trump.deckList[0].remove(l[1].name)
                    trump.deckList[0].add(c)
                    l[1] = canvas.drawImage(
                        c.judgeStr,
                        playBasePos+((cardSize[0]+pad)*l[0], 0),
                        name=c.judgeStr
                    )
                    return
            g.plData = []
            g.animRateProgression = 6
        elif g.animRateProgression == 6:
            # cpuのカードを補充
            cpuCalc(3)
        elif g.animRateProgression == 7:
            # 並べ替え
            trump.deckList[0].sort()
            trump.deckList[1].sort()
            g.animRateProgression = 8
        elif g.animRateProgression == 8:
            # 自分のカードの表示(順番)を更新
            for i, c in enumerate(trump.deckList[0].cardList):
                item = canvas.getItem(c.judgeStr)
                if item is not None:
                    item.setPos(
                        playBasePos+((cardSize[0]+pad)*i, 0),
                    )
            g.animRateProgression = 9
        elif g.animRateProgression == 9:
            # カード入れ替えを複数回使用する場合はここに書く
            g.loopCou += 1
            if g.loopCou < g.loopMax:
                g.animTurn = False
                g.cpCalcWait = True
                Poker.asyncBestHand(trump, trump.deckList[1], abh)
                return
            g.loopCou = 0
            g.animRateProgression = 10
        elif g.animRateProgression == 10:
            # cpuのカード公開(手の開示)
            cpuCalc(4)
            # 勝敗判定
            g.vd = Poker.confrontation(
                trump.deckList[0],
                trump.deckList[1],
            )
            g.animRateProgression = 11
        elif g.animRateProgression == 11:
            playAnim()
            g.animRateProgression = 12
        elif g.animRateProgression == 12:
            init()
            g.animTurn = False

    def playAnim() -> None:
        if g.playAminCou == 0:
            g.playAnim = True

            # プレイヤー役表示
            d = Poker.get_trans(g.vd[1])
            canvas.drawSquare(
                (
                    0, tkc.winMaxY-cardSize[1] - 150
                ),
                (tkc.winMaxX+100, 100), "black",
                name="plBack"
            )
            canvas.drawText(
                d[0],
                ("MSゴシック体", 40),
                (tkc.winMaxX-100, tkc.winMaxY-cardSize[1]-150),
                "ne",
                "white",
                name="plTrans1"
            )
            canvas.drawText(
                d[1],
                ("MSゴシック体", 20),
                (tkc.winMaxX-100, tkc.winMaxY-cardSize[1]-90),
                "ne",
                "#8f8f8f",
                name="plTrans2"
            )
            # cpu役表示
            d = Poker.get_trans(g.vd[2])
            canvas.drawSquare(
                (0, cardSize[1]+50), (tkc.winMaxX+100, 100), "black",
                name="cpBack"
            )
            canvas.drawText(
                d[0],
                ("MSゴシック体", 40),
                (tkc.winMaxX//2, cardSize[1]+50),
                "ne",
                "white",
                name="cpTrans1"
            )
            canvas.drawText(
                d[1],
                ("MSゴシック体", 20),
                (tkc.winMaxX//2, cardSize[1]+110),
                "ne",
                "#8f8f8f",
                name="cpTrans2"
            )

            # 勝敗
            v = Vector2()
            if g.vd[0] == 1:
                v.x = tkc.winMaxX//2-100
                v.y = tkc.winMaxY-cardSize[1]-150
            elif g.vd[0] == -1:
                v.x = tkc.winMaxX-100
                v.y = cardSize[1]+50

            if g.vd[0] != 0:
                canvas.drawText(
                    "勝ち！",
                    ("MSゴシック体", 40),
                    v,
                    "ne",
                    "red",
                    name="win"
                )
        elif g.playAminCou > 35:
            t = canvas.getItem("plTrans1")
            if t is not None:
                t.destroy()
            t = canvas.getItem("plTrans2")
            if t is not None:
                t.destroy()
            t = canvas.getItem("plBack")
            if t is not None:
                t.destroy()
            t = canvas.getItem("cpTrans1")
            if t is not None:
                t.destroy()
            t = canvas.getItem("cpTrans2")
            if t is not None:
                t.destroy()
            t = canvas.getItem("cpBack")
            if t is not None:
                t.destroy()
            t = canvas.getItem("win")
            if t is not None:
                t.destroy()
            g.playAnim = False
            g.playAminCou = 0

        if g.playAnim:
            g.playAminCou += 1
            tkc.after(100, playAnim)
        else:
            turn()

    # ==================================================
    # cpuカード計算

    def cpuCalc(type_: int = 0) -> None:
        if type_ == 0:
            # bestHandの跡地
            g.animRateProgression = 2
        elif type_ == 1:
            for i in range(5):
                for j, cp in enumerate(g.cpuData):
                    if i == cp[0]:
                        c = canvas.getItem(f"back{i}")
                        if c is None:
                            break
                        if c.getPos().y == cpBasePos.y:
                            n = trump.deckList[1].get(i)
                            g.cpuData[j].append(
                                canvas.drawImage(
                                    n.judgeStr,
                                    c.getPos()+(0, 20),
                                    name=n.judgeStr
                                ))
                            c.destroy()
                            return
                        break
            g.animRateProgression = 3
        elif type_ == 2:
            for l in g.cpuData:
                if l[1].getPos().y == cpBasePos.y + 20:
                    l[1].setPos(
                        (
                            tkc.winMaxX//2-cardSize[0]//2 +
                            rnd.randint(-10, 10)*10,
                            tkc.winMaxY//2-cardSize[1]//2+rnd.randint(-3, 3)*10
                        )
                    )
                    return
            g.animRateProgression = 5
        elif type_ == 3:
            for l in g.cpuData:
                if l[1].getPos().y != cpBasePos.y:
                    c = trump.throwDeck.pop(0)
                    trump.deckList[1].remove(l[1].name)
                    trump.deckList[1].add(c)
                    l[1] = canvas.drawImage(
                        "back",
                        cpBasePos+((cardSize[0]+pad)*l[0], 0),
                        name=f"back{l[0]}"
                    )
                    return
            g.cpuData = []
            g.animRateProgression = 7
        elif type_ == 4:
            for i in range(5):
                c = canvas.getItem(f"back{i}")
                if c is None:
                    continue
                n = trump.deckList[1].get(i)
                canvas.drawImage(
                    n.judgeStr,
                    c.getPos()+(0, 20),
                    name=n.judgeStr
                )
                c.destroy()
            g.animRateProgression = 11

    def abh(t) -> None:
        for v in t:
            g.cpuData.append([v])
        g.cpCalcWait = False

    # ==================================================
    # イベント

    def en(event=None) -> None:
        if g.isNotClick:
            return
        if g.cpCalcWait:
            tkc.msgbox.show("info", "まだcpuが手を決定していません", "poker")
            return
        g.isNotClick = True
        g.animTurn = True

        for i in range(len(g.plData)):
            n = g.plData[i]
            c = canvas.getItem(n)
            if c is None:
                raise RuntimeError(f"不明なカード {n}")
            g.plData[i] = [trump.deckList[0].getIndex(n), c]
        g.plData.sort()

        turn()

    def nu(ind: int):
        def func(e=None):
            c = canvas.getItem(trump.deckList[0].get(ind).judgeStr)
            if c is None:
                print("カードが見つかりませんでした")
                return
            mo(
                c
            )
        return func

    def mo(cur: Tkc.Tkc_Canvas.CanvasItem):
        g.isNotClick = True
        if cur.getPos().y == playBasePos.y:
            cur.move((0, -20))
            g.plData.append(cur.name)
        else:
            cur.move((0, 20))
            g.plData.remove(cur.name)

        turn()

    def ce(event: Tkc.tk.Event, x: int, y: int, cur: Tkc.Tkc_Canvas.CanvasItem, lst: List[Tkc.Tkc_Canvas.CanvasItem]) -> None:
        # クリックイベント
        if cur is None:
            return
        if g.isNotClick:
            return

        if trump.deckList[0].getIndex(cur.name) == -1:
            if cur.name != "決定ボタン":
                return

        if cur.name == "決定ボタン":
            en()
        else:
            mo(cur)

    # ==================================================
    tkc.bind("<Return>", en)
    tkc.bind("<Key-1>", nu(0))
    tkc.bind("<Key-2>", nu(1))
    tkc.bind("<Key-3>", nu(2))
    tkc.bind("<Key-4>", nu(3))
    tkc.bind("<Key-5>", nu(4))
    canvas.getClickEvent(ce)

    init()
    tkc.drawStart()


if __name__ == "__main__":
    # カレントディレクトリ修正
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    main()
