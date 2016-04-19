import pygraphviz as pgv
import pickle, sys
B=pgv.AGraph('/home/igor/graph1min.dot')

import pickle
import pygraphviz as pgv
import pickle, sys

original_graph=pgv.AGraph('/home/igor/graph1min.dot')

def load():
    degr_path_list = []

    with open('wergzeug_10rps.pickle', 'rb') as handle:
        wergzeug_10rps = pickle.load(handle)

    with open('wergzeug_60rps.pickle', 'rb') as handle:
        wergzeug_60rps = pickle.load(handle)

    with open('wergzeug_111rps.pickle', 'rb') as handle:
        wergzeug_111rps = pickle.load(handle)

    for file_path in wergzeug_10rps:
        try:
            avg_time_1 = wergzeug_10rps[file_path][0]
            avg_time_2 = wergzeug_60rps[file_path][0]
            avg_time_3 = wergzeug_111rps[file_path][0]
            avg_calls_3 = wergzeug_111rps[file_path][2]
            if avg_time_1 < avg_time_2 and avg_time_2 <  avg_time_3:
                if avg_time_2 - avg_time_1 < avg_time_3 - avg_time_2:
                    sub_1 = avg_time_3 - avg_time_2
                    sub_2 = avg_time_2 - avg_time_1
                    degr_path_list.append([avg_calls_3 * avg_time_3, sub_1, sub_2, file_path])

        except:
            pass#print("err, #3", file_path)
    return degr_path_list


def limit(min_div, min_sub=0, min_time=0):
    files = []
    for time, sub_1, sub_2, file_path in degr_path_list:
        if sub_1/sub_2 >= min_div and sub_1-sub_2>= min_sub and time >= min_time:
            files.append((file_path[0].replace(".py", ""), file_path[2]))
    return files




def is_restricted(node_): # FIRST
    node_s = node_.split(".")
    result = False
    for file in files:
        if node_.split(".")[-1] == file[1]:
            s = file[0].replace("keystone/venv/local/", "")
            xs = s.split("/") + [file[1]]
            for y in ["", "home", "modis", "lib", "python2.7", "site-packages"]:
                if y in xs:
                    xs.remove(y)
            todel = []
            for i in node_s:
                if [y.isupper() for y in i].count(1) > 0 or i == "common":
                    todel.append(i)
            for j in todel:
                node_s.remove(j)
                if j in xs:
                    xs.remove(j)

            if node_s == xs:
                result = True
    return result


def get_restr_list():
    restr_list = []

    for node in original_graph.nodes():
        if is_restricted(node):
            restr_list.append(node)
    return restr_list


def set_color(node_name, color):
    n = original_graph.get_node(node_name)
    n.attr['fillcolor']=color



def get_predecessors(fnode):
    all_edg = set()
    for tuple_ in B.in_edges(fnode):
        for elem in tuple_:
            all_edg.add(elem)
    return list(all_edg)

def shortest_paths(prev_flist):
    next_flist = []
    for flist in prev_flist:
        next_flist += [flist + [i] for i in get_predecessors(flist[-1]) if not i in flist]
    if [i[-1] for i in next_flist].count("webob.dec.wsgify.__call__") > 0:
        return [j for j in next_flist if j[-1] == "webob.dec.wsgify.__call__"]
    return shortest_paths(next_flist)


def del_unmarked_nodes():
    marks = {}
    for node_key in restr_list:
        init_flist = [[node_key]]
        for path in shortest_paths(init_flist):
            print len(path),  path
            for save_node in path:
                marks[save_node] = 2
                set_color(save_node, "#E4E4E4")
            req_func = path[0]
            marks[req_func] = 1
            set_color(req_func, "#FF6500")
    for node in original_graph.nodes():
        if not node in marks:
            original_graph.remove_node(node)


def save_to_dot():
    set_color("webob.dec.wsgify.__call__", "#4900F5")
    original_graph.write('div2.dot')


