# coding=utf8

import joblib, model2
import datetime, multiprocessing, time

class MergeProcess(multiprocessing.Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
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
        self.info_from_map = {
            'job5156': '智通人才网',
            'job577': '瑞安人才网',
            'jobcn': '卓博人才网',
        }

    def info_from_process(self, corp_info):
        info_from = corp_info['info_from']
        if info_from in self.info_from_map:
            corp_info['info_from'] = self.info_from_map[info_from]
        return corp_info

    def check_corp_info(self, corp_info):
        for key in ['info_from', 'insert_date']:
            if not corp_info[key]: return False
        return True

    def run(self):
        for corp in model2.session.query(model2.CorpModel).offset(32910):
            corp_info = {}
            for key, s_key in self.key_map.items():
                corp_info[key] = getattr(corp, s_key)
            if not self.check_corp_info(corp_info):
                print('{0} 失效!'.format(corp_info['name']))
                continue
            corp_info = self.info_from_process(corp_info)
            self.queue.put(corp_info)
            time.sleep(0.1)
        self.queue.put(None)
        print('Done')


if __name__ == '__main__':
    queue = multiprocessing.Queue()
    commiter = joblib.Commiter(queue, 1)
    commiter.start()
    merge_process = MergeProcess(queue)
    merge_process.start()
    merge_process.join()
    commiter.join()

