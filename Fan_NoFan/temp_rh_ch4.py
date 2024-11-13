# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 12:26:44 2024

@author: Anthony Macias
"""

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
#import pytz
#from matplotlib.ticker import MaxNLocator
import numpy as np
import matplotlib.dates as mdates

# Load data
df1 = pd.read_excel('03_shinyout_10_29.xlsx')
df2 = pd.read_excel('10_29_LICOR.xlsx', skiprows=7)
df3 = pd.read_excel('13_shinyout_10_29.xlsx')

# Adjust time by subtracting 7 hours for PDT (if necessary)
def adjust_to_pdt(df, time_column):
    df['PDT_Time'] = pd.to_datetime(df[time_column], unit='s') - timedelta(hours=7)
    return df

# Apply time adjustment to each DataFrame
df1 = adjust_to_pdt(df1, df1.columns[6])  # Assumes time is in the 7th column
df2 = adjust_to_pdt(df2, df2.columns[1])  # Assumes time is in the 2nd column
df3 = adjust_to_pdt(df3, df3.columns[6])  # Assumes time is in the 7th column

# Convert Methane columns to numeric [ppb]
df1['Methane_Concentration'] = 1000 * pd.to_numeric(df1.iloc[:, 4], errors='coerce')
df2['Methane_Concentration'] = pd.to_numeric(df2.iloc[:, 10], errors='coerce')
df3['Methane_Concentration'] = 1000 * pd.to_numeric(df3.iloc[:, 4], errors='coerce')

# Convert Temperature and Humidity columns to numeric
df1['Temperature'] = pd.to_numeric(df1.iloc[:, 2], errors='coerce')
df3['Temperature'] = pd.to_numeric(df3.iloc[:, 2], errors='coerce')
df1['Humidity'] = pd.to_numeric(df1.iloc[:, 1], errors='coerce')
df3['Humidity'] = pd.to_numeric(df3.iloc[:, 1], errors='coerce')

# Filter the datasets for the desired intervals
start_time = "15:00:00"
end_time = "15:30:00"
df1_filtered = df1[(df1['PDT_Time'].dt.strftime('%H:%M:%S') >= start_time) & (df1['PDT_Time'].dt.strftime('%H:%M:%S') <= end_time)]
df2_filtered = df2[(df2['PDT_Time'].dt.strftime('%H:%M:%S') >= start_time) & (df2['PDT_Time'].dt.strftime('%H:%M:%S') <= end_time)]
df3_filtered = df3[(df3['PDT_Time'].dt.strftime('%H:%M:%S') >= start_time) & (df3['PDT_Time'].dt.strftime('%H:%M:%S') <= end_time)]

# Adjust Sensor 03's time by subtracting 6 minutes
df1_filtered['PDT_Time'] = df1_filtered['PDT_Time'] - pd.Timedelta(minutes=7.5)

# Downsample LICOR (every other row)
df2_everyother = df2_filtered.iloc[::1, :]

# Function to calculate the average slope
def calculate_average_slope(data):
    time_ordinal = np.arange(len(data))
    slope, _ = np.polyfit(time_ordinal, data.values, 1)
    return slope

# Calculate slopes for each dataset
avg_slope_03 = calculate_average_slope(df1_filtered['Methane_Concentration'])
avg_slope_LICOR = calculate_average_slope(df2_everyother['Methane_Concentration'])
avg_slope_13 = calculate_average_slope(df3_filtered['Methane_Concentration'])

# Set up the figure with two subplots
fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(18, 12))

# Plot Methane Concentration (first subplot)
ax1.plot(df1_filtered['PDT_Time'], df1_filtered['Methane_Concentration'], marker='o', linestyle='-', color='r', label='Sensor 03')
#ax1.plot(df2_everyother['PDT_Time'], df2_everyother['Methane_Concentration'], marker='o', linestyle='-', color='g', label='LICOR')
ax1.plot(df3_filtered['PDT_Time'], df3_filtered['Methane_Concentration'], marker='o', linestyle='-', color='b', label='Sensor 13')

# Set labels and title
ax1.set_xlabel('Time (PDT)')
ax1.set_ylabel('Methane Concentration [ppb]')
ax1.set_title('Methane Concentration vs. Time with Humidity')
ax1.grid(True)

# Format x-axis labels as HH:MM
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.xticks(rotation=45)
ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))

# Secondary y-axis for Temperature with transparency
ax2 = ax1.twinx()
ax2.plot(df1_filtered['PDT_Time'], df1_filtered['Temperature'], marker='x', linestyle='--', color='red', label='Sensor 03 Temperature', alpha=0.1)
ax2.plot(df3_filtered['PDT_Time'], df3_filtered['Temperature'], marker='x', linestyle='--', color='blue', label='Sensor 13 Temperature', alpha=0.1)
ax2.set_ylabel('Temperature [°C]')

# Display average slopes
#ax1.text(0.5, 0.85, f'LICOR Slope [ppb/s]: {avg_slope_LICOR:.4f}', 
         #horizontalalignment='center', verticalalignment='top',
         #fontsize=12, color='green', transform=ax1.transAxes)
ax1.text(0.5, 0.75, f'Sensor 03 Slope [ppb/s]: {avg_slope_03:.4f}', 
         horizontalalignment='center', verticalalignment='top',
         fontsize=12, color='red', transform=ax1.transAxes)
ax1.text(0.5, 0.65, f'Sensor 13 Slope [ppb/s]: {avg_slope_13:.4f}', 
         horizontalalignment='center', verticalalignment='top',
         fontsize=12, color='blue', transform=ax1.transAxes)

# Show legends for both y-axes in the first subplot
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Second subplot for Methane Concentration and Humidity
ax3.plot(df1_filtered['PDT_Time'], df1_filtered['Methane_Concentration'], marker='o', linestyle='-', color='r', label='Sensor 03 Methane')
ax3.plot(df3_filtered['PDT_Time'], df3_filtered['Methane_Concentration'], marker='o', linestyle='-', color='b', label='Sensor 13 Methane')

# Set labels and title for the second subplot
ax3.set_xlabel('Time (PDT)')
ax3.set_ylabel('Methane Concentration [ppb]')
ax3.set_title('Methane Concentration vs. Time with Humidity')
ax3.grid(True)

# Format x-axis labels as HH:MM
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.xticks(rotation=45)
ax3.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))

# Secondary y-axis for Humidity
ax4 = ax3.twinx()
ax4.plot(df1_filtered['PDT_Time'], df1_filtered['Humidity'], marker='x', linestyle='--', color='red', label='Sensor 03 Humidity', alpha=0.1)
ax4.plot(df3_filtered['PDT_Time'], df3_filtered['Humidity'], marker='x', linestyle='--', color='blue', label='Sensor 13 Humidity', alpha=0.1)
ax4.set_ylabel('Humidity [%]')

# Show legends for both y-axes in the second subplot
ax3.legend(loc='upper left')
ax4.legend(loc='upper right')

plt.tight_layout()
plt.show()
