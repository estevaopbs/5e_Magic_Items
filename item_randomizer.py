from typing import Tuple, Union
import requests
from bs4 import BeautifulSoup
import re
import random
import copy


class Magic_items:
    source_help = """
    AI	        Acquisitions Incorporated

    BG:DA	    Baldur's Gate: Descent into Avernus

    CM	        Candlekeep Mysteries

    CoS	        Curse of Strahd

    DC	        Divine Contention

    DMG	        Dungeon Master's Guide

    E:RLW	    Eberron: Rising from the Last War

    EGW	        Explorer's Guide to Wildemount

    FTD	        Fizban's Treasury of Dragons

    GGR	        Guildmaster's Guide to Ravnica

    GoS	        Ghosts of Saltmarsh

    ID:RF	    Icewind Dale: Rime of the Frostmaiden

    IMR	        Infernal Machine Rebuild

    LLK	        Lost Laboratory of Kwalish

    LMP	        Lost Mine of Phandelver

    MOT	        Mythic Odysseys of Theros

    OoA	        Out of the Abyss

    PoA	        Princes of the Apocalypse

    RoT	        The Rise of Tiamat

    SDW	        Sleeping Dragon's Wake

    SKT	        Storm King's Thunder

    TCE	        Tasha's Cauldron of Everything

    ToA	        Tomb of Annihilation

    ToD	        Tyranny of Dragons

    TYP	        Tales from the Yawning Portal

    VRGR	    Van Richten's Guide to Ravenloft

    VGM	        Volo's Guide to Monsters

    WDH	        Waterdeep - Dragon Heist

    WBW	        The Wild Beyond the Witchlight

    XGE	        Xanathar's Guide to Everything
    """
    html = BeautifulSoup(requests.get('http://dnd5e.wikidot.com/wondrous-items').text, 'html.parser')
    sources = {_source.split('\n')[0]: _source.split('\n')[1] for _source in re.findall('.+\n.+',
        html.select('.wiki-content-table')[0].text)}
    rarities = []
    for rarity in html.select('.yui-nav')[0].text.split('\n'):
        rarities.append(rarity)
    while '' in rarities: rarities.remove('')
    rarities = {rarity: n for n, rarity in enumerate(rarities)}
    magic_items = []
    for rarity in rarities.keys():
        rarity_table = html.find(id=f'wiki-tab-0-{rarities[rarity]}')
        attribs = rarity_table.find('tr').text.split('\n')
        while('') in attribs: attribs.remove('')
        for item in rarity_table.find_all('tr')[1:]:
            item_attribs = item.text.split('\n')
            while('') in item_attribs: item_attribs.remove('')
            item_dict = {attrib: item_attrib for attrib, item_attrib in zip(attribs, item_attribs)}
            item_dict.update({'Rarity': rarity})
            item_dict.update({'URL': item.find('a').get('href')})
            magic_items.append(item_dict)

    @staticmethod
    def random(amount: int = 1, **kwargs: Union[Tuple[str], str]) -> str:
        """kwargs may be Source, Rarity, Type, Attuned. Don't insert the kwarg means left it without any restriction
        enabling the randomizer to pick items with any value for the respective kwarg.
        """
        return Magic_items._get_items(kwargs, show_all=False, amount=amount)

    @staticmethod
    def show_all(**kwargs: Union[Tuple[str], str]) -> str:
        return Magic_items._get_items(kwargs, show_all=True)
    
    @staticmethod
    def _get_items(kwargs: dict, show_all, amount=1) -> list:
        _kwargs = copy.copy(kwargs)
        for kwarg in kwargs.keys():
            if len(kwargs[kwarg]) == 0:
                _kwargs.pop(kwarg)
        kwargs = _kwargs
        items = list(filter(lambda item: ([False for kwarg in kwargs.keys() if not item[kwarg] in kwargs[kwarg]] +\
            [True])[0], Magic_items.magic_items))
        if len(items) < 1:
            return "There's no items that fits the exigences."
        if not show_all:
            items = random.choices(items, k=amount)
        items_str = ''
        for item in items:
            item_str = ''
            for attrib in item.keys():
                item_str += (f'{attrib}: {item[attrib]}\n')
            for source in Magic_items.sources.keys():
                if source in item_str:
                    item_str = item_str.replace(source, Magic_items.sources[source])
            item_str = item_str.split(': /')
            item_str = item_str[0] + ': http://dnd5e.wikidot.com/' + item_str[1] + '\n'
            items_str += item_str
        return items_str


if __name__ == '__main__':
    print(Magic_items.random())
