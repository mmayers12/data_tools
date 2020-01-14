import numpy as np
import pandas as pd

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

