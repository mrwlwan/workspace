# coding=utf8

import config, joblib, model
import os, imp, sys, multiprocessing, itertools, re, datetime, csv

class Application:
    def __init__(self):
        self.suport_actions = [('抓取数据', 'fetch', True), ('生成报告', 'report', True)] # 第三项表示是否有下级选择
        self.subjob_modules = self.load_subjob_modules()
        self.today = datetime.date.today()

    def load_subjob_modules(self):
        subjob_modules = []
        for filename in os.listdir(config.subjob_path):
            filepath = os.path.join(config.subjob_path, filename)
            if not os.path.isfile(filepath) or filename.startswith('__'): continue
            module_name = 'sites.' + os.path.splitext(filename)[0]
            subjob_modules.append(imp.load_source(module_name, filepath))
        return subjob_modules

    def input(self):
        while 1:
            action_index = itertools.count(1)
            print('*'*60)
            print('0. 退出')
            print('\n'.join(['{0}. {1}'.format(next(action_index), action[0]) for action in self.suport_actions]))
            select_index = int(input('请选择操作: ').strip())-1
            print('\n')
            if select_index<0: sys.exit()
            action = self.suport_actions[select_index]
            action_method = getattr(self, action[1]+'_action')
            module_index = itertools.count(1)
            print('0. 返回')
            print('\n'.join(['{0}. {1}'.format(next(module_index), module.SubJobProcess.info_from) for module in self.subjob_modules]))
            select_indexes = input('请选择操作(默认非{0}): '.format(config.check_info_from)).strip()
            print('\n')
            if select_indexes=='0': continue
            if select_indexes:
                select_indexes = [int(index)-1 for index in re.split(r'\s+', select_indexes)]
                modules = list(map(self.subjob_modules.__getitem__, select_indexes))
            else:
                modules = None
            action_method(modules)

    def fetch_action(self, modules):
        queue = multiprocessing.Queue()
        commiter = joblib.Commiter(queue, len(modules))
        commiter.start()
        job_processes = []
        for module in modules:
            process = module.SubJobProcess(queue)
            job_processes.append(process)
            process.start()
        for process in job_processes:
            process.join()
        commiter.join()

    def report_action(self, modules=None):
        report_filename_parts = []
        args = [model.CorpModel.insert_date==self.today]
        if modules:
            for module in modules:
                report_filename_parts.append(module.SubJobProcess.info_from)
                args.append(model.CorpModel.info_from==module.SubJobProcess.info_from)
        else:
            args.append(model.CorpModel.info_from!=config.check_info_from)
        query = model.session.query(model.CorpModel).filter(*args)
        if not query.count(): return print('当天没有抓取数据.')
        report_filename_parts.append(config.report_filename)
        report_filename = '_'.join(report_filename_parts)
        queue = multiprocessing.Queue()
        subjobs_classes = dict([(module.SubJobProcess.info_from, module.SubJobProcess) for module in self.subjob_modules])
        subjobs = {}
        title_row = []
        keys = []
        for field in config.report_fields:
            title_row.append(field[0])
            keys.append(field[1])
        with open(report_filename, 'w', encoding=config.report_encoding) as f:
            csv_writer = csv.writer(f, delimiter=',', lineterminator='\n')
            csv_writer.writerow(title_row)
            for corp in query:
                row = []
                for key in keys:
                    if callable(key):
                        if corp.info_from not in subjobs: subjobs[corp.info_from] = subjobs_classes.get(corp.info_from)(queue)
                        row.append(key(subjobs.get(corp.info_from), corp))
                    else:
                        row.append(getattr(corp, key))
                csv_writer.writerow(row)
            f.close()
        print('生成 csv 数据完毕!')


if __name__=='__main__':
    app = Application()
    app.input()
