import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from pandas.api.types import CategoricalDtype

def marginal_dependency_plot(
    data, 
    target, 
    feature_col, 
    is_categorical=False, 
    bins=20, 
    sample_pct=1, 
    lower_q=.1,
    upper_q=.9,
    max_n_categories=100,
    categories_recall_pct=1,
    keep_nan=True,
):
    nan_target_constrain = ~data[target].isna()
    
    sample_data = (
        data[[target, feature_col]].loc[nan_target_constrain]
        .sample(frac=sample_pct)
        .copy()
    )
    if is_categorical is False:
        sample_data[feature_col] = categorify_feature(sample_data[feature_col], bins)
    else:
        sample_data[feature_col] = trim_categories(
            sample_data[feature_col], 
            max_n_categories,
            categories_recall_pct,
            keep_nan)
    group_statistics = get_group_statistics(sample_data, feature_col, target, lower_q, upper_q)
    if is_categorical is True:
        group_statistics = group_statistics.sort_values(by='quantile_0.5')

    fig = plot_statistics(group_statistics)
    fig.show()

def categorify_feature(feature_series, bins):
    feature_values = feature_series.to_frame('feature')
    feature_values['feature_bin'] = pd.cut(feature_values['feature'], bins=bins)
    print(feature_values.feature_bin.unique())
    
    interval_mapping = (
        feature_values
        .groupby('feature_bin')['feature']
        .apply(pretty_interval)
        .to_dict()
    )

    feature_values['feature_bin'] = feature_values['feature_bin'].map(interval_mapping)
    print(interval_mapping.values())
    cat_type = CategoricalDtype(list(interval_mapping.values()), ordered=True)
    feature_values['feature_bin'] = feature_values['feature_bin'].astype(cat_type)

    return feature_values['feature_bin'].values

def pretty_interval(bin_grouped_df):
    print(bin_grouped_df.name)
    if np.isnan(bin_grouped_df.min()):
        print('oli')
    left = bin_grouped_df.min()
    right = bin_grouped_df.max()
    if left < right:
        return f'{left} a {right}'
    else:
        return str(left)


def trim_categories(categories_series, max_n_categories, categories_recall_pct, keep_nan):
    categories_pct = (
        categories_series
        .value_counts(normalize=True, dropna=False)
        .sort_values(ascending=False)
        .cumsum()
    )
    recall_categories = categories_pct[categories_pct <= categories_recall_pct].index
    selected_categories = recall_categories[:min(max_n_categories, len(recall_categories))]
    category_mapping = {c: 'otras' for c in categories_series.unique() if not c in selected_categories}

    if keep_nan and np.NaN in categories_pct.index:
        try:
            category_mapping[None] = 'NaN'
        except:
            pass
        try:
            category_mapping[np.NaN] = 'NaN'
        except:
            pass
    return categories_series.replace(category_mapping)

def get_group_statistics(data, feature_col, target, lower_q, upper_q):
    quantiles = [lower_q, 0.5, upper_q]
    group_quantiles = (
        data.groupby(feature_col)
        [target]
        .apply(np.quantile, q=quantiles)
        .explode()
        .reset_index()
    )
    group_quantiles[target] = group_quantiles[target].astype(float)
    quantile_names = [f'quantile_{q}' for q in quantiles]
    group_quantiles['statistic'] = np.concatenate([quantile_names for _ in range(group_quantiles[feature_col].nunique())])
    group_quantiles = pd.pivot_table(group_quantiles, index=feature_col, columns='statistic', values=target)
    group_quantiles['mean'] = data.groupby(feature_col)[target].mean()

    return group_quantiles

def plot_statistics(data, yaxis_title=None, xaxis_title=None, title=None):
    quantile_cols = [c for c in data.columns if 'quantile' in c]
    quantiles = [float(q.split('quantile_')[1]) for q in quantile_cols]
    lower_q = min(quantiles)
    upper_q = max(quantiles)

    color_lower_upper_marker = "#C7405A"
    color_fillbetween = 'rgba(63, 13, 74, 0.3)'
    color_median = 'rgba(69, 25, 78)' 	
    fig = go.Figure([
    go.Scatter(
        name='Median',
        x=data.index,
        y=data['quantile_0.5'],
        mode='lines',
        line=dict(color=color_median),
    ),
    go.Scatter(
        name='Mean',
        x=data.index,
        y=data['mean'],
        mode='lines',
        line=dict(color='black', dash='dash'),
    ),
    go.Scatter(
        name=f'Quantile {int(100*upper_q)}%',
        x=data.index,
        y=data[f'quantile_{upper_q}'],
        mode='lines',
        marker=dict(color=color_lower_upper_marker),
        line=dict(width=0),
        showlegend=False
    ),
    go.Scatter(
        name=f'Quantile {int(100*lower_q)}%',
        x=data.index,
        y=data[f'quantile_{lower_q}'],
        marker=dict(color=color_lower_upper_marker),
        line=dict(width=0),
        mode='lines',
        fillcolor=color_fillbetween,
        fill='tonexty',
        showlegend=False
    )
    ])

    fig.update_layout(
        yaxis=dict(title=yaxis_title, showgrid=False),
        xaxis=dict(title=xaxis_title, showgrid=False),
        title=title,
        hovermode="x",
    )
    return fig