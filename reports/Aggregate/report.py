import numpy as np
from lxml import etree

from lib.basereport import BaseReport
from lib.utils import percentile90


class AggregateReport(BaseReport):
    """Aggregate JMeter report.
    Calculate Mean, Median, 90% Line, Max, Min and Throughput by label.
    """

    def _generate_html_data(self):
        if not hasattr(self, 'df') or not self.df:
            return ''

        # group data by 'label' field
        group_by_operation = self.df.groupby('label')
        # calc statistic by operation: mean, median, 90% line
        result = group_by_operation['Latency'].agg([np.mean, np.median, percentile90, np.min, np.max, np.sum])
        size = group_by_operation.size()

        # Calc throughput for every group
        result['sum'] = result['sum'].astype(float)
        for i in size.index:
            result['sum'][i] = float(size[i]) / float(result['sum'][i]) * 1000

        result = result.applymap(lambda x: round(x, 2))

        # rename columns
        result.rename(columns={'mean': 'Mean, msec',
                               'median': 'Median, msec',
                               'percentile90': '90% Line, msec',
                               'amin': 'Min, msec',
                               'amax': 'Max, msec',
                               'sum': 'Throughput, req/sec'}, inplace=True)

        xml = etree.XML(result.to_html())
        xml.set('class', 'table table-hover table-striped table-condensed table-responsive table-bordered')
        xml.set('border', '')

        return etree.tostring(xml)