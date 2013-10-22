import pandas as pd
import numpy as np
from jinja2 import Template

# Basic aggregation report


class AggregateReport:
    def __init__(self):
        pass
#
# input_df = pd.read_csv('test.csv')
# group_by_operation = input_df.groupby('label')
#
#
# def perc75(x):
#     return np.percentile(x, 0.75)
#
# def perc90(x):
#     return np.percentile(x, 0.9)
#
# def perc95(x):
#     return np.percentile(x, 0.95)
#
# stats = group_by_operation['Latency'].agg([np.mean, np.median, perc75, perc90, perc95]).applymap(lambda x: round(x, 2))
#
#
#
# template = Template('<body>{{ tbl }}</body>')
# report = template.render(tbl=stats.to_html())
#
# f = open('../../test.html', 'w')
# f.write(report)
# f.close