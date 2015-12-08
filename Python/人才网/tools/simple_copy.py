# coding=utf8

import model
import model_old
import itertools

class CopyProcess:
    def __init__(self):
        self.key_map = { # target.key: source.key
            'name': 'name',
            'code': 'corp_code',
            'address': 'addr',
            'contact_person': 'contact_person',
            'contact_phone': 'contact_tel_no',
            'mail': 'mail',
            'website': 'website',
            'info_from': 'info_from',
            'insert_date': 'insert_date',
        }
        self.commit_count = 50

    def action(self):
        index = itertools.count(1)
        for corp in model_old.session.query(model_old.CorpModel).all():
            corp_info = {}
            for key in self.key_map.keys():
                corp_info[key] = getattr(corp, key)
            model.session.add(model.CorpModel(**corp_info))
            cur_index = next(index)
            if not cur_index % self.commit_count:
                model.session.commit()
                print(cur_index)
        print('Done!')


if __name__=='__main__':
    copy_process = CopyProcess()
    copy_process.action()
