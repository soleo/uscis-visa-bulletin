#!/usr/bin/python3

import urllib.request
import lxml.html
import pandas
import dateutil
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import os


BASEURL = 'https://travel.state.gov'
VISABULLETTINS = BASEURL + '/content/travel/en/legal/visa-law0/visa-bulletin.html'
FY = 2016
def main():
    vb_index = urllib.request.urlopen(VISABULLETTINS).read()
    tree = lxml.html.fromstring(vb_index)

    bulletins = set()
    for link in tree.iterlinks():
        # example of a link: "/content/travel/en/legal/visa-law0/visa-bulletin/2020/visa-bulletin-for-may-2020.html"
        if '/visa-bulletin/' in link[2]:
            # select only Visa Bulletin from a few latest fiscal years
            # Note: US Govt FYs starts on October, and they are part of the URL components
            if int(link[2].split('/')[7]) >= FY:
                bulletins.add(BASEURL + link[2])

    file_dates_eb2 = dict()
    file_dates_eb3 = dict()

    for bulletin in bulletins:
        # the month the bulletin refers to
        current_month = dateutil.parser.parse('1 ' + bulletin.split('/')[-1].replace('visa-bulletin-for-', '').replace('.html', ''))

        data = pandas.read_html(bulletin)
        for table in data:
            # there are multiple tables, we care about only the first one about "Employment-based" sponsorship
            if 'employment' in table[0][0].lower():
                # get only the EB2/3 for "China"
                file_date_china_eb2 = table[2][2]
                file_date_china_eb3 = table[2][3]
                if file_date_china_eb2 == 'C':
                    file_dates_eb2[current_month] = current_month
                    file_dates_eb3[current_month] = current_month
                else:
                    file_dates_eb2[current_month] = dateutil.parser.parse(file_date_china_eb2)
                    file_dates_eb3[current_month] = dateutil.parser.parse(file_date_china_eb3)
                break

    # generate the EB2 graphs
    plt_locator = mdates.MonthLocator(interval=2)
    plt_formatter = mdates.AutoDateFormatter(plt_locator)
    fig, ax = plt.subplots()
    fig.set_size_inches(16, 10)
    ax.xaxis.set_major_locator(plt_locator)
    ax.xaxis.set_major_formatter(plt_formatter)
    plt.title(f"Waiting time (in months) for filing EB2/3; FY {FY} to current")
    ax.set_ylabel('Months')
    ax.set_xlabel('Visa Bulletin Date')

    ax.plot(sorted(file_dates_eb2.keys()), [(date - file_dates_eb2[date]).days // 30 for date in sorted(file_dates_eb2.keys())], label='EB2 waiting time w final action date')
    ax.plot(sorted(file_dates_eb3.keys()), [(date - file_dates_eb3[date]).days // 30 for date in sorted(file_dates_eb3.keys())], label='EB3 waiting time w final action date')

    plt.xticks(rotation=18, ha='right')
    plt.grid()
    fig.tight_layout()
    ax.legend(loc='upper left')
    os.makedirs('images', exist_ok=True)
    plt.savefig('images/EB2_3.svg')

if __name__ == 'main':
    main()
