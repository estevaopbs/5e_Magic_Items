import enum
import requests
from bs4 import BeautifulSoup
import re
import json


def import_items():
    html = BeautifulSoup(requests.get('http://dnd5e.wikidot.com/wondrous-items').text, 'html.parser')
    sources = {_source.split('\n')[0]: _source.split('\n')[1] for _source in re.findall('.+\n.+',
        html.select('.wiki-content-table')[0].text)}
    rarities = [rarity for rarity in html.select('.yui-nav')[0].text.split('\n') if rarity != '']
    magic_items = dict()
    for n, rarity in enumerate(rarities):
        rarity_table = html.find(id=f'wiki-tab-0-{n}')
        attribs = [attrib for attrib in rarity_table.find('tr').text.split('\n') if attrib != '']
        for item in rarity_table.find_all('tr')[1:]:
            item_attribs = [item_attrib for item_attrib in item.text.split('\n') if item_attrib != '']
            item_dict = {attrib: item_attrib for attrib, item_attrib in zip(attribs, item_attribs)}
            if item_dict['Attuned'] == 'Attuned':
                item_dict['Attuned'] = True
            else:
                item_dict['Attuned'] = False
            for k, v in sources.items():
                item_dict['Source'] = item_dict['Source'].replace(k, v)
            item_dict.update({'Rarity': rarity})
            item_html = BeautifulSoup(requests.get(
                f"http://dnd5e.wikidot.com{item.find('a').get('href')}").text,
                'html.parser'
                )
            item_dict.update({'HTML': str(item_html.select('.page-title')[0]) + str(item_html.find(id='page-content'))\
                    .replace(str(item_html.find(id='page-content').select('.content-separator')[0]), '')\
                        .replace('\n\n', '\n')})
            item_dict['HTML'] = item_dict['HTML'].replace('<span>', '<h2>').replace('</span>', '</h2>')
            item_dict['HTML'] = re.sub('<a href=.*>', '', item_dict['HTML']).replace('</a>', '')
            item_label = item_dict[list(item_dict.keys())[0]]
            item_dict.pop(list(item_dict.keys())[0])
            magic_items.update({item_label: item_dict})
            print(item_label)
    with open('magic_items.json', 'w') as file:
        json.dump(magic_items, file, indent=4)


def import_spells():
    html = BeautifulSoup(requests.get('http://dnd5e.wikidot.com/spells').text, 'html.parser')
    levels = [level for level in html.select('.yui-nav')[0].text.split('\n') if level != '']
    spells = dict()
    for n, level in enumerate(levels):
        level_table = html.find(id=f'wiki-tab-0-{n}')
        attribs = [attrib for attrib in level_table.find('tr').text.split('\n') if attrib != '']
        for spell in level_table.find_all('tr')[1:]:
            spell_attribs = [spell_attrib for spell_attrib in spell.text.split('\n') if spell_attrib != '']
            if '(HB)' in spell_attribs[0] or '(UA)' in spell_attribs[0]:
                continue
            spell_dict = {attrib: spell_attrib for attrib, spell_attrib in zip(attribs, spell_attribs)}
            spell_dict.update({'Level': level})
            if spell_dict['Casting Time'][-1] == 'R':
                spell_dict.update({'Ritual': True})
                spell_dict['Casting Time'] = spell_dict['Casting Time'][:-2]
            else:
                spell_dict.update({'Ritual': False})
            if 'Concentration' in spell_dict['Duration'].split(' ')[0]:
                spell_dict.update({'Concentration': True})
                spell_dict['Duration'] = ' '.join(spell_dict['Duration'].split(' ')[1:])
            else:
                spell_dict.update({'Concentration': False})
            if spell_dict['School'].split(' ')[-1] == 'D':
                spell_dict['School'] = spell_dict['School'].split(' ')[0]
                spell_dict.update({'Special': 'Dunamancy'})
            elif spell_dict['School'].split(' ')[-1] == 'DG':
                spell_dict['School'] = spell_dict['School'].split(' ')[0]
                spell_dict.update({'Special': 'Dunamancy: Graviturgy'})
            elif spell_dict['School'].split(' ')[-1] == 'DC':
                spell_dict['School'] = spell_dict['School'].split(' ')[0]
                spell_dict.update({'Special': 'Dunamancy: Chronurgy'})
            else:
                spell_dict.update({'Special': ''})
            url = 'http://dnd5e.wikidot.com' + spell.find('a').get('href')
            spell_html = BeautifulSoup(requests.get(url).text, 'html.parser')
            spell_dict.update({'HTML': str(spell_html.select('.page-title')[0]) +\
                str(spell_html.find(id='page-content')).replace(str(spell_html.find(id='page-content').\
                    select('.content-separator')[0]), '').replace('\n\n', '\n')})
            for p in spell_html.find(id='page-content').findAll('p'):
                if '(UA)' in str(p) or '(HB)' in str(p):
                    spell_dict['HTML'] = spell_dict['HTML'].replace(str(p), '')
            for a in spell_html.find(id='page-content').findAll('p')[-1].findAll('a'):
                spell_dict['HTML'] = spell_dict['HTML'].replace(str(a), a.text)
            spell_dict['HTML'] = spell_dict['HTML'].replace('\n\n', '\n').replace('Spell Lists: ', 'Spell Lists. ')
            spell_dict['HTML'] = spell_dict['HTML'].replace('<span>', '<h2>').replace('</span>', '</h2>')
            spell_dict['HTML'] = re.sub('<a href=.*>', '', spell_dict['HTML']).replace('</a>', '')
            if spell_dict[list(spell_dict.keys())[0]] != 'Ceremony':
                spell_dict.update({'Source': spell_html.find(id='page-content').find('p').text.split(': ')[1]})
            else:
                spell_dict.update({'Source': "Xanathar's Guide to Everything"})
            if spell_dict['Special'] == '':
                spell_dict.update({'Spell Lists': ' '.join(spell_html.find(id='page-content').\
                    findAll('p')[-1].text.split(' ')[2:])})
            else:
                spell_dict.update({'Spell Lists': ' '.join(spell_html.find(id='page-content').\
                    findAll('p')[-1].text.split(' ')[2:-1])})
            spell_label = spell_dict[list(spell_dict.keys())[0]]
            spell_dict.pop(list(spell_dict.keys())[0])
            spells.update({spell_label: spell_dict})
            print(spell_label)
    with open('spells.json', 'w') as file:
        json.dump(spells, file, indent=4)


