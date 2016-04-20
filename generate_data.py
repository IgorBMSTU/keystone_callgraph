import os
import datetime
import pprint
import pstats
import marshal
import matplotlib
matplotlib.use('Agg')
from numpy import array
from scipy import stats
import numpy as np
import pylab
import pickle
from six import iteritems

class Pstat:
    def __init__(self, outp_dir):
        self.func_dict = {}
        self.outp_dir = outp_dir

    def parse_stat(self, stats):
        for func, (cc, nc, tt, ct, callers) in iteritems(stats):
            if not func in self.func_dict:
                self.func_dict[func] = []
            self.func_dict[func].append([float(ct)/float(cc), ct, cc])


    def read_stat(self, fname):
        with open("%s/%s" % (self.outp_dir, fname), "rb") as f:
            data = marshal.load(f)
            return data

    def get_flist(self, directory):
        unsorted_flist = []
        f_names = filter(lambda x: x.endswith('.prof'), os.listdir(directory))
        for fname in f_names:
            timestamp = float(fname.split(".")[-2])
            unsorted_flist.append([timestamp, fname])
        unsorted_flist.sort()
        return unsorted_flist


    def sort_flist(self):
        sorted_flist = os.listdir(self.outp_dir)
        if not len(self.func_dict):
            for file_ in sorted_flist:
                try:
                    d1 = self.read_stat(file_)
                    self.parse_stat(d1)
                except:
                    print "#1", file_

    def gen_arrays(self):
        res_dict = {}
        for fpath in self.func_dict:
            div_arr = [val[0] for val in self.func_dict[fpath]]
            ct_arr = [val[1] for val in self.func_dict[fpath]]
            cc_arr = [val[2] for val in self.func_dict[fpath]]
            res_dict[fpath] = [np.average(div_arr), np.average(ct_arr), sum(cc_arr)]
        return res_dict




if __name__ == "__main__":
    first_test= Pstat("/home/modis/werkzeug_data/1.5min_10")
    first_test.sort_flist()
    D1 = first_test.gen_arrays()
    with open('wergzeug_10rps.pickle', 'wb') as handle:
        pickle.dump(D1, handle)

    second_test = Pstat("/home/modis/werkzeug_data/1.5min_60")
    second_test.sort_flist()
    D2 = second_test.gen_arrays()
    with open('wergzeug_60rps.pickle', 'wb') as handle:
        pickle.dump(D2, handle)

    third_test = Pstat("/home/modis/werkzeug_data/1.5min_111")
    third_test.sort_flist()
    D3 = third_test.gen_arrays()
    with open('wergzeug_111rps.pickle', 'wb') as handle:
        pickle.dump(D3, handle)
