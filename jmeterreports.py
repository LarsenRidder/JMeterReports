__author__ = 'Evgeny.Luvsandugar'

import argparse

parser = argparse.ArgumentParser(description='JMeter report generator')
parser.add_argument('name', metavar='REPORT_NAME', type=str, help='Report name')
parser.add_argument('data_file', metavar='DATA_FILE', type=str,
                    help='Path to JMeter jtl report (from aggregate report or simple data writer)')

args = parser.parse_args()


