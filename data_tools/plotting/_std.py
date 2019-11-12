import pandas as pd
import seaborn as sns


__all__ = ['count_plot_h']

def count_plot_h(data, annotate=True, **params):
    """
    Wrapper for seaborn's Barpolot with horizontal result. Functions like sns.countplot(), but also allows for
    the result of Series.value_counts() to be passed as an argument.

    :param data: Pandas Series, either the data to be counted, or the result of value_counts() output
        (Or value counts with further data manipulation, (i.e. convert to percentages))
    :param annotate: Boolean, dict, or Series. If `True` will plot the counts at the end of the bars. If `False`,
        no annotations will be plotted. If a Series or dict, annotations other than the values can be passed
        and plotted at the end of the bars.  (e.g. plot percentages, but annotate with counts).
    :**params: Other arguments to be passed to Seaborn's Barplot function.
    """

    # Do the value counts if not already done....
    if data.dtype not in [int, float]:
        data = data.value_counts()

    # Plot the data orderred from most to least frequent
    splot = sns.barplot(x=data, y=data.index, **params)

    # Allow a series to be passed
    if type(annotate) == pd.Series:
        annotate = annotate.to_dict()

    # Optionally Print the counts at the end of the data
    if annotate:
        # Allow for user-passed annotation map, or simply annotate the values
        if type(annotate) == bool:
            annotate = data.to_dict()

        # Esnure proper formmating for printing integers...
        if pd.Series(annotate).dtype == int:
            f = lambda v: int(v)
            fs = '{:,}'
        else:
            f = lambda v: v
            fs = '{:,.2}'

        for (p, n) in zip(splot.patches, splot.get_yticklabels()):
            annotation = annotate[n.get_text()]
            splot.annotate(fs.format(f(annotation)), (p.get_width(), p.get_y() + p.get_height()),
                           ha = 'left', va = 'center_baseline', xytext = (0, 10), textcoords = 'offset points')

