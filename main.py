from PyQt5.QtCore import Qt
from design import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QScrollBar
import sys
import time


class Randomizer(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.all_rarities = [self.Common, self.Uncommon, self.Rare, self.Very_Rare, self.Legendary, self.Artifact,
            self.Unique, self.unknown]
        self.all_types = [self.Armor, self.Potion, self.Ring, self.Scroll, self.Staff, self.Wand, self.Weapon, self.Wondrous_Item]
        self.all_attunements = [self.attunement, self._attunement]
        self.randomize.clicked.connect(self.randomize_func)
        self.source_help.clicked.connect(self.source_help_func)
        self.amount_box.setMinimum(1)
        self.show_all.clicked.connect(self.show_all_func)
        self.setWindowTitle('5e Magic Items')
        self.text_scroll = QScrollBar()
        self.items_area.setVerticalScrollBar(self.text_scroll)
        self.items_on_display = []
        self.items_grid.setAlignment(Qt.AlignTop)
        
    def source_help_func(self):
        for i in reversed(range(self.items_grid.count())): 
            self.items_grid.itemAt(i).widget().setParent(None)
        source_help = QtWidgets.QTextBrowser()
        source_string = '## Source Books\n\n' + Magic_item.source_help()
        source_help.setMarkdown(source_string)
        self.items_grid.addWidget(source_help, 0, 0, 1 ,1)
        self.items_on_display.append(source_help)
        self.text_scroll.setValue(0)

    def _get_inputs(self):
        sources = []
        rarities = []
        types = []
        attunements = []
        for _source in self.source_grid.keys():
            if self.source_grid[_source].checkState() == 2:
                sources.append(self.source_grid[_source].text())
        for _rarity in self.all_rarities:
            if _rarity.checkState() == 2:
                rarities.append(_rarity.text())
        for _type in self.all_types:
            if _type.checkState() == 2:
                types.append(_type.text())
        for _attunement in self.all_attunements:
            if _attunement.checkState() == 2:
                attunements.append(_attunement.text())
        return sources, rarities, types, attunements

    def show_all_func(self):
        for i in reversed(range(self.items_grid.count())): 
            self.items_grid.itemAt(i).widget().setParent(None)
        self.items_on_display = []
        sources, rarities, types, attunements = self._get_inputs()
        j = 0
        n = 0
        for item in Magic_item.show_all(Source=sources, Rarity=rarities, Type=types, Attuned=attunements):
            item_display = Magic_item_browser(item, self.items_area_content)
            self.items_grid.addWidget(item_display, n, j, 1, 1)
            j = 1 if j == 0 else 0
            n += 1 if j == 0 else 0
            self.items_on_display.append(item_display)
        self.text_scroll.setValue(0)
        
    def randomize_func(self):
        for i in reversed(range(self.items_grid.count())): 
            self.items_grid.itemAt(i).widget().setParent(None)
        self.items_on_display = []
        sources, rarities, types, attunements = self._get_inputs()
        j = 0
        n = 0
        for item in Magic_item.random(self.amount_box.value(), Source=sources, Rarity=rarities, Type=types,
            Attuned=attunements):
            item_display = Magic_item_browser(item, self.items_area_content)
            self.items_grid.addWidget(item_display, n, j, 1, 1)
            j = 1 if j == 0 else 0
            n += 1 if j == 0 else 0
            self.items_on_display.append(item_display)
        self.text_scroll.setValue(0)


class Magic_item_browser(QtWidgets.QTextBrowser):
    def __init__(self, properties, content_area):
        super().__init__(content_area)
        self.properties = properties
        self.setFixedHeight(135)
        self.setMarkdown(str(self))
        self.setOpenExternalLinks(True)
        self.showing_description = False
        self.is_description_loaded = False
        self.description = None
        self.text_scroll = QScrollBar()
        self.setVerticalScrollBar(self.text_scroll)
        self.mouseDoubleClickEvent = lambda x: self.description_switch()

    def description_switch(self):
        if self.showing_description == False:
            if not self.is_description_loaded:
                html = BeautifulSoup(requests.get(
                    f"http://dnd5e.wikidot.com{self.properties['URL']}").text,
                    'html.parser'
                    )
                self.description = str(html.select('.page-title')[0]) + str(html.find(id='page-content'))\
                    .replace(str(html.find(id='page-content').select('.content-separator')[0]), '')\
                        .replace('\n\n', '\n')
                self.is_description_loaded = True
            self.setHtml(self.description)
            while self.text_scroll.maximum() != 0:
                self.setFixedHeight(self.height() + 1)
        else:
            self.setFixedHeight(135)
            self.setMarkdown(str(self))
        self.showing_description = not self.showing_description

    def __str__(self) -> str:
        item_str = f"[**{self.properties[list(self.properties.keys())[0]]}**]" +\
            "(http://dnd5e.wikidot.com{self.properties['URL']})\n\n"
        for attrib in list(self.properties.keys())[1:-1]:
            item_str += (f'**{attrib}:** {self.properties[attrib]}\n\n')
        for source in Magic_item.sources.keys():
            if source in item_str:
                item_str = item_str.replace(source, Magic_item.sources[source])
        return item_str


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    randomizer = Randomizer()
    randomizer.show()
    qt.exec_()
