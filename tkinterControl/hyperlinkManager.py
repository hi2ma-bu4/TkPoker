# coding: utf-8
"""
tkinterのtext Widgetのハイパーリンクをハイライトする
"""

import webbrowser


class HyperlinkManager:

    def __init__(self, text) -> None:

        self.text = text

        self.text.tag_config("hyper", foreground="blue", underline=1)

        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Control-Button-1>", self._click)

        self.reset()

    def reset(self) -> None:
        self.links = {}

    def add(self, urls: str):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = urls
        return [urls, ("hyper", tag)]

    def _enter(self, event) -> None:
        self.text.config(cursor="hand2")

    def _leave(self, event) -> None:
        self.text.config(cursor="")

    def _click(self, event) -> None:
        for tag in self.text.tag_names("current"):
            if tag[:6] == "hyper-":
                webbrowser.open(self.links[tag])
                return
