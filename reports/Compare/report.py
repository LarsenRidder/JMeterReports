import numpy as np
import pandas as pd
from lxml import etree

from lib.basereport import BaseReport
from lib.utils import percentile90, trend


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

        result_df2.rename(columns={'mean': 'Mean 2, msec',
                                   'median': 'Median 2, msec',
                                   'percentile90': '90% Line 2, msec',
                                   'amin': 'Min 2, msec',
                                   'amax': 'Max 2, msec',
                                   'sum': 'Throughput 2, req/sec'}, inplace=True)

        result = result_df1.join(result_df2, how='outer')

        # calc trend for mean, median, 90% line
        result['Mean trend, %'] = result[['Mean 1, msec','Mean 2, msec']].apply(trend, axis=1)
        result['Median trend, %'] = result[['Median 1, msec','Median 2, msec']].apply(trend, axis=1)
        result['90% Line trend, %'] = result[['90% Line 1, msec','90% Line 2, msec']].apply(trend, axis=1)

        # reorder columns
        result = result.applymap(lambda x: round(x, 2))
        result = result[['Mean 1, msec', 'Mean 2, msec', 'Mean trend, %',
                         'Median 1, msec', 'Median 2, msec', 'Median trend, %',
                         '90% Line 1, msec', '90% Line 2, msec', '90% Line trend, %',
                         'Min 1, msec', 'Min 2, msec',
                         'Max 1, msec', 'Max 2, msec',
                         'Throughput 1, req/sec', 'Throughput 2, req/sec']]

        # generate html table, parse and add bootstrap classes
        xml = etree.XML(result.to_html())
        xml.set('class', 'table table-hover table-striped table-condensed table-responsive table-bordered')
        xml.set('id', 'data')

        # add classes for columns, for fast select in jquery
        paths = {'mean1': ['//table[@id="data"]/tbody/tr/td[1]', '//table[@id="data"]/thead/tr/th[2]'],
                 'mean2': ['//table[@id="data"]/tbody/tr/td[2]', '//table[@id="data"]/thead/tr/th[3]'],
                 'mean_trend': ['//table[@id="data"]/tbody/tr/td[3]', '//table[@id="data"]/thead/tr/th[4]'],
                 'median1': ['//table[@id="data"]/tbody/tr/td[4]', '//table[@id="data"]/thead/tr/th[5]'],
                 'median2': ['//table[@id="data"]/tbody/tr/td[5]', '//table[@id="data"]/thead/tr/th[6]'],
                 'median_trend': ['//table[@id="data"]/tbody/tr/td[6]', '//table[@id="data"]/thead/tr/th[7]'],
                 'line901': ['//table[@id="data"]/tbody/tr/td[7]', '//table[@id="data"]/thead/tr/th[8]'],
                 'line902': ['//table[@id="data"]/tbody/tr/td[8]', '//table[@id="data"]/thead/tr/th[9]'],
                 'line90_trend': ['//table[@id="data"]/tbody/tr/td[9]', '//table[@id="data"]/thead/tr/th[10]'],
                 'min1': ['//table[@id="data"]/tbody/tr/td[10]', '//table[@id="data"]/thead/tr/th[11]'],
                 'min2': ['//table[@id="data"]/tbody/tr/td[11]', '//table[@id="data"]/thead/tr/th[12]'],
                 'max1': ['//table[@id="data"]/tbody/tr/td[12]', '//table[@id="data"]/thead/tr/th[13]'],
                 'max2': ['//table[@id="data"]/tbody/tr/td[13]',  '//table[@id="data"]/thead/tr/th[14]'],
                 'throughput1': ['//table[@id="data"]/tbody/tr/td[14]', '//table[@id="data"]/thead/tr/th[15]'],
                 'throughput2': ['//table[@id="data"]/tbody/tr/td[15]', '//table[@id="data"]/thead/tr/th[16]']}

        for k in paths:
            for path in paths[k]:
                tags = xml.xpath(path)
                for t in tags:
                    t.set('class', k)

        return etree.tostring(xml)