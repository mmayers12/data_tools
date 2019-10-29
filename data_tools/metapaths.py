import pandas as pd
from collections import Counter
from collections import defaultdict
from hetnetpy.hetnet import MetaGraph


def dataframes_to_metagraph(nodes, edges):
    abbrev_dict, edge_tuples = get_abbrev_dict_and_edge_tuples(nodes, edges)
    return MetaGraph(abbrev_dict, edge_tuples)


def metapaths_to_json(metapaths):
    """
    Takes a list of objects of hetnetpy.hetnet.MetaPath, and extracts relevant info to a json (dict) structure
    """
    metapaths_out = dict()

    for mp in metapaths:
        if len(mp) == 1:
            continue
        mp_info = dict()
        mp_info['length'] = len(mp)
        mp_info['edges'] = [str(x) for x in mp.edges]
        mp_info['edge_abbreviations'] = [x.get_abbrev() for x in mp.edges]
        mp_info['standard_edge_abbreviations'] = [x.get_standard_abbrev() for x in mp.edges]

        metapaths_out[str(mp)] = mp_info
    return metapaths_out


def subset_mps_by_node_count(metapaths, max_counts=None, subset=None, default_max=1):

    if max_counts is None:
        max_counts = defaultdict(lambda:default_max)
    else:
        max_counts = defaultdict(lambda:default_max, max_counts)

    out = []
    if subset is None:
        subset = metapaths.keys()

    for m in subset:
        # Un-direct the edges...
        no_dir_edges = [e.replace('>', '-').replace('<', '-') for e in metapaths[m]['edges']]
        path_nodes = [no_dir_edges[0].split(' - ')[0]] + [e.split(' - ')[-1] for e in no_dir_edges]
        c = Counter(path_nodes)

        if all([v <= max_counts[k] for k,v in c.items()]):
            out.append(m)

    return out


