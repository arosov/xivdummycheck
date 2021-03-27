import json
import sys
import numpy as np

BOSSDATA = 'data.json'


class DummyData:

    def list_fights(self):
        with open(BOSSDATA, 'r') as fdata:
            data = json.load(fdata)
            for fight in data['boss']:
                print(fight['bossName'])

    def get(self, boss_id):
        boss_id = str(boss_id)
        with open(BOSSDATA, 'r') as fdata:
            data = json.load(fdata)
            for fight in data['boss']:
                if 'ids' not in fight:
                    continue
                if boss_id in fight['ids']:
                    return fight['jobs']
            print('Fight with id {} not found !'.format(boss_id), sys.stderr)
            return None

    def get_dps(self, id_boss, class_tri):
        data = self.get(id_boss)
        hp = [x['bossHp'] for x in data if x['job'] == class_tri][0]
        hp = int(hp)
        return np.round(hp/180, 2)
# e9s 73
# e10s 74
# e11s 75
# e12s 76 77

#dum = DummyData()
#dum.list_fights()
#print(dum.get('73'))
#print(dum.get_dps('73', 'sch'))
#print(dum.get_dps('73', 'gnb'))
