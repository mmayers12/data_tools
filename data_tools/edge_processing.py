import pandas as pd
from tqdm import tqdm


def change_edge_type(edges, from_type, to_type, swap=False):
    """
    In-place change of an edge type in a hetnet file.
    """
    idx = edges.query('type == @from_type').index
    edges.loc[idx, 'type'] = to_type
    if swap:
        tmp = edges.loc[idx, 'start_id']
        edges.loc[idx, 'start_id'] = edges.loc[idx, 'end_id']
        edges.loc[idx, 'end_id'] = tmp


def map_edge_types_from_file(edges, map_df, orig_type='type', new_type='new_type',
                             swap_label='reverse_node_labels', prog=True):
    """
    In-place updater of Edge Types from a mapping dataframe
    """

    def inner_func():
        from_type = getattr(row, orig_type)
        to_type = getattr(row, new_type)
        swap = getattr(row, swap_label)

        change_edge_type(edges, from_type, to_type, swap)

    if prog:
        for row in tqdm(map_df.itertuples(), total=len(map_df)):
            inner_func()
    else:
        for row in map_df.itertuples():
            inner_func()

    edges.dropna(subset=['type'], inplace=True).reset_index(drop=True, inplace=True)
