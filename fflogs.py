import os
import json
import sys
from prettytable import PrettyTable
import requests
import numpy as np
import datetime
from dummy import DummyData

FFLOGS_BASE = 'https://fflogs.com/v1'
FFLOGS_FIGHTS = FFLOGS_BASE + '/report/fights/{}'
FFLOGS_ZONES = FFLOGS_BASE + '/zones'
FFLOGS_SUMMARY = FFLOGS_BASE + '/report/tables/summary/{}'

CLASS_TRI = {'Astrologian': 'ast', 'Bard': 'brd', 'BlackMage': 'blm',
             'DarkKnight': 'drk', 'Dragoon': 'drg', 'Machinist': 'mch',
             'Monk': 'mnk', 'Ninja': 'nin', 'Paladin': 'pld',
             'Scholar': 'sch', 'Summoner': 'smn', 'Warrior': 'war',
             'WhiteMage': 'whm', 'RedMage': 'rdm', 'Samurai': 'sam',
             'Dancer': 'dnc', 'Gunbreaker': 'gnb'}


class FFlogs:

    def __init__(self, api_key):
        self.api_key = api_key

    def list_zones(self):
        resp = requests.get(FFLOGS_ZONES, {'translate': 'false', 'api_key': self.api_key})
        if resp.status_code != 200:
            print('Non 200 status code fetching zones', sys.stderr)
            print(resp.json(), sys.stderr)
        print(resp.json(), sys.stderr)
        data = resp.json()
        for zone in data:
            print('{} | {}'.format(zone['name'], zone['id']))
            for enc in zone['encounters']:
                print('---> {} | {}'.format(enc['name'], enc['id']))

    def report(self, report_id):
        resp = requests.get(FFLOGS_FIGHTS.format(report_id), {'translate': 'false', 'api_key': self.api_key})
        data = resp.json()
        if resp.status_code != 200:
            print('Non 200 status code fetching {}', report_id, sys.stderr)
            print(data, sys.stderr)
            return None
        #print(resp.json(), sys.stderr)
        #print(json.dumps(data, indent=2))
        return data['fights']

    def fights_data(self, report_id):
        report = self.report(report_id)
        #print(json.dumps(report, indent=2))
        data = []
        for fight in report:
            if 'id' not in fight or not fight['boss']:
                continue
            duration = fight['end_time'] - fight['start_time']
            fight_percentage = -1
            kill = False
            if 'fightPercentage' in fight:
                fight_percentage = fight['fightPercentage']/100
            if 'kill' in fight:
                kill = fight['kill']
            data.append([fight['id'], fight['boss'], fight['name'],
                         np.round(100 - fight_percentage, 2),
                         fight['start_time'], fight['end_time'],
                         fight['zoneName'], kill])
        return data

    def fight_data_bounded(self, report_id, start, end, boss_id):
        resp = requests.get(FFLOGS_SUMMARY.format(report_id), {'translate': 'false', 'api_key': self.api_key,
                                                               'start': start, 'end': end})
        table = resp.json()
        if resp.status_code != 200:
            print('Non 200 status code fetching {}', report_id, sys.stderr)
            print(table, sys.stderr)
            return None
        #print(json.dumps(table, indent=2))
        fight = []
        for m in table['composition']:
            fight.append([m['id'], m['name'], CLASS_TRI[m['type']]])
        #print(fight)
        for m in table['damageDone']:
            tmp = [y for y in fight if y[0] == m['id']]
            if not tmp:
                continue
            tmp = tmp[0]
            duration = (end - start) / 1000
            dps = np.round(m['total']/duration, 2)
            tmp.append(dps)
            # death count
            tmp.append(0)
        #print(fight)
        fight.sort(key=lambda x: x[3], reverse=True)
        dead = {}
        # count death events
        for m in table['deathEvents']:
            tmp = [y for y in fight if y[0] == m['id']][0]
            tmp[-1] = tmp[-1] + 1
        # remove id
        res = []
        for m in fight:
            res.append(m[1:])
        print(res)
        return res, boss_id

    def _fight_data(self, data, report_id, fid):
        fight = [x for x in data if x[0] is fid]
        print(fight)
        if not fight:
            print("Fight with id {} not found".format(fid), sys.stderr)
            return None
        start = fight[0][4]
        end = fight[0][5]
        return self.fight_data_bounded(report_id, start, end, fight[0][1])

    def fight_data(self, report_id, fid):
        data = self.fights_data(report_id)
        #print(data)
        return self._fight_data(data, report_id, fid)

    def fight_data_dummy(self, report_id, fid):
        data, boss_id = self.fight_data(report_id, fid)
        dummy_data = DummyData()
        try:
            for m in data:
                dps_min = dummy_data.get_dps(boss_id, m[1])
                m.insert(3, dps_min)
            return data, boss_id
        except NotImplemented:
            print('Boss not supported {} {}', boss_id, data[6])
        return self.fight_data(data, report_id, fid)

    def print_fights(self, report_id):
        table = PrettyTable()
        table.field_names = ['Id', 'BossId', 'Boss', '%', 'Duration', 'Zone', 'Kill']
        data = self.fights_data(report_id)
        pdata = []
        for row in data:
            tmp = row[:4]
            duration = row[5] - row[4]
            tmp.append(str(datetime.timedelta(seconds=duration//1000)))
            tmp = tmp + row[-2:]
            pdata.append(tmp)
        table.add_rows(pdata)
        print(table)

    def print_fight(self, report_id, fid):
        table = PrettyTable()
        data, boss_id = self.fight_data_dummy(report_id, fid)
        total_dps = sum([x[2] for x in data])
        print('total_dps {}'.format(total_dps))
        for m in data:
            m.insert(3, np.round(100*m[2]/total_dps, 2))
        # in case dummy min dps is supported
        if len(data[0]) > 5:
            table.field_names = ['Name', 'Class', 'Dps', '% Dps', 'MinDps', '% MinDps', 'Deaths']
            for m in data:
                delta = m[2] - m[4]
                m.insert(5, '{0:+.2f}'.format(np.round(100*delta/m[4], 2)))
        else:
            table.field_names = ['Name', 'Class', 'Dps', '% Dps', 'Deaths']
        print(data)
        table.add_rows(data)
        print(table)


test = FFlogs(os.environ.get('API_KEY'))
#test.report('Jtxv83AkV6gWYXC2')
#test.list_zones()
#test.print_fights('bVJvc7hjND4nAtFZ')
test.print_fight('bVJvc7hjND4nAtFZ', 54)
#test.print_fight('Jtxv83AkV6gWYXC2', 14)
