#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser
import glob
import sys
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib # these three lines were added so that my linux sybsystem won't try to make these interactive 
matplotlib.use('agg')
plt.ioff()
from matplotlib.collections import LineCollection

args = ArgumentParser('./visualize_cgm.py', description="""This program has been designed 
                      to create graphs from CGM data. We have been using the Dexcom G6, but the file
                      formats from other devices could be changed to mirror this input type. The required
                      columns are 'Timestamp' (which has unfortunately been changed by Excel for the 
                      ones that we obtained), 'Event Type' (only values with 'EGV' are used), and 
                      'Glucose Value (mg/dL)'.  
                      Example usage: ./visualize_cgm.py -i 100_1_cgm.csv""")

args.add_argument(
	'-i',
	'--input_file',
	help="""
	This is the csv that visualize_cgm.py will read to create the graphs. 
	""",
	default=None
)

args.add_argument(
	'-o',
	'--output',
	help="""
	This is the name of the output folder and the prefix for the png files.
    If no output is specified, the header for the input file will be used. 
	""",
	default=None
)

args = args.parse_args()
input_file = args.input_file
output = args.output

def error_message():
    print()
    print("""\tWelcome to visualize_cgm.py. This program has been designed to create graphs from CGM data.
\tWe have been using the Dexcom G6, but the file formats from other devices could be changed
\tto mirror this input type. The required columns are 'Timestamp' (which has unfortunately been
\tchanged by Excel for the ones that we obtained), 'Event Type' (only values with 'EGV' are used), and
\t'Glucose Value (mg/dL)'.
          """)
    print("\tExample usage: ./visualize_cgm.py -i 100_1_cgm.csv")
    print()

if not input_file:
    error_message()
    print("\tYou have not specified an input csv format file. Please specify an input file with the -i option.")
    print()
    current_csv_files = glob.glob('*.csv')
    if len(current_csv_files) > 0:
        print("\tThe current files in your current working directory are possibly the correct format:")
        print()
        print(current_csv_files)
        print()
    sys.exit(1)

if not input_file.endswith('.csv'):
    error_message()
    print("\tThe input file that you have entered is not in csv format. Please specify an input csv file with the -i option.")
    print()
    current_csv_files = glob.glob('*.csv')
    if len(current_csv_files) > 0:
        print("\tThe current files in your current working directory are possibly the correct format:")
        print()
        print(current_csv_files)
        print()
    sys.exit(1)

if not output:
    output = input_file.removesuffix('.csv')

cgm_df = pd.read_csv(input_file)
cgm_df = cgm_df[cgm_df['Event Type'] == 'EGV'] # remove any of the rows that don't show glucose values
glucose_values = cgm_df['Glucose Value (mg/dL)'].values # If any "Low" or "High" values exist, change them to numbers
if 'Low' in glucose_values or 'High' in glucose_values:
    new_list = []
    for value in glucose_values:
        if value.isdigit():
            new_list.append(int(value))
        elif value == 'Low':
            new_list.append(40) 
        elif value == 'High':
            new_list.append(400) 
        else:
            new_list.append('') 
    cgm_df['Glucose Value (mg/dL)'] = new_list

weekday_dict = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}
def split_datetime(row):
    string_format = row['Timestamp (YYYY-MM-DDThh:mm:ss)']
    dt_object = datetime.strptime(string_format, '%m/%d/%Y %H:%M')
    year = dt_object.year
    month = dt_object.month
    day = dt_object.day
    str_year = str(year)
    str_month = str(month)
    if len(str_month) == 1:
        str_month = '0'+str_month
    str_day = str(day)
    if len(str_day) == 1:
        str_day = '0'+str_day
    row['year'] = year
    row['month'] = month
    row['day'] = day
    row['hour'] = dt_object.hour
    row['minute'] = dt_object.minute
    weekday_str = weekday_dict[dt_object.weekday()]
    row['weekday'] = weekday_str

    row['date'] = str_year+'_'+str_month+'_'+str_day+' '+weekday_str
    return row

cgm_df = cgm_df.apply(split_datetime, axis = 1)
days = sorted(set(cgm_df['date'].values))

num_subplots = len(days)
plt.rcParams["figure.figsize"] = (22,4*num_subplots)
fig, ax = plt.subplots(num_subplots)

for subplot_index, day in enumerate(days):
    tmp_df = cgm_df[cgm_df['date'] == day]
    glucose_list = tmp_df['Glucose Value (mg/dL)'].values
    hour_list = tmp_df['hour'].values
    minute_list = tmp_df['minute'].values
    line_segments = []
    colors = []
    for i in range(len(glucose_list)-1):
        x1 = 60*hour_list[i]+minute_list[i]
        x2 = 60*hour_list[i+1]+minute_list[i+1]
        y1 = glucose_list[i]
        y2 = glucose_list[i+1]
        line_segments.append([[x1,y1], [x2,y2]])
        output_color = 'black'
        if min(y1, y2) < 70:
            output_color = 'blue'
        if min(y1, y2) < 50:
            output_color = 'red'
        elif max(y1,y2) > 180:
            output_color = 'blue'
        elif max(y1, y2) > 200:
            output_color = 'red'
        colors.append(output_color)

    line_segments2 = LineCollection(line_segments, linestyles='solid', colors=colors, linewidth=3)#, alpha=0.3)
    ax[subplot_index].add_collection(line_segments2)
    ax[subplot_index].set_xlim([0, 1440])
    ax[subplot_index].set_ylim([30, 200])
    ax[subplot_index].axvline(x=360, color='orange', linestyle='dashed')
    ax[subplot_index].axvline(x=720, color='orange', linestyle='dashed')
    ax[subplot_index].axvline(x=1080, color='orange', linestyle='dashed')
    ax[subplot_index].axhline(y=100, color='orange', linestyle='dashed')
    ax[subplot_index].axhline(y=70, color='blue', linestyle='dashed')
    ax[subplot_index].axhline(y=50, color='red', linestyle='dashed')
    ax[subplot_index].axhline(y=180, color='blue', linestyle='dashed')
    ax[subplot_index].set(ylabel=day)
plt.savefig(output+'.png')
