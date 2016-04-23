import os
import marshal
import numpy as np
import pickle
from six import iteritems

LOW_RPS_FOLDER = "/var/lib/werkzeug_floder/uwsgi_10"
MEDIUM_RPS_FOLDER = "/var/lib/werkzeug_floder/uwsgi_60"
HIGH_RPS_FOLDER = "/var/lib/werkzeug_floder/uwsgi_111"

class Pstat:
    def __init__(self, outp_dir):
        self.outp_dir = outp_dir
        self.func_dict = {}

    def fill_fulldict(self, stats):
        for func, (cc, nc, tt, ct, callers) in iteritems(stats):
            if not func in self.func_dict:
                self.func_dict[func] = {}
                self.func_dict[func]["cumtime_values"] = []
                self.func_dict[func]["call_values"] = []
                self.func_dict[func]["percall_values"] = []
            self.func_dict[func]["percall_values"].append(float(ct)/float(cc))
            self.func_dict[func]["cumtime_values"].append(ct)
            self.func_dict[func]["call_values"].append(cc)

    def read_stat(self, fname):
        with open("%s/%s" % (self.outp_dir, fname), "rb") as f:
            data = marshal.load(f)
            return data



    def load_profiler_data(self):
        flist = os.listdir(self.outp_dir)
        if not self.func_dict:
            for file_ in flist:
                if os.path.exists("%s/%s" % (self.outp_dir, file_)):
                    marshal_data = self.read_stat(file_)
                    self.fill_fulldict(marshal_data)

    def count_avg(self):
        res_dict = {}
        for fpath in self.func_dict:
            cumtime_list = self.func_dict[fpath]["cumtime_values"]
            percall_list = self.func_dict[fpath]["percall_values"]
            cc_list = self.func_dict[fpath]["call_values"]
            res_dict[fpath] = { "avg_cumtime": np.average(cumtime_list),
                                "avg_percall": np.average(percall_list),
                                "number_of_calls": sum(cc_list)
                }
        return res_dict



if __name__ == "__main__":
    first_test = Pstat(LOW_RPS_FOLDER)
    first_test.load_profiler_data()
    low_data = first_test.count_avg()
    with open('werkzeug_low_rps.pickle', 'wb') as handle:
        pickle.dump(low_data, handle)

    second_test = Pstat(MEDIUM_RPS_FOLDER)
    second_test.load_profiler_data()
    medium_data = second_test.count_avg()
    with open('werkzeug_medium_rps.pickle', 'wb') as handle:
        pickle.dump(medium_data, handle)

    third_test = Pstat(HIGH_RPS_FOLDER)
    third_test.load_profiler_data()
    high_data = third_test.count_avg()
    with open('werkzeug_high_rps.pickle', 'wb') as handle:
        pickle.dump(high_data, handle)

