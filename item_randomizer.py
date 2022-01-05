from typing import Tuple, Union
import requests
from bs4 import BeautifulSoup
import re
import random
import copy


class Magic_item:
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
    
    def __init__(self, properties: dict) -> None:
        self.properties = properties

    def __str__(self) -> str:
        item_str = ''
        for attrib in self.properties.keys():
            item_str += (f'{attrib}: {self.properties[attrib]}\n')
        for source in Magic_item.sources.keys():
            if source in item_str:
                item_str = item_str.replace(source, Magic_item.sources[source])
        item_str = item_str.split(': /')
        item_str = item_str[0] + ': http://dnd5e.wikidot.com/' + item_str[1][:-1]
        return item_str

    @staticmethod
    def random(amount: int = 1, **kwargs: Union[Tuple[str], str]) -> str:
        """kwargs may be Source, Rarity, Type, Attuned. Don't insert the kwarg means left it without any restriction
        enabling the randomizer to pick items with any value for the respective kwarg.
        """
        magic_items = Magic_item._get_items(kwargs, show_all=False, amount=amount)
        for magic_item in magic_items:
            yield magic_item

    @staticmethod
    def show_all(**kwargs: Union[Tuple[str], str]) -> str:
        magic_items = Magic_item._get_items(kwargs, show_all=True)
        for magic_item in magic_items:
            yield magic_item
    
    @staticmethod
    def _get_items(kwargs: dict, show_all, amount=1) -> list:
        _kwargs = copy.copy(kwargs)
        for kwarg in kwargs.keys():
            if len(kwargs[kwarg]) == 0:
                _kwargs.pop(kwarg)
        kwargs = _kwargs
        items = list(filter(lambda item: ([False for kwarg in kwargs.keys() if not item[kwarg] in kwargs[kwarg]] +\
            [True])[0], Magic_item.magic_items))
        if len(items) < 1:
            return "There's no items that fits the exigences."
        if not show_all:
            items = random.choices(items, k=amount)
        for item in items:
            yield item

    @staticmethod
    def source_help():
        source_help_str = ''
        for source in Magic_item.sources.keys():
            source_help_str += source + (10-len(source))*' ' + f'\t\t{Magic_item.sources[source]}\n\n'
        return source_help_str


if __name__ == '__main__':
    print(str(next(Magic_item.random())))
