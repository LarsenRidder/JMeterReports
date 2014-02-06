import numpy as np
from lxml import etree
import matplotlib.pyplot as plt

from lib.basereport import BaseReport
from lib.utils import percentile60, percentile70, percentile80, percentile90


class PercentilesReport(BaseReport):
    """Aggregate JMeter report.
    Calculate Mean, Median, 90% Line, Max, Min and Throughput by label.
    """

    def _generate_html_data(self):
        if not hasattr(self, 'df') or not self.df:
            return ''

        # group data by 'label' field. this data use in plot generation.
        self._group_by_operation = self.df.groupby('label')
        # calc statistic by operation
        result = self._group_by_operation['Latency'].agg([np.median, percentile60, percentile70, percentile80, percentile90])
        size = self._group_by_operation.size()

        result = result.applymap(lambda x: round(x, 2))

        # rename columns
        result.rename(columns={'median': '50% Line, msec',
                               'percentile60': '60% Line, msec',
                               'percentile70': '70% Line, msec',
                               'percentile80': '80% Line, msec',
                               'percentile90': '90% Line, msec'}, inplace=True)

        xml = etree.XML(result.to_html())
        xml.set('class', 'table table-hover table-condensed table-responsive table-bordered')
        xml.set('id', 'data')

        paths = {'50line': ['//table[@id="data"]/tbody/tr/td[1]', '//table[@id="data"]/thead/tr/th[2]'],
                 '60line': ['//table[@id="data"]/tbody/tr/td[2]', '//table[@id="data"]/thead/tr/th[3]'],
                 '70line': ['//table[@id="data"]/tbody/tr/td[3]', '//table[@id="data"]/thead/tr/th[4]'],
                 '80line': ['//table[@id="data"]/tbody/tr/td[4]', '//table[@id="data"]/thead/tr/th[5]'],
                 '90line': ['//table[@id="data"]/tbody/tr/td[5]', '//table[@id="data"]/thead/tr/th[6]']}

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
                                    '<td colspan="8" class="hiddenRow nohover">'
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
        """

        :param report_name:
        """
        for label, data in self._group_by_operation:
            file_name = self._normalize_test_name(label)
            d = data['Latency']

            plt.figure(figsize=(6, 4))
            d.hist(color='g', normed=1, facecolor='g', alpha=0.50, bins=100)

            plt.xlabel('Response time')
            plt.ylabel('Probability')
            plt.title('Histogram of all response time')
            plt.tight_layout()
            plt.savefig('results/' + report_name + '/plots/' + file_name + '_hist_prob_all.png')
            plt.close()

            plt.figure(figsize=(6, 4), dpi=150)
            d[d < np.percentile(d, 90)].hist(color='g', normed=1, facecolor='g', alpha=0.50, bins=60)
            plt.xlabel('Response time')
            plt.ylabel('Probability')
            plt.title('Histogram of 90% line response time')
            plt.tight_layout()
            plt.savefig('results/' + report_name + '/plots/' + file_name + '_hist_prob_90line.png')
            plt.close()

            plt.figure(figsize=(6, 4), dpi=150)
            a = data['Latency']
            plt.plot(range(1, len(a) + 1), a, 'ro', color='g', alpha=0.50)
            plt.xlabel('Request')
            plt.ylabel('Time')
            plt.title('Requests times')
            plt.tight_layout()
            plt.savefig('results/' + report_name + '/plots/' + file_name + '_requests.png')
            plt.close()
