#!/usr/bin/env python

import csv
import numpy as np
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

LOCKDOWN_INTRODUCTION = 27
STAGE_1_LIFTING = 77
STAGE_2_LIFTING = 98
LEVEL_3_BEGIN = 220
LEVEL_3_PLUS_BEGIN = 228
LEVEL_5_BEGIN = 235
CHRISTMANS = 305

def clean_date(date):
    return date.split(' ')[0]

def average(rows, average_over):
    # Needed to last period in N day average 
    # is not less than N days
    extra_fill = len(rows) % average_over
    for i in range(0, extra_fill):
        rows.insert(0, 0)

    b = []
    for i in range(0, len(rows), average_over):
        s = rows[i:i + average_over]
        yield sum(s)/float(len(s))

def args():
    stats = ['deaths', 'cases', 'hospitalisied', 'icu', 'worker']
    stat = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in stats else 'cases'

    if stat == 'cases':
        idx, chart_name = 4, 'Cases'
    if stat == 'deaths':
        idx, chart_name = 6, 'Deaths'
    if stat == 'hospitalisied':
        idx, chart_name = 9, 'Hospitalisied'
    if stat == 'icu':
        idx, chart_name = 10, 'Icu'
    if stat == 'worker':
        idx, chart_name = 11, 'Worker'
    return chart_name, idx

choosen_stat = []
choosen_stat_per_day = []
slope_over_time = [0]
slope_over_time_linear = [0]
max_per_day = 0
average_over = 7
previous_periods_in_projection = 3 # min is 2


stat, idx = args()
with open('CovidStatisticsProfileHPSCIrelandOpenData.csv') as data_file:
    reader = csv.reader(data_file, delimiter=',')
    headers = next(reader)

    last_day_total = 0
    for row in reader:
        cur_day_total = 0 if row[idx] == '' else int(row[idx])
        choosen_stat.append(cur_day_total)
        choosen_stat_per_day.append(cur_day_total - last_day_total)
        if cur_day_total - last_day_total > max_per_day:
            max_per_day = cur_day_total - last_day_total
        last_day_total = cur_day_total

choosen_stat = list(average(choosen_stat, average_over))
choosen_stat_per_period = list(average(choosen_stat_per_day, average_over))
days_since_epoch = range(average_over - 1, len(choosen_stat) * average_over, average_over)

for i in range(1, len(choosen_stat)):
    if choosen_stat[i - 1] == 0:
        slope_over_time.append(0)
        slope_over_time_linear.append(0)
    else:
        rate_of_growth = np.log(float(choosen_stat[i]) / float(choosen_stat[i - 1]))
        slope_over_time.append(rate_of_growth * 100)
        slope_over_time_linear.append((float(choosen_stat[i]) / float(choosen_stat[i - 1]) - 1) * 100)

fig, ax1 = plt.subplots()
plt.title('{} over time (Averaged over {} day(s))'.format(stat, average_over), fontsize=20)

ax1.plot(days_since_epoch, choosen_stat, '.r', label='Total {}'.format(stat.lower()) )
ax1.plot(days_since_epoch, slope_over_time, '.g', label='Rate of change')

plt.legend(loc = 'upper left')

ax1.set_yscale('log')
ax1.set_ylabel('Total number of {}'.format(stat.lower()), fontsize=18)
ax1.set_xlabel('Days since 29 Feb', fontsize=18)

ax2 = ax1.twinx()
ax2.set_yticks([50, 200, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 7000, 8000])

last_3_periods = choosen_stat_per_period[-previous_periods_in_projection::]
ninty_day_prediction = [choosen_stat_per_period[-1]]
r = 0
while len(ninty_day_prediction) < (90. + average_over)/average_over:
    r = (sum(last_3_periods[1::]))/(sum(last_3_periods[:previous_periods_in_projection-1]))
    next_projection = r * last_3_periods[-1]
    ninty_day_prediction.append(next_projection)
    last_3_periods.append(next_projection)
    last_3_periods = last_3_periods[-previous_periods_in_projection::]

r = round(r, 2)

ninty_day_prediction_r5 = [choosen_stat_per_period[-1]]
while len(ninty_day_prediction_r5) < (90. + average_over)/average_over:
    next_projection = 0.6 * ninty_day_prediction_r5[-1]
    ninty_day_prediction_r5.append(next_projection)

