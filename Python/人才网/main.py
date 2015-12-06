# coding=utf8

import config, joblib
import os, imp, sys, multiprocessing

class Application:
    def __init__(self):
        self.subjob_modules = self.load_subjob_modules()

    def load_subjob_modules(self):
        subjob_modules = []
        for filename in os.listdir(config.subjob_path):
            filepath = os.path.join(config.subjob_path, filename)
            if not os.path.isfile(filepath) or filename.startswith('_'): continue
            module_name = 'sites.' + os.path.splitext(filename)[0]
            subjob_modules.append(imp.load_source(module_name, filepath))
        return subjob_modules

    def run(self):
        for module in self.subjob_modules:
            print(module.SubJobProcess.info_from)
        print('OK')

    def test(self):
        queue = multiprocessing.Queue()
        commiter = joblib.Commiter(queue, 1)
        commiter.start()
        job5156 = self.subjob_modules[0]
        process = job5156.SubJobProcess(queue)
        process.start()
        process.join()
        commiter.join()

if __name__=='__main__':
    app = Application()
    app.run()
    app.test()
