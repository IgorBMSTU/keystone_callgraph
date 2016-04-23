import ast
import pickle
import pygraphviz as pgv
from os.path import exists


ORIGINAL_GRAPH_PATH = '/home/modis/graph1min.dot'
ROOT_FUNCTION = "webob.dec.wsgify.__call__"
GRAPH_FNAME = 'last_outp'

ROOT_COLOR = "#4900F5"
DEGR_NODES_COLOR = "#FF6500"
OTHER_NODES_COLOR = "#E4E4E4"

def load_werkzeug_data(min_div = 1, min_sub=0, min_time=0):
    degr_path_list = []#defaultdict(dict)
    with open('werkzeug_low_rps.pickle', 'rb') as handle:
        low_rps_data = pickle.load(handle)

    with open('werkzeug_medium_rps.pickle', 'rb') as handle:
        medium_rps_data = pickle.load(handle)

    with open('werkzeug_high_rps.pickle', 'rb') as handle:
        high_rps_data = pickle.load(handle)
    
    for file_path in low_rps_data:
        if file_path in medium_rps_data and file_path in high_rps_data:
            avg_time_low = low_rps_data[file_path]["avg_percall"]
            avg_time_medium = medium_rps_data[file_path]["avg_percall"]
            avg_time_high = high_rps_data[file_path]["avg_percall"]
            avg_calls_high = high_rps_data[file_path]["number_of_calls"]
            if avg_time_low < avg_time_medium and avg_time_medium <  avg_time_high:
                sub_right = avg_time_high - avg_time_medium
                sub_left = avg_time_medium - avg_time_low
                if sub_right > sub_left:
                    if sub_right / sub_left >= min_div and sub_right-sub_left >= min_sub and avg_time_high*avg_calls_high >= min_time:
                        degr_path_list.append(file_path)
    print len(degr_path_list)
                    #degr_path_list[file_path]["avg"] = avg_calls_high * avg_time_high

    #.append([avg_calls_high * avg_time_high, sub_right, sub_left, file_path])
    
    #print filter(lambda tt, sr, sl, fp: sr/sl >= min_div and sr-sl >= min_sub and tt >= min_time, degr_path_list)
    #files = []
    #for time, sub_right, sub_left, file_path in degr_path_list:
    #    if sub_right / sub_left >= min_div and sub_right-sub_left >= min_sub and time >= min_time:
    #        files.append(file_path)
    #return files
    
    return degr_path_list


    
def find_classname(func_data):
    path, strnumb, name = func_data
    if exists(path):
        with open(path, "r") as f:
            source = f.read()
            tree = ast.parse(source)
            for obj in tree.body:
                if isinstance(obj, ast.ClassDef):
                    for line in obj.body: #i.body
                        #if isinstance(j, ast.FunctionDef):
                        if int(line.lineno) == strnumb:
                            return "%s.%s.%s" % (path.replace(".py", "").split("/")[-1], obj.name, name)
    return "%s.%s" % (path.replace(".py", "").split("/")[-1], name)

def get_degr_list(files):
    nodes_for_save = []
    for path_tuple in files:
        node_ends_with = find_classname(path_tuple)
        for node in original_graph.nodes():
            if node.endswith(node_ends_with):
                nodes_for_save.append(node)
    return nodes_for_save    

    
def limit(min_div, min_sub=0, min_time=0):
    files = []
    for time, sub_right, sub_left, file_path in degr_path_list:
        if sub_right / sub_left >= min_div and sub_right-sub_left >= min_sub and time >= min_time:
            files.append(file_path)
    return files

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
        next_flist += [flist + [parent] for parent in get_predecessors(flist[-1])]
    next_filtered = filter(lambda j: j[-1] == ROOT_FUNCTION, next_flist)
    if next_filtered:
        return next_filtered
    return shortest_paths(next_flist)


def del_unmarked_nodes():
    marked = []
    for node_key in restr_list:
        init_flist = [[node_key]]
        for path in shortest_paths(init_flist):
            for save_node in path:
                marked.append(save_node)
                set_color(save_node, OTHER_NODES_COLOR)
            req_func = path[0]
            marked.append(req_func)
            set_color(req_func, DEGR_NODES_COLOR)
    for node in original_graph.nodes():
        if not node in marked:
            original_graph.remove_node(node)


def save_to_dot():
    set_color(ROOT_FUNCTION, ROOT_COLOR)
    original_graph.write("%s.dot" % GRAPH_FNAME)

if __name__ == "__main__":
    original_graph = pgv.AGraph(ORIGINAL_GRAPH_PATH)
    files = load_werkzeug_data(min_div = 1, min_sub = 0, min_time = 0)
    #files = limit(min_div = 5, min_sub = 0, min_time = 2)
    restr_list = get_degr_list(files)
    del_unmarked_nodes()
    print 1
    save_to_dot()
    original_graph.layout()
    original_graph.draw("%s.svg" % GRAPH_FNAME, prog='dot')
    print "number of nodes: ", len(original_graph.nodes())

