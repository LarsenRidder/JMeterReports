import numpy as np
import pandas as pd
from lxml import etree

from lib.basereport import BaseReport
from lib.utils import percentile90


class CompareReport(BaseReport):
    """Compare JMeter report.
    Compare Mean, Median, 90% Line, Max, Min and Throughput by label.
    """

    def read_csv(self, file_paths):
        self.df1 = pd.read_csv(file_paths[0])
        self.df2 = pd.read_csv(file_paths[1])

    def _generate_html_data(self):
        if not hasattr(self, 'df1') or not self.df1:
            return ''
        if not hasattr(self, 'df2') or not self.df2:
            return ''

        # Calc aggregate report for first data frame
        group_by_operation = self.df1.groupby('label')
        result_df1 = group_by_operation['Latency'].agg([np.mean, np.median, percentile90, np.min, np.max, np.sum])
        size = group_by_operation.size()

        result_df1['sum'] = result_df1['sum'].astype(float)
        for i in size.index:
            result_df1['sum'][i] = float(size[i]) / float(result_df1['sum'][i]) * 1000

        result_df1 = result_df1.applymap(lambda x: round(x, 2))
        result_df1.rename(columns={'mean': 'Mean 1, msec',
                                   'median': 'Median 1, msec',
                                   'percentile90': '90% Line 1, msec',
                                   'amin': 'Min 1, msec',
                                   'amax': 'Max 1, msec',
                                   'sum': 'Throughput 1, req/sec'}, inplace=True)

        # Calc aggregate report for second data frame
        group_by_operation = self.df2.groupby('label')
        result_df2 = group_by_operation['Latency'].agg([np.mean, np.median, percentile90, np.min, np.max, np.sum])
        size = group_by_operation.size()

        result_df2['sum'] = result_df2['sum'].astype(float)
        for i in size.index:
            result_df2['sum'][i] = float(size[i]) / float(result_df2['sum'][i]) * 1000

        result_df2 = result_df2.applymap(lambda x: round(x, 2))
        result_df2.rename(columns={'mean': 'Mean 2, msec',
                                   'median': 'Median 2, msec',
                                   'percentile90': '90% Line 2, msec',
                                   'amin': 'Min 2, msec',
                                   'amax': 'Max 2, msec',
                                   'sum': 'Throughput 2, req/sec'}, inplace=True)

        result = result_df1.join(result_df2, how='outer')
        result = result[['Mean 1, msec', 'Mean 2, msec',
                         'Median 1, msec', 'Median 2, msec',
                         '90% Line 1, msec', '90% Line 2, msec',
                         'Min 1, msec', 'Min 2, msec',
                         'Max 1, msec', 'Max 2, msec',
                         'Throughput 1, req/sec', 'Throughput 2, req/sec']]

        xml = etree.XML(result.to_html())
        xml.set('class', 'table table-hover table-striped table-condensed table-responsive table-bordered')
        xml.set('id', 'data')

        paths = {'mean1': ['//table[@id="data"]/tbody/tr/td[1]', '//table[@id="data"]/thead/tr/th[2]'],
                 'mean2': ['//table[@id="data"]/tbody/tr/td[2]', '//table[@id="data"]/thead/tr/th[3]'],
                 'median1': ['//table[@id="data"]/tbody/tr/td[3]', '//table[@id="data"]/thead/tr/th[4]'],
                 'median2': ['//table[@id="data"]/tbody/tr/td[4]', '//table[@id="data"]/thead/tr/th[5]'],
                 '90line1': ['//table[@id="data"]/tbody/tr/td[5]', '//table[@id="data"]/thead/tr/th[6]'],
                 '90line2': ['//table[@id="data"]/tbody/tr/td[6]', '//table[@id="data"]/thead/tr/th[7]'],
                 'min1': ['//table[@id="data"]/tbody/tr/td[7]', '//table[@id="data"]/thead/tr/th[8]'],
                 'min2': ['//table[@id="data"]/tbody/tr/td[8]', '//table[@id="data"]/thead/tr/th[9]'],
                 'max1': ['//table[@id="data"]/tbody/tr/td[9]', '//table[@id="data"]/thead/tr/th[10]'],
                 'max2': ['//table[@id="data"]/tbody/tr/td[10]',  '//table[@id="data"]/thead/tr/th[11]'],
                 'throughput1': ['//table[@id="data"]/tbody/tr/td[11]', '//table[@id="data"]/thead/tr/th[12]'],
                 'throughput2': ['//table[@id="data"]/tbody/tr/td[12]', '//table[@id="data"]/thead/tr/th[13]']}

        for k in paths:
            for path in paths[k]:
                tags = xml.xpath(path)
                for t in tags:
                    t.set('class', k)

        return etree.tostring(xml)