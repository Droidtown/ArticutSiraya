#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re

class XP:
    """
    一個最基本的 XP 會有的參數。
    """
    def __init__(self):
        self.headFirst = True

class OBL(XP):
    """
    OBL-case 繼承 XP 的結構，設為一 headFirst 參數的節點。
    """
    def __init__(self):
        self.TagSTR = "OBL"
        return None

class ArticutSiraya:
    def __init__(self):
        self.inputSTR = None
        self.tagDICT = {}
        self.OBL = OBL()
        self.OBLpat = re.compile(r"\bki\b", re.IGNORECASE)
        return None

    def oblMarker(self):
        self.tagDICT = {"TAG":self.OBL.TagSTR}
        return re.sub(self.OBLpat, "<{TAG}>ki</{TAG}>".format(**self.tagDICT), self.inputSTR)

    def parse(self, inputSTR, level="lv1"):
        self.inputSTR = inputSTR
        self.inputSTR = self.oblMarker()
        return self.inputSTR

if __name__ == "__main__":
    inputSTR = "Sulat ki kavuilan ti Jesus Christus"
    siraya = ArticutSiraya()
    resultDICT = siraya.parse(inputSTR)
    print(resultDICT)