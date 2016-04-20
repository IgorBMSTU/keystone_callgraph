import pickle
import pygraphviz as pgv

ORIGINAL_GRAPH_PATH = '/home/igor/graph1min.dot'
ROOT_FUNCTION = "webob.dec.wsgify.__call__"
GRAPH_FNAME = 'last_outp'

def load_werkzeug_data():
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
                sub_1 = avg_time_3 - avg_time_2
                sub_2 = avg_time_2 - avg_time_1
                if sub_2 < sub_1:
                    degr_path_list.append([avg_calls_3 * avg_time_3, sub_1, sub_2, file_path])
        except:
            pass#print("err, #3", file_path)
    return degr_path_list


def limit(min_div, min_sub=0, min_time=0):
    files = []
    for time, sub_1, sub_2, file_path in degr_path_list:
        if sub_1 / sub_2 >= min_div and sub_1-sub_2 >= min_sub and time >= min_time:
            files.append((file_path[0].replace(".py", ""), file_path[2]))
    return files


def is_restricted(node_): # FIRST
    path_with_class = node_.split(".")
    return_value = False
    for file in files:
        cl_funcname = node_.split(".")[-1]
        dir_funcname = file[1]
        if cl_funcname == dir_funcname:
            dir_path = file[0].replace("keystone/venv/local/", "")
            rel_path = dir_path.split("/") + [dir_funcname]
            unwanted_words = ["",
                    "home",
                    "modis",
                    "lib",
                    "python2.7",
                    "site-packages"]
            rel_path = [word for word in rel_path if not word in unwanted_words]
            for_del = []
            for word in path_with_class:
                if [letter.isupper() for letter in word].count(1) > 0 or word == "common":
                    for_del.append(word)
                    if word in rel_path:
                        rel_path.remove(word)
            for j in for_del:
                path_with_class.remove(j)
            if path_with_class == rel_path:
                return_value = True
    return return_value


def get_restr_list():
    restr_list = []
    for node in original_graph.nodes():
        if is_restricted(node):
            restr_list.append(node)
    return restr_list


def set_color(node_name, color):
    node_obj = original_graph.get_node(node_name)
    node_obj.attr['fillcolor']=color



def get_predecessors(fnode):
    all_edges = set()
    for edges_tuple in original_graph.in_edges(fnode):
        for edge in edges_tuple:
            all_edges.add(edge)
    return list(all_edges)

def shortest_paths(prev_flist):
    next_flist = []
    for flist in prev_flist:
        next_flist += [flist + [parent] for parent in get_predecessors(flist[-1]) if not parent in flist]
    if [function[-1] for function in next_flist].count(ROOT_FUNCTION) > 0:
        return [j for j in next_flist if j[-1] == ROOT_FUNCTION]
    return shortest_paths(next_flist)


def del_unmarked_nodes():
    marks = {}
    for node_key in restr_list:
        init_flist = [[node_key]]
        for path in shortest_paths(init_flist):
            #print len(path),  path
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
    set_color(ROOT_FUNCTION, "#4900F5")
    original_graph.write("%s.dot" % GRAPH_FNAME)

if __name__ == "__main__":
    original_graph=pgv.AGraph(ORIGINAL_GRAPH_PATH)
    degr_path_list = load_werkzeug_data()
    files = limit(min_div=50, min_sub = 0, min_time=10)
    restr_list = get_restr_list()
    del_unmarked_nodes()
    save_to_dot()
    original_graph.layout()
    original_graph.draw("%s.svg" % GRAPH_FNAME, prog='dot')
    print "number of nodes: ", len(original_graph.nodes())
