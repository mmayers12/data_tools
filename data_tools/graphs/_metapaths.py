from collections import Counter as _Counter
from collections import defaultdict as _defaultdict
from hetnetpy.hetnet import MetaGraph as _MetaGraph, MetaEdge as _MetaEdge
from ._graphs import get_abbrev_dict_and_edge_tuples


__all__ = ['dataframes_to_metagraph', 'metapaths_to_json', 'subset_mps_by_node_count']


def dataframes_to_metagraph(nodes, edges):
    """Converts Nodes and Edges DataFrame to a hetnetpy.hetnet.MetaGraph"""
    abbrev_dict, edge_tuples = get_abbrev_dict_and_edge_tuples(nodes, edges)
    return _MetaGraph.from_edge_tuples(edge_tuples, abbrev_dict)


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
    """Subsets lists of metapaths by number of repeats of a metanode"""
    if max_counts is None:
        max_counts = _defaultdict(lambda:default_max)
    else:
        max_counts = _defaultdict(lambda:default_max, max_counts)

    out = []
    if subset is None:
        subset = metapaths.keys()

    for m in subset:
        # Un-direct the edges...
        no_dir_edges = [e.replace('>', '-').replace('<', '-') for e in metapaths[m]['edges']]
        path_nodes = [no_dir_edges[0].split(' - ')[0]] + [e.split(' - ')[-1] for e in no_dir_edges]
        c = _Counter(path_nodes)

        if all([v <= max_counts[k] for k,v in c.items()]):
            out.append(m)

    return out


