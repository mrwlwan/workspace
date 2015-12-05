# coding=utf8

import joblib


class SubJobProcess(joblib.JobProcess):
    info_from = '智通人才网'
    def __init__(self, queue):
        setting = {
                }
        super().__init__(queue, setting)
