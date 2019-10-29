import pandas as pd


def change_edge_type(edges, from_type, to_type, swap=False):
    idx = edges.query('type == @from_type').index
    edges.loc[idx, 'type'] = to_type
    if swap:
        tmp = edges.loc[idx, 'start_id']
        edges.loc[idx, 'start_id'] = edges.loc[idx, 'end_id']
        edges.loc[idx, 'end_id'] = tmp


def map_edge_types_from_file(edges, map_df, orig_type='type', new_type='new_type',
                             swap_label='reverse_node_labels'):
    """
    In-place updater of Edge Types from a mapping dataframe
    """
    for row in map_df.itertuples():
        from_type = getattr(row, orig_type)
        to_type = getattr(row, new_type)
        swap = getattr(row, swap_label)

        change_edge_type(edges, from_type, to_type, swap)