def import_creatures():
    n = 1
    creatures = dict()
    while True:
        html = BeautifulSoup(requests.get(f'https://www.dndwiki.io/monsters?227df1c3_page={n}').text, 'html.parser')
        if html.select('.collection-list-wrapper')[0].text == 'No items found.Previous':
            break
        for creature_url in ['https://www.dndwiki.io' + creature.find('a').get('href') for creature in\
            html.select('.container-list-menu')[0].select('.list-menu-item')]:
            creature_html = BeautifulSoup(requests.get(creature_url).text, 'html.parser')
            creature_dict = dict()
            creature_label = creature_html.select('.entry-heading')[0].text
            creature_dict.update({'Size': creature_html.select('.entry-metadata-label')[0].text.split(' ')[0]})
            creature_dict.update({'Type': creature_html.select('.entry-metadata-label')[0].text.split(' ')[1]})
            creature_dict.update({'Alignment': creature_html.select('.entry-metadata-label')[2].text})
            creature_dict.update({'Armor Class': creature_html.select('.entry-metadata-label')[4].text})
            creature_dict.update({'Hit Points': creature_html.select('.entry-metalabel-content')[0].text})
            creature_dict.update({'Speed': creature_html.select('.entry-metalabel-content')[1].text})
            creature_dict.update({'Stats': {stat.select('.entry-metadata-label')[0].text: stat.select\
                ('.entry-metalabel-content')[0].text for stat in creature_html.select('.monster-stat-entry')}})
            creature_dict.update({'Saving Throws': creature_html.select('.container-entry')[0]\
                .select('.entry-metadata')[4].select('.entry-metadata-label')[1].text})
            creature_dict.update({'Skills': creature_html.select('.container-entry')[0].select('.entry-metadata')[5]\
                .select('.entry-metadata-label')[1].text})
            creature_dict.update({'Damage Vulnerabilities': creature_html.select('.container-entry')[0]\
                .select('.entry-metadata')[6].select('.entry-metadata-label')[1].text})
            creature_dict.update({'Damage Resistances': creature_html.select('.container-entry')[0]\
                .select('.entry-metadata')[7].select('.entry-metadata-label')[1].text})
            creature_dict.update({'Damage Immunities': creature_html.select('.container-entry')[0]\
                .select('.entry-metadata')[8].select('.entry-metadata-label')[1].text})
            creature_dict.update({'Condition Immunities': creature_html.select('.container-entry')[0]\
                .select('.entry-metadata')[9].select('.entry-metadata-label')[1].text})
            creature_dict.update({'Senses': creature_html.select('.container-entry')[0]\
                .select('.entry-metadata')[10].select('.entry-metadata-label')[1].text})
            creature_dict.update({'Languages': creature_html.select('.container-entry')[0]\
                .select('.entry-metadata')[11].select('.entry-metadata-label')[1].text})
            creature_dict.update({'Challenge': creature_html.select('.container-entry')[0]\
                .select('.entry-metadata')[12].select('.entry-metadata-label')[1].text})
            print(creature_dict)
            break
        break
        n+=1
        

if __name__ == '__main__':
    #import_items()
    #import_spells()
    import_creatures()
