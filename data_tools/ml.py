import numpy as np
import pandas as pd
from copy import deepcopy
from tqdm.auto import tqdm

def add_percentile_for_grp(in_df, group_col, new_col, sort_col='prediction'):

    grpd = in_df.groupby(group_col)
    out_dfs = []

    for grp, df1 in grpd:
        df = df1.copy()

        total = df.shape[0]

        df.sort_values(sort_col, inplace=True)
        order = df.reset_index(drop=True).index.values

        percentile = (order+1) / total
        df[new_col] = percentile

        out_dfs.append(df)

    return pd.concat(out_dfs, sort=False, ignore_index=True)


def get_model_coefs(model, X, f_names):
    """Helper Function to quickly return the model coefs and correspoding fetaure names"""

    # Ensure we have a numpy array for the features
    if type(X) == pd.DataFrame:
        X = X.values

    # Grab the coeffiencts
    coef = model.coef_
    # Some models return a double dimension array, others only a single
    if len(coef) != len(f_names):
        coef = coef[0]

    # insert the intercept
    coef = np.insert(coef, 0, model.intercept_)
    names = np.insert(f_names, 0, 'intercept')

    # Calculate z-score scaled coefficients based on the features
    z_intercept = coef[0] + sum(coef[1:] * X.mean(axis=0))
    z_coef = coef[1:] * X.std(axis=0)
    z_coef = np.insert(z_coef, 0, z_intercept)

    # Return
    return pd.DataFrame([names, coef, z_coef]).T.rename(columns={0:'feature', 1:'coef', 2:'zcoef'})



def piecewise_extraction(function, to_split, block_size=1000, axis=0, ignore_cols=None, **params):
    """
    Run hetnet_ml.extractor.MatrixFormattedGraph feature extraction methods in a piecewise manner
    """

    assert type(to_split) == str and to_split in params

    # Won't want progress bars for each subsetx
    params['verbose'] = False

    # Retain a copy of the original parameters
    full_params = deepcopy(params)
    total = len(params[to_split])

    # Determine the number of iterations needed
    num_iter = total // block_size
    if total % block_size != 0:
        num_iter += 1

    all_results = []
    for i in tqdm(range(num_iter)):

        # Get the start and end indicies
        start = i * block_size
        end = (i+1) * block_size

        # End can't be larger than the total number items
        if end > total:
            end = total

        # Subset the paramter of interest
        params[to_split] = full_params[to_split][start: end]

        # Get the funciton results
        all_results.append(function(**params))

    if ignore_cols is not None:
        to_cat = [r.drop(ignore_cols, axis=axis) if i > 0 else r for i, r in enumerate(all_results)]
    else:
        to_cat = all_results

    return pd.concat(to_cat, sort=False, axis=axis)


