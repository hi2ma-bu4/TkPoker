# coding: utf-8
"""
tkinterのimageを簡単に操作出来るようにしたやつ
"""


from typing import Dict, Tuple, Union, Optional, Literal
from tkinter import PhotoImage
from PIL import Image, ImageTk
from lib.calc2d import Vector2, ta_pos


# type aliases
ta_imageTk = Union[ImageTk.PhotoImage, PhotoImage]

ta_resample_num = Literal[0, 1, 2, 3, 4, 5]
ta_resample_type = Literal[
    "nearest", "lanczos", "bilinear", "bicubic",
    "box", "hamming"]
# ここまで


class _Tkc_Photo:
    """
    photo管理クラス
    """

    def __init__(self) -> None:
        self.imageDict: Dict[str, Image.Image] = {}
        self.imageTkDict: Dict[str, Optional[ta_imageTk]] = {}

    def __str__(self) -> str:
        itc = 0
        for v in self.imageTkDict.values():
            if v is not None:
                itc += 1
        return f"<image: {len(self.imageDict)}, imageTk: {itc}>"

    def __len__(self) -> int:
        return len(self.imageDict)

    def add(self, name: str, url: str) -> Image.Image:
        """
        画像を追加する
        """
        image = Image.open(url)
        self.imageDict[name] = image
        self.imageTkDict[name] = None
        return image

    def getImage(self, name: str) -> Optional[Image.Image]:
        """
        画像を取得する
        """
        if name not in self.imageDict:
            return None
        return self.imageDict[name]

    def getImageTk(self, names: Union[str, Image.Image, ta_imageTk]) -> ta_imageTk:
        """
        tkinter用の画像を取得する
        (自動変換)
        """
        if isinstance(names, str):
            if names in self.imageTkDict:
                im = self.imageTkDict[names]
                if im is not None:
                    return im
            if names in self.imageDict:
                im = ImageTk.PhotoImage(self.imageDict[names])
                self.imageTkDict[names] = im
                return im
            raise ValueError(f"名前「{names}」の画像が見つかりません")
        if isinstance(names, Image.Image):
            im = ImageTk.PhotoImage(names)
            return im
        if isinstance(names, ta_imageTk):
            return names
        raise ValueError("不明な引数の型")

    def updateImage(self, name: str, image: Image.Image) -> Image.Image:
        """
        画像を更新する
        """
        im = self.getImage(name)
        if im is None:
            raise ValueError(f"名前「{name}」の画像が見つかりません")
        im = image
        self.imageDict[name] = im
        self.imageTkDict[name] = None
        return im

    def updateImageTk(self, name: str) -> ImageTk.PhotoImage:
        """
        tkinter用の画像を更新する
        (強制更新)
        """
        im = self.getImage(name)
        if im is None:
            raise ValueError(f"名前「{name}」の画像が見つかりません")
        imt = ImageTk.PhotoImage(im)
        self.imageTkDict[name] = imt
        return imt

    def copy(self, name: str, newName: str) -> Image.Image:
        """
        画像objをコピーする
        """
        im = self.getImage(name)
        if im is None:
            raise ValueError(f"名前「{name}」の画像が見つかりません")
        if newName in self.imageDict:
            raise ValueError(f"名前「{newName}」の画像は既に存在します")
        nim = im.copy()
        self.imageDict[newName] = nim
        self.imageTkDict[newName] = None
        return nim

    def delete(self, name: str) -> None:
        """
        画像を削除する
        """
        if name in self.imageDict:
            del self.imageDict[name]
        if name in self.imageTkDict:
            del self.imageTkDict[name]

    def resize(
            self, name: str, size: Tuple[int, int],
            resample: Union[ta_resample_num, ta_resample_type] = 0,
            reducing_gap: float = 2.0) -> Image.Image:
        """
        画像のサイズを変更する
        (指定のサイズにリサイズする)
        """
        im = self.getImage(name)
        if im is None:
            raise ValueError(f"名前「{name}」の画像が見つかりません")

        if isinstance(resample, str):
            resample = self._resample(resample)

        im = im.resize(size, resample=resample, reducing_gap=reducing_gap)
        return self.updateImage(name, im)

    def thumbnail(
        self, name: str, size: Tuple[int, int],
        resample: Union[ta_resample_num, ta_resample_type] = 0,
        reducing_gap: float = 2.0
    ) -> Image.Image:
        """
        画像のサイズを変更する
        (アスペクト比を保ってサイズを変更する)
        """
        im = self.getImage(name)
        if im is None:
            raise ValueError(f"名前「{name}」の画像が見つかりません")

        if isinstance(resample, str):
            resample = self._resample(resample)

        im.thumbnail(size, resample=resample, reducing_gap=reducing_gap)
        return self.updateImage(name, im)

    def zoom(
            self, name: str, zoom: Tuple[float, float],
            resample: Union[ta_resample_num, ta_resample_type] = 0,
            reducing_gap: float = 2.0) -> Image.Image:
        """
        画像のサイズを変更する
        (指定の倍率に拡大縮小する)
        """
        im = self.getImage(name)
        if im is None:
            raise ValueError(f"名前「{name}」の画像が見つかりません")

        if isinstance(resample, str):
            resample = self._resample(resample)

        im = im.resize(
            (int(im.width * zoom[0]), int(im.height * zoom[1])),
            resample=resample, reducing_gap=reducing_gap
        )
        return self.updateImage(name, im)

    def crop(
            self, name: str, pos: ta_pos, size: ta_pos,
    ) -> Image.Image:
        """
        画像のトリミング
        """
        im = self.getImage(name)
        if im is None:
            raise ValueError(f"名前「{name}」の画像が見つかりません")

        p = Vector2.convert(pos)
        s = Vector2.convert(size)

        im = im.crop((p.x, p.y, p.x + s.x, p.y + s.y))
        return self.updateImage(name, im)

    def _resample(self, resample: ta_resample_type) -> ta_resample_num:
        ret = 0
        if resample == "nearest":
            ret = Image.NEAREST
        elif resample == "lanczos":
            ret = Image.LANCZOS
        elif resample == "bilinear":
            ret = Image.BILINEAR
        elif resample == "bicubic":
            ret = Image.BICUBIC
        elif resample == "box":
            ret = Image.BOX
        elif resample == "hamming":
            ret = Image.HAMMING
        else:
            raise ValueError("不明なresample")
        return ret