ninty_day_prediction_r75 = [choosen_stat_per_period[-1]]
while len(ninty_day_prediction_r75) < (90. + average_over)/average_over:
    next_projection = 0.75 * ninty_day_prediction_r75[-1]
    ninty_day_prediction_r75.append(next_projection)


ax2.plot(days_since_epoch, choosen_stat_per_period, 'b', label ='{} per day'.format(stat))
days_for_projection = [days_since_epoch[-1]]

while len(days_for_projection) < len(ninty_day_prediction):
    days_for_projection.append(days_for_projection[-1] + average_over)

ax2.plot(days_for_projection, ninty_day_prediction, 'b', linestyle='dashed', label ='R {}'.format(r))
ax2.plot(days_for_projection, ninty_day_prediction_r5, 'r', linestyle='dashed', label ='R 0.6')
ax2.plot(days_for_projection, ninty_day_prediction_r75, 'g', linestyle='dashed', label ='R 0.75')

ax2.legend(loc = 'upper right')
plt.ylabel('Number of {} daily'.format(stat.lower()), fontsize=18)

# ax2.plot([LOCKDOWN_INTRODUCTION, LOCKDOWN_INTRODUCTION], [0, max_per_day], 'k-')
# ax2.annotate('Lockdown\nstarts', xy=(LOCKDOWN_INTRODUCTION + 1, max_per_day - max_per_day * .2))

offset = 12
# ax2.plot([STAGE_1_LIFTING, STAGE_1_LIFTING], [0, max_per_day], 'k-')
# ax2.annotate('Phase 1\neasing', xy=(STAGE_1_LIFTING - offset, max_per_day - max_per_day * .2))

# ax2.plot([STAGE_2_LIFTING, STAGE_2_LIFTING], [0, max_per_day], 'k-')
# ax2.annotate('Phase 2\neasing', xy=(STAGE_2_LIFTING - offset, max_per_day - max_per_day * .2))

# ax2.plot([LEVEL_3_BEGIN, LEVEL_3_BEGIN], [0, max_per_day], 'k-')
# ax2.plot([LEVEL_3_BEGIN + 14, LEVEL_3_BEGIN + 14], [0, max_per_day], 'k-', linestyle='dotted')
# ax2.annotate('Level 3', xy=(LEVEL_3_BEGIN - offset, max_per_day - max_per_day * .2))

# ax2.plot([LEVEL_3_PLUS_BEGIN, LEVEL_3_PLUS_BEGIN], [0, max_per_day], 'k-')
# ax2.plot([LEVEL_3_PLUS_BEGIN + 14, LEVEL_3_PLUS_BEGIN + 14], [0, max_per_day], 'k-', linestyle='dotted')
# ax2.annotate('Level 3+', xy=(LEVEL_3_PLUS_BEGIN - offset, max_per_day - max_per_day * .2 - 100))

# ax2.plot([LEVEL_5_BEGIN, LEVEL_5_BEGIN], [0, max_per_day], 'k-')
# ax2.plot([LEVEL_5_BEGIN + 14, LEVEL_5_BEGIN + 14], [0, max_per_day], 'k-', linestyle='dotted')
# ax2.annotate('Level 5', xy=(LEVEL_5_BEGIN - offset, max_per_day - max_per_day * .2))

ax2.plot([CHRISTMANS, CHRISTMANS], [0, max_per_day], 'k-', linestyle='dotted')
ax2.annotate('Christmas', xy=(CHRISTMANS - offset, max_per_day - max_per_day * .2))

ax2.plot([days_since_epoch[-1] + 30, days_since_epoch[-1] + 30], [0, max_per_day], 'k-', linestyle='dotted')
ax2.annotate('+ 30 days', xy=(days_since_epoch[-1] + 30 - offset, max_per_day - max_per_day * .2))

ax2.plot([days_since_epoch[-1] + 60, days_since_epoch[-1] + 60], [0, max_per_day], 'k-', linestyle='dotted')
ax2.annotate('+ 60 days', xy=(days_since_epoch[-1] + 60 - offset, max_per_day - max_per_day * .25))

ax2.plot([days_since_epoch[-1] + 90, days_since_epoch[-1] + 90], [0, max_per_day], 'k-', linestyle='dotted')
ax2.annotate('+ 90 days', xy=(days_since_epoch[-1] + 90 - offset, max_per_day - max_per_day * .2))

plt.grid()
#plt.show()


figure = plt.gcf()  # get current figure
figure.set_size_inches(18, 10)

plt.savefig('out', bbox_inches='tight', pad_inches=.75)