degr_path_list = load()
###
files = limit(min_div=50, min_sub = 0, min_time=10)
###
restr_list = get_restr_list()
print len(restr_list)
del_unmarked_nodes()
save_to_dot()
original_graph.layout()
original_graph.draw('last_outp.svg', prog='dot')
print "(2) number of nodes: ", len(original_graph.nodes())






# for x in L1:
#     if x[-1] == "webob.dec.wsgify.__call__":
#         print x, len(x)







"""
L_slow = get_rootpath()

    mark = {}
    for node_key in L_slow:
        for save_node in L_slow[node_key]:
            mark[save_node] = 2
            set_color(save_node, "#CCFFCC")
    for rnode in L_slow:
        mark[rnode] = 1
        set_color(rnode, "#FF6500")

    for node in original_graph.nodes():
        if not node in mark:
            original_graph.remove_node(node)
#def get_rootpath(): # SECOND
#     with open("restr_listsSlow.txt", "r") as f2:
#         txt2 = f2.read()
#     L_slow = {}
#
#     for x in txt2.split("\n"):
#         mas = x.replace(" u'", "").replace("[u'", "").replace("'", "").replace("[","").replace("]", "").replace(" ", "").split(",")
#         L_slow[mas[0]] = mas
#     del L_slow[""]
#     todel = []
#     for x in L_slow:
#         if not x in restr_list:
#             todel.append(x)
#
#     for x in todel:
#         del L_slow[x]
#     print L_slow
#     return L_slow
n = 2

path = []
visited = {}
# def dfs(v):
#     path.append(v)
#     visited[v] = True
#     in_edges =  get_predecessors(B.in_edges(v))
#     for node in reversed(in_edges):
#         if not node in visited:
#             dfs(node)
#     if path[-1] == "webob.dec.wsgify.__call__":
#         print len(path), path  #return path,
#     #print list(reversed(path))
#     print path
#     path.pop()
#     #return path


#dfs("oslo_config.cfg._Namespace._check_deprecated")

def shortest_paths2(func_name):

    def create_lists_for_pred(arr):
        fnode = arr[-1]
        res = []
        for x in get_predecessors(fnode):
            if not x in arr:
                res.append(arr + [x])
        return res

    L = [[func_name]]
    while True:
        new_L = []
        for x in L:
            try:
                new_L = new_L + create_lists_for_pred(x)
                # if [x[-1] for x in new_L].count("webob.dec.wsgify.__call__") > 0:
                #     return new_L
            except:
                print("err")
        L = new_L[:]
        print [x[-1] for x in L].count("webob.dec.wsgify.__call__"), "/", len(L)
        # if len(L) == [x[-1] for x in L].count("webob.dec.wsgify.__call__"):
        #     return L
        if [x[-1] for x in L].count("webob.dec.wsgify.__call__") > 0:
            return L

    return L


def create_lists_for_pred(arr):
    return [arr+[x] for x in get_predecessors(arr[-1]) if not x in arr]
    #fnode = arr[-1]
    # res = []
    # for x in get_predecessors(fnode):
    #     if not x in arr:
    #         res.append(arr + [x])
    #return res


def shortest_paths3(func_name):


    L = [[func_name]]
    while True:
        new_L = []
        for x in L:
            try:
                new_L = new_L + create_lists_for_pred(x)
                # if [x[-1] for x in new_L].count("webob.dec.wsgify.__call__") > 0:
                #     return new_L
            except:
                print("err")
        L = new_L[:]
        if [x[-1] for x in L].count("webob.dec.wsgify.__call__") > 0:
            return L

    return L

def create_lists_for_pred(arr):
    fnode = arr[-1]
    res = []
    for x in get_predecessors(fnode):
        if not x in arr:
            res.append(arr + [x])
    return res

def shortest_paths(L):
    new_L = []
    for x in L:
        new_L += [x+[i] for i in create_lists_for_pred(x)
    if [i[-1] for i in new_L].count("webob.dec.wsgify.__call__") > 0:
        return new_L
    return shortest_paths(new_L)

"""




