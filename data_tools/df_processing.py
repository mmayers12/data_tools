import pandas as pd
from itertools import chain


def char_combine_iter(iterable, char='|', sort=False):
    """Deduplicates elements, then combines an iterable on a character to a single string output"""
    out = list(set(iterable))
    return char.join(sorted(out)) if sort else char.join(out)


def char_combine_series(col, char='|', sort=False):
    """
    Converts a Series to a string, splitting elements within that Series on a character, dedupcating all elements,
    removing na values, then joining across that character on that charcter.

    e.g. 1   "123456|102934"
         2   "123456"
         3   "102934|432452"
         4   "201945"

         becomes:
            "123456|102934|432452|201945"

    :param col: The Series to process in this maner
    :param char: The character to split, and then rejoin elements on,
    :param sort: Boolean, if True, the output will be sorted before joining
    :param split: Boolean, if False, will not split the input before uniqifying and rejoining.
            Primarily used to increase processing speed when it is known there are zero character
            joined items in the input

    :return: str, The newly joined output
    """

    # Dropna Values and combine to a single cell
    if split:
        out = col.dropna().apply(lambda r: r.split(char))
        return char_combine_iter(chain(*out))
    else:
        return char_combine_iter([v for v in col.values if str(v) != 'nan'])


def char_combine_frame(df, char='|', sort=False, split=True):
    """
    Converts all values of a dataframe to a single string, deduplicating and joining on a character.

    For example,. the DataFrame
                0    1    2
            0   A|B  C    A
            1   D    NaN  C
            2   NaN  D|C  F

    Becomes
            'B|A|D|F|C'

    :param df: The dataframe of elements to join
    :param char: The character to split, and then rejoin elements on,
    :param sort: Boolean, if True, the output will be sorted before joining
    :param split: Boolean, if False, will not split the input before uniqifying and rejoining.
            Primarily used to increase processing speed when it is known there are zero character
            joined items in the input. (this may be important on very large datasets)

    :return: String, the joined elements in one string
    """

    # this split can be expensive on large data, so only do it if we know that it needs to be split.
    if split:
        return char_combine_iter(chain(*[v.split('|') for v in chain(*df.values) if not str(v) == 'nan']), char, sort)
    else:
        return char_combine_iter([v for v in chain(*df.values) if not str(v) == 'nan'], char, sort)


def find_cols_with_multi_values(grouped):
    """
    In a Pandas Groupby object, determines which columns have more than one value per group
    """
    multi_val_cols = (grouped.nunique() > 1).sum()
    multi_val_cols = multi_val_cols[multi_val_cols > 0].index.tolist()
    return multi_val_cols


def combine_group_cols_on_char(df, group_on, combine_cols=None, char='|', sort=False, split=True):
    """
    Performs a Groupby on a dataframe and then converts each group into a single row, joinned by a character `char`

    Primarly suppports grouping on columns, other methods have not been tested.

    :param df:  The dataframe to group
    :param group_on: the column name or list of column names to group by
    :param combine_cols: a list of column names to combine with a character, if None, will combine all columns.
        can save computation time to provide only the columns of interest for combination
    :param char: the character to combine the columns with. Defaults to a `|` character.
    :param sort: bool, whether or not to sort the output before joining the string
    :param split: Boolean, if False, will not split the input before uniqifying and rejoining.
            Primarily used to increase processing speed when it is known there are zero character
            joined items in the input. (this may be important on very large datasets)

    :return: Dataframe with 1 row per group, and information of different rows joined by given character.

    """
    col_order = df.columns

    if type(group_on) in (str, int, float):
        group_on = [group_on]

    grouped = df.groupby(group_on)

    if combine_cols is None:
        combine_cols = find_cols_with_multi_values(grouped)

    out_df = grouped.first()

    # Splitting before doing the groupby is much much faster
    if split:
        split_df = df[combine_cols].applymap(lambda x: str(x).split('|'))
        grouped = pd.concat([df[group_on], split_df], axis=1).groupby(group_on)

    # Apply the uniqify and comine to each col in the target groups.
    for col in tqdm(combine_cols, desc='total_progress'):
        tqdm.pandas(desc=col)

        # The split result needs an extra chain
        if split:
            out_df[col] = grouped[col].progress_apply(lambda s: char_combine_iter([v for v in chain(*s.values) if v != 'nan']
                                                                                  , char=char, sort=sort))
        else:
            out_df[col] = grouped[col].progress_apply(char_combine_series, char=char, sort=sort)

    return out_df.reset_index()[col_order]


def add_curi(data_frame, curi_map):
    """
    Adds CUIs to each item in a DataFrame. Only 1 item per cell. Will skip if elemnts aready start with `CURI:`.

    :param data_frame: The DataFrame to add curis to.
    :param curi_map: dict, with key == column name and value == CURI.

    :return: DataFrame, the DataFrame with CURIs added to each element in columns
    """

    out = data_frame.copy()
    for col_name, curi in curi_map.items():

        # Skip empty columns and those that already have CURIs in their identifier
        col_items = out[col_name].dropna()
        if len(col_items) == 0 or (col_items.str.startswith(curi).sum() == len(col_items) and \
               col_items.str.contains(':').sum() == len(col_items)):
            continue

        out[col_name] = curi+':'+out[col_name]
    return out


def split_col(col, char, dropna=False):
    """Splits a Series by a characters, into a new series of equal length with each element as a list"""
    if dropna:
        return col.dropna().apply(lambda s: s.split(char))
    return pd.Series([s.split(char) if type(s) == str else [s] for s in col.tolist()], name=col.name, index=col.index)


def expand_split_col(col_split):
    """
    Takes a Pandas.Series that contains an iterable, and expands to a 2-col DataFrame with 1 item per row.
    The original index will be contained in the second column.
    """
    col_name = col_split.name

    old_idx = list(chain(*[[x]*len(v) for x, v in col_split.to_dict().items()]))
    new_col = list(chain(*col_split.values))

    return pd.DataFrame({'old_idx': old_idx, col_name: new_col})


def expand_col_on_char(df, col_name, char, dropna=False):
    """
    Expands rows in a dataframe due to a column where elements contain multiple values separated by a character,
    resulting in only one element per row in the new column

    For example, a column of pipe separated Pubmed IDs (in .csv format):
        letter, pmid
        a, 12805067|17698565|18279049|21329777
        b, 10072544|12721113

    Would become:
        letter, pmid
        a, 12805067
        a, 17698565
        a, 18279049
        a, 21329777
        b, 10072544
        b, 12721113

    :param df: The DataFrame to expand.
    :param col_name: str, the name of the column to expand
    :param char: the char to expand the column on
    :param dropna: If True, rows with NAN values in the epanded column will be dropped in the final result.
        While this loses data, it can greatly speed up the algorithm on large datasets, when NAN rows are not
        needed.
    :return: DataFrame, with the extra rows
    """
    # Copy df and get column order
    col_order = df.columns
    out = dict()

    if dropna:
        df = df.dropna(subset=[col_name])
        # Split the desired column on the desired character
        split_col = [s.split(char) for s in df[col_name].tolist()]
    else:
        # Split the desired column on the desired character
        split_col = [s.split(char) if type(s) == str else [s] for s in df[col_name].tolist()]
    # expand the rows
    out[col_name] = chain(*split_col)

    # Now fix the other cols
    other_cols = [c for c in col_order if c != col_name]
    lens = [len(s) for s in split_col]
    for col in other_cols:
        col_vals = list(chain(*[[v]*l for v, l in zip(df[col].tolist(), lens)]))
        out[col] = col_vals

    return pd.DataFrame(out)[col_order]



