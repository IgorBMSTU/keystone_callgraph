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

LOW_RPS_DATA = "werkzeug_low_rps.pickle"
MEDIUM_RPS_DATA = 'werkzeug_medium_rps.pickle'
HIGH_RPS_DATA = 'werkzeug_high_rps.pickle'

def load_werkzeug_data(min_div = 1, min_sub=0, min_time=0):
    degr_path_list = []
    with open(LOW_RPS_DATA, 'rb') as handle:
        low_rps_data = pickle.load(handle)

    with open(MEDIUM_RPS_DATA, 'rb') as handle:
        medium_rps_data = pickle.load(handle)

    with open(HIGH_RPS_DATA, 'rb') as handle:
        high_rps_data = pickle.load(handle)
    
    for file_path in low_rps_data:
        if file_path in medium_rps_data and file_path in high_rps_data:
            time_low = low_rps_data[file_path]["avg_percall"]
            time_medium = medium_rps_data[file_path]["avg_percall"]
            time_high = high_rps_data[file_path]["avg_percall"]
            calls_high = high_rps_data[file_path]["number_of_calls"]
            sub_right = time_high - time_medium
            sub_left = time_medium - time_low
            sub = sub_right - sub_left
            time = time_high * calls_high
            if time_low < time_medium and time_medium <  time_high:
                div = sub_right / sub_left
                if sub_right > sub_left and div >= min_div and sub >= min_sub and time >= min_time:
                        degr_path_list.append(file_path)
    return degr_path_list
    
def find_classname(func_data):
    path, strnumb, name = func_data
    func_name = path.replace(".py", "").split("/")[-1]
    if exists(path):
        with open(path, "r") as f:
            source = f.read()
            tree = ast.parse(source)
            for ast_obj in tree.body:
                if isinstance(ast_obj, ast.ClassDef):
                    for line in ast_obj.body:
                        if line.lineno == strnumb:
                            return "%s.%s.%s" % (func_name, ast_obj.name, name)
    return "%s.%s" % (func_name, name)

def get_degr_list(files):
    nodes_for_save = []
    for path_tuple in files:
        node_ends_with = find_classname(path_tuple)
        for node in original_graph.nodes():
            if node.endswith(node_ends_with):
                nodes_for_save.append(node)
    return nodes_for_save    

def set_color(node_name, color):
    node_obj = original_graph.get_node(node_name)
    node_obj.attr['fillcolor']=color

def get_predecessors(fnode):
    return [x[0] for x in original_graph.in_edges(fnode)]

def shortest_paths(prev_flist):
    next_flist = []
    for flist in prev_flist:
        next_flist += [flist + [i] for i in get_predecessors(flist[-1])]
    next_filtered = filter(lambda j: j[-1] == ROOT_FUNCTION, next_flist)
    if next_filtered:
        return next_filtered
    return shortest_paths(next_flist)

def del_unmarked_nodes(restr_list):
    marked = []
    for node_key in restr_list:
        init_flist = [[node_key]]
        for path in shortest_paths(init_flist):
            for save_node in path:
                marked.append(save_node)
                set_color(save_node, OTHER_NODES_COLOR)
            req_func = path[0]  # name of the degrading function
            marked.append(req_func)
            set_color(req_func, DEGR_NODES_COLOR)
    for node in original_graph.nodes():
        if not node in marked:
            original_graph.remove_node(node)

def save_to_dot(original_graph):
    set_color(ROOT_FUNCTION, ROOT_COLOR)
    original_graph.write("%s.dot" % GRAPH_FNAME)

if __name__ == "__main__":
    original_graph = pgv.AGraph(ORIGINAL_GRAPH_PATH)
    files = load_werkzeug_data(min_div = 6, min_sub = 0, min_time = 0)
    restr_list = get_degr_list(files)
    print len(restr_list)
    del_unmarked_nodes(restr_list)
    save_to_dot(original_graph)
    original_graph.layout()
    original_graph.draw("%s.svg" % GRAPH_FNAME, prog='dot')
    print "number of nodes: ", len(original_graph.nodes())
