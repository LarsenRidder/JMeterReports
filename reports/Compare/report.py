import math
import numpy as np
import pandas as pd
from lxml import etree

from lib.basereport import BaseReport
from lib.utils import percentile90, trend
import matplotlib.pyplot as plt
import pylab as pl
from matplotlib import rc
from mpltools import style


class CompareReport(BaseReport):
    """Compare JMeter report.
    Compare Mean, Median, 90% Line, Max, Min and Throughput by label.
    """

    def read_csv(self, file_paths):
        self.df1 = pd.read_csv(file_paths[0])
        self.df2 = pd.read_csv(file_paths[1])

    def _generate_html_data(self):
        if not hasattr(self, 'df1') or self.df1.empty:
            return ''
        if not hasattr(self, 'df2') or self.df2.empty:
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
        result['Mean trend, %'] = result[['Mean 1, msec', 'Mean 2, msec']].apply(trend, axis=1)
        result['Median trend, %'] = result[['Median 1, msec', 'Median 2, msec']].apply(trend, axis=1)
        result['90% Line trend, %'] = result[['90% Line 1, msec', '90% Line 2, msec']].apply(trend, axis=1)

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
                 'max2': ['//table[@id="data"]/tbody/tr/td[13]', '//table[@id="data"]/thead/tr/th[14]'],
                 'throughput1': ['//table[@id="data"]/tbody/tr/td[14]', '//table[@id="data"]/thead/tr/th[15]'],
                 'throughput2': ['//table[@id="data"]/tbody/tr/td[15]', '//table[@id="data"]/thead/tr/th[16]']}

        for k in paths:
            for path in paths[k]:
                tags = xml.xpath(path)
                for t in tags:
                    t.set('class', k)

        for t in xml.xpath('//table[@id="data"]/tbody/tr'):
            req_name = self._normalize_test_name(t[0].text)
            t.set('data-toggle', 'collapse')
            t.set('data-target', '#' + req_name)
            t.set('class', 'accordion-toggle')
            t.addnext(etree.XML('<tr>'
                                    '<td colspan="10" class="hiddenRow nohover">'
                                        '<div id="' + req_name + '" class="accordian-body collapse">'
                                            '<img src="plots/' + req_name + '_hist_prob_all.png"/>'
                                            '<img src="plots/' + req_name + '_hist_prob_90line.png"/>'
                                            '<img src="plots/' + req_name + '_requests.png"/>'
                                        '</div>'
                                    '</td>'
                                 '</tr>'))

        return etree.tostring(xml)

    def _generate_plots(self, report_name):
        """

        :param report_name:
        """
        font = {'size': '8'}
        #'family' : 'monospace',
        #'weight' : 'bold',
        rc('font', **font)
        style.use('ggplot')

        l1 = self.df1['Latency']
        l2 = self.df2['Latency']

        plt.figure(figsize=(8, 5), dpi=150)
        plt.hist(l1,
                 bins=math.pow(len(l1), float(1) / 3),
                 normed=True,
                 color=['g'],
                 fill=True,
                 alpha=0.40,
                 histtype='step',
                 label='1')
        plt.hist(l2,
                 bins=math.pow(len(l1), float(1) / 3),
                 normed=True,
                 color=['g'],
                 fill=True,
                 alpha=0.40,
                 histtype='step',
                 label='2')
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tick_params(axis='both', which='minor', labelsize=6)
        plt.legend()
        plt.xlabel('Response time', fontsize=9)
        plt.ylabel('Probability', fontsize=9)
        plt.title('Histogram of all response time', fontsize=10)
        plt.tight_layout()
        plt.savefig('results/' + report_name + '/plots/hist_prob_all.png')
        plt.close()

        plt.figure(figsize=(8, 5), dpi=150)
        l1_90 = l1[l1 < np.percentile(l1, 90)].reset_index(drop=True)
        l2_90 = l2[l2 < np.percentile(l2, 90)].reset_index(drop=True)
        plt.hist(l1_90,
                 bins=math.pow(len(l1_90), float(1) / 3),
                 normed=True,
                 color=['g'],
                 fill=True,
                 alpha=0.40,
                 histtype='step',
                 label='1')
        plt.hist(l2_90,
                 bins=math.pow(len(l2_90), float(1) / 3),
                 normed=True,
                 color=['g'],
                 fill=True,
                 alpha=0.40,
                 histtype='step',
                 label='2')
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tick_params(axis='both', which='minor', labelsize=6)
        plt.legend()
        plt.xlabel('Response time', fontsize=9)
        plt.ylabel('Probability', fontsize=9)
        plt.title('Histogram of 90% line response time', fontsize=10)
        plt.tight_layout()
        plt.savefig('results/' + report_name + '/plots/hist_prob_90line.png')
        plt.close()

        # generate compare plots for tests
        # this code is ugly
        x1 = self.df1.loc[:, ['label', 'Latency']]
        x1 = x1.groupby('label')
        x1m = x1['Latency'].agg([np.mean, np.std])

        x2 = self.df2.loc[:, ['label', 'Latency']]
        x2 = x2.groupby('label')
        x2m = x2['Latency'].agg([np.mean, np.std])

        df = x1m.join(x2m, how='outer', lsuffix='1', rsuffix='2')
        for label, data in df.iterrows():
            file_name = self._normalize_test_name(label)
            if not pd.isnull(data['mean1']):
                d1 = x1.get_group(label)['Latency']
            if not pd.isnull(data['mean2']):
                d2 = x2.get_group(label)['Latency']

            if not pd.isnull(data['mean1']) or not pd.isnull(data['mean2']):
                plt.figure(figsize=(6, 4))
                if not pd.isnull(data['mean1']):
                    d1.hist(normed=True, alpha=0.2, label='1')
                    d1.plot(kind='kde', label='1')

                if not pd.isnull(data['mean2']):
                    d2.hist(normed=True, alpha=0.2, label='2')
                    d2.plot(kind='kde', label='2')

                # if not pd.isnull(data['mean1']) and not pd.isnull(data['mean2']):
                #     l = len(d1) if len(d1) > len(d2) else len(d2)
                #     n, bins, patches = plt.hist([d1, d2],
                #                                 bins=math.pow(l, float(1) / 3),
                #                                 normed=1,
                #                                 alpha=0.60,
                #                                 label=['1', '2'],
                #                                 color=['g', 'b'])
                #     #plt.plot(bins, pl.normpdf(bins, np.mean(d1), np.std(d1)), 'r--', color='g', label='norm1', linewidth=2)
                #     #plt.plot(bins, pl.normpdf(bins, np.mean(d2), np.std(d2)), 'r--', color='b', label='norm2', linewidth=2)
                # elif not pd.isnull(data['mean1']):
                #     n, bins, patches = plt.hist(d1,
                #                                 bins=math.pow(len(d1), float(1) / 3),
                #                                 normed=1,
                #                                 alpha=0.60,
                #                                 label='1',
                #                                 color='g')
                #     plt.plot(bins, pl.normpdf(bins, np.mean(d1), np.std(d1)), 'r--', color='g', label='norm1', linewidth=2)
                # elif not pd.isnull(data['mean2']):
                #     n, bins, patches = plt.hist(d2,
                #                                 bins=math.pow(len(d2), float(1) / 3),
                #                                 normed=1,
                #                                 alpha=0.60,
                #                                 label='2',
                #                                 color='b')
                #     plt.plot(bins, pl.normpdf(bins, np.mean(d2), np.std(d2)), 'r--', color='g', label='norm2', linewidth=2)
                plt.legend()
                plt.xlabel('Response time', fontsize=9)
                plt.ylabel('Probability', fontsize=9)
                plt.title('Histogram of all response time', fontsize=10)
                plt.tick_params(axis='both', which='major', labelsize=8)
                plt.tick_params(axis='both', which='minor', labelsize=6)
                plt.tight_layout()
                plt.savefig('results/' + report_name + '/plots/' + file_name + '_hist_prob_all.png')
                plt.close()

                plt.figure(figsize=(6, 4))
                if not pd.isnull(data['mean1']):
                    d1[d1 < np.percentile(d1, 90)].hist(normed=True, alpha=0.2, label='1')
                    try:
                        d1[d1 < np.percentile(d1, 90)].plot(kind='kde', label='1')
                    except np.linalg.linalg.LinAlgError:
                        pass
                        # if singular matrix - no plot
                    except:
                        raise

                if not pd.isnull(data['mean2']):
                    d2[d2 < np.percentile(d2, 90)].hist(normed=True, alpha=0.2, label='2')
                    try:
                        d2[d2 < np.percentile(d2, 90)].plot(kind='kde', label='2')
                    except np.linalg.linalg.LinAlgError:
                        pass
                        # if singular matrix - no plot
                    except:
                        raise
                # if not pd.isnull(data['mean1']) and not pd.isnull(data['mean2']):
                #     l = len(d1) if len(d1) > len(d2) else len(d2)
                #     n, bins, patches = plt.hist([d1[d1 < np.percentile(d1, 90)], d2[d2 < np.percentile(d2, 90)]],
                #                                 bins=math.pow(l, float(1) / 3),
                #                                 normed=1,
                #                                 alpha=0.60,
                #                                 label=['1', '2'],
                #                                 color=['g', 'b'])
                #     plt.plot(bins, pl.normpdf(bins, np.mean(d1[d1 < np.percentile(d1, 90)]), np.std(d1[d1 < np.percentile(d1, 90)])), 'r--', color='g', label='norm1', linewidth=2)
                #     plt.plot(bins, pl.normpdf(bins, np.mean(d2[d2 < np.percentile(d2, 90)]), np.std(d2[d2 < np.percentile(d2, 90)])), 'r--', color='b', label='norm2', linewidth=2)
                # elif not pd.isnull(data['mean1']):
                #     n, bins, patches = plt.hist(d1[d1 < np.percentile(d1, 90)],
                #                                 bins=math.pow(len(d1[d1 < np.percentile(d1, 90)]), float(1) / 3),
                #                                 normed=1,
                #                                 alpha=0.60,
                #                                 label='1',
                #                                 color='g')
                #     plt.plot(bins, pl.normpdf(bins, np.mean(d1[d1 < np.percentile(d1, 90)]), np.std(d1[d1 < np.percentile(d1, 90)])), 'r--', color='g', label='norm1', linewidth=2)
                # elif not pd.isnull(data['mean2']):
                #     n, bins, patches = plt.hist(d2[d2 < np.percentile(d2, 90)],
                #                                 bins=math.pow(len(d2[d2 < np.percentile(d2, 90)]), float(1) / 3),
                #                                 normed=1,
                #                                 alpha=0.60,
                #                                 label='2',
                #                                 color='b')
                #     plt.plot(bins, pl.normpdf(bins, np.mean(d2[d2 < np.percentile(d2, 90)]), np.std(d2[d2 < np.percentile(d2, 90)])), 'r--', color='g', label='norm2', linewidth=2)
                plt.legend()
                plt.xlabel('Response time', fontsize=9)
                plt.ylabel('Probability', fontsize=9)
                plt.title('Histogram of 90% line response time', fontsize=10)
                plt.tick_params(axis='both', which='major', labelsize=8)
                plt.tick_params(axis='both', which='minor', labelsize=6)
                plt.tight_layout()
                plt.savefig('results/' + report_name + '/plots/' + file_name + '_hist_prob_90line.png')
                plt.close()

                plt.figure(figsize=(6, 4), dpi=150)
                if not pd.isnull(data['mean1']):
                    plt.plot(range(1, len(d1) + 1), d1, 'ro', color='g', alpha=0.50, label='1')
                if not pd.isnull(data['mean2']):
                    plt.plot(range(1, len(d2) + 1), d2, 'ro', color='b', alpha=0.50, label='2')
                plt.legend()
                plt.xlabel('Request', fontsize=9)
                plt.ylabel('Time', fontsize=9)
                plt.title('Requests time', fontsize=10)
                plt.tick_params(axis='both', which='major', labelsize=8)
                plt.tick_params(axis='both', which='minor', labelsize=6)
                plt.tight_layout()
                plt.savefig('results/' + report_name + '/plots/' + file_name + '_requests.png')
                plt.close()