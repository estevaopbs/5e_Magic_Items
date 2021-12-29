from item_randomizer import *
from design import *
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys


class Randomizer(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.all_sources = [self.AI, self.BGDA, self.CM, self.CoS, self.DC, self.DMG, self.ERLW, self.EGW, self.FTD,
            self.GGR, self.GoS, self.IDRF, self.IMR, self.LLK, self.LMP, self.MOT, self.OoA, self.PoA, self.RoT,
            self.SDW, self.SKT, self.TCE, self.ToA, self.ToD, self.TYP, self.VRGR, self.VGM, self.WDH, self.WBW,
            self.XGE]
        self.all_rarities = [self.Common, self.Uncommon, self.Rare, self.Very_Rare, self.Legendary, self.Artifact,
            self.Unique, self.unkown]
        self.all_types = [self.Armor, self.Potion, self.Ring, self.Scroll, self.Staff, self.Wand, self.Weapon]
        self.all_attunements = [self.attunement, self._attunement]
        self.randomize.clicked.connect(self.randomize_func)
        self.source_help.clicked.connect(self.source_help_func)
        self.amount_box.setMinimum(1)
        self.show_all.clicked.connect(self.show_all_func)
        self.setWindowTitle('Uber Item')
        self.textBrowser.setOpenExternalLinks(True)

    def source_help_func(self):
        self.textBrowser.setText(Magic_items.source_help)

    def show_all_func(self):
        sources = []
        rarities = []
        types = []
        attunements = []
        for _source in self.all_sources:
            if _source.checkState() == 2:
                sources.append(_source.text())
        for _rarity in self.all_rarities:
            if _rarity.checkState() == 2:
                rarities.append(_rarity.text())
        for _type in self.all_types:
            if _type.checkState() == 2:
                types.append(_type.text())
        for _attunement in self.all_attunements:
            if _attunement.checkState() == 2:
                attunements.append(_attunement.text())
        items_str = Magic_items.show_all(Source=sources, Rarity=rarities, Type=types, Attuned=attunements)
        self.textBrowser.setText(items_str)

    def randomize_func(self):
        sources = []
        rarities = []
        types = []
        attunements = []
        for _source in self.all_sources:
            if _source.checkState() == 2:
                sources.append(_source.text())
        for _rarity in self.all_rarities:
            if _rarity.checkState() == 2:
                rarities.append(_rarity.text())
        for _type in self.all_types:
            if _type.checkState() == 2:
                types.append(_type.text())
        for _attunement in self.all_attunements:
            if _attunement.checkState() == 2:
                attunements.append(_attunement.text())
        items_str = Magic_items.random(self.amount_box.value(), Source=sources, Rarity=rarities, Type=types,
            Attuned=attunements)
        self.textBrowser.setText(items_str)


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    randomizer = Randomizer()
    randomizer.show()
    qt.exec_()
