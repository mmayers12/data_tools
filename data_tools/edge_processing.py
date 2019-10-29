import pandas as pd
from tqdm import tqdm
from hetnet_ml.graph_tools import combine_nodes_and_edges


def change_edge_type(edges, idx, new_type, swap=False):
    """
    In-place change of an edge type in a hetnet file.
    """
    edges.loc[idx, 'type'] = new_type
    if swap:
        tmp = edges.loc[idx, 'start_id']
        edges.loc[idx, 'start_id'] = edges.loc[idx, 'end_id']
        edges.loc[idx, 'end_id'] = tmp


def map_edge_types_from_file(edges, map_df, orig_type='type', new_type='new_type',
                              swap_label='reverse_node_labels', nodes=None,
                              start_label='start_label', end_label='end_label',
                              prog=True):
    """
    In-place updater of Edge Types from a mapping dataframe
    """

    # Option to strictly enforce node typing
    if nodes is not None:
        combo = combine_nodes_and_edges(nodes, edges)

    def inner_func():

        # Strict type encforment if all variables there (allows for sloppy edge abbreviations)
        if nodes is not None:
            sl = getattr(row, start_label)
            el = getattr(row, end_label)
            from_type = getattr(row, orig_type)

            to_change = combo.query('start_label == @sl and end_label == @el and type == @from_type').index
        else:
            from_type = getattr(row, orig_type)
            to_change = edges.query('type == @from_type').index

        to_type = getattr(row, new_type)
        swap = getattr(row, swap_label)

        change_edge_type(edges, to_change, to_type, swap)

    if prog:
        for row in tqdm(map_df.itertuples(), total=len(map_df)):
            inner_func()
    else:
        for row in map_df.itertuples():
            inner_func()

    edges.dropna(subset=['type'], inplace=True)
    edges.reset_index(drop=True, inplace=True)

