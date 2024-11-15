"""
Created on Thu Aug 29 09:34:07 2024

@author: Anthony Macias
"""
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import pytz
from matplotlib.ticker import MaxNLocator
import numpy as np

# Load the Excel files
df1 = pd.read_excel('OC15_Octo.xlsx')
#df2 = pd.read_excel('OC45_LICOR_AM.xlsx', skiprows=7)
#df3 = pd.read_excel('Extension_OC45.xlsx')

# Define timezone
pdt_zone = pytz.timezone('America/Los_Angeles')

# Function to convert Unix epoch time to PDT
def epoch_to_pdt_time(epoch_time):
    date_obj = datetime.utcfromtimestamp(epoch_time)
    return date_obj.astimezone(pdt_zone).strftime("%H:%M:%S")

# Convert the time columns
df1['PDT_Time'] = pd.to_datetime(df1.iloc[:, 6], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.strftime('%H:%M:%S')
#df2['PDT_Time'] = pd.to_datetime(df2.iloc[:, 1], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.strftime('%H:%M:%S')
#df3['PDT_Time'] = pd.to_datetime(df3.iloc[:, 6], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.strftime('%H:%M:%S')
print(df1['PDT_Time'].head())
#print(df2['PDT_Time'].head())
#print(df3['PDT_Time'].head())

# Convert Methane columns to numeric, Make Extension data ppb
df1['Methane_Concentration'] = pd.to_numeric(df1.iloc[:, 4], errors='coerce')
#df2['Methane_Concentration'] = pd.to_numeric(df2.iloc[:, 10], errors='coerce')
#df3['Methane_Concentration'] = 1000*pd.to_numeric(df3.iloc[:, 4], errors='coerce')

# Filter the datasets for the desired intervals
df1_filtered = df1[(df1['PDT_Time'] >= '10:30:00') & (df1['PDT_Time'] <= '16:00:00')]
#df2_filtered = df2[(df2['PDT_Time'] >= '10:47:00') & (df2['PDT_Time'] <= '10:55:00')]
#df3_filtered = df3[(df3['PDT_Time'] >= '10:47:00') & (df3['PDT_Time'] <= '10:55:00')]

# Downsample LICOR (every other row)
#df2_everyother = df2_filtered.iloc[::2, :]

def calculate_average_slope(data):
    time_ordinal = np.arange(len(data))
    slope, _ = np.polyfit(time_ordinal, data.values, 1)
    return slope

# Calculate slopes for each dataset
avg_slope_octo = calculate_average_slope(df1_filtered['Methane_Concentration'])
#avg_slope_LICOR = calculate_average_slope(df2_everyother['Methane_Concentration'])
#avg_slope_extension = calculate_average_slope(df3_filtered['Methane_Concentration'])

# Set Figure Size
plt.figure(figsize=(18, 6))

# Plot the Octo Data
plt.subplot(1, 2, 1)
plt.plot(df1_filtered['PDT_Time'], df1_filtered['Methane_Concentration'], marker='o', color='b')
plt.axvline(x=385, color='red', linestyle='--')
plt.axvline(x=780, color='red', linestyle='--')
plt.xlabel('Time (PDT)')
plt.ylabel('Methane Concentration [ppm]')
plt.title('Octopus Prototype Methane vs. Time (All-Day, 15mL Organic Carbon Treatment)')
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))
plt.grid(True)

# Plot the Extension and LICOR data
#plt.subplot(1, 3, 3)
#plt.plot(df3_filtered['PDT_Time'], df3_filtered['Methane_Concentration'], marker='o', linestyle='-', color='r', label='Extension')
#plt.plot(df2_everyother['PDT_Time'], df2_everyother['Methane_Concentration'], marker='o', linestyle='-', color='g', label='LICOR')

#plt.xlabel('Time (PDT)')
#plt.ylabel('Methane Concentration [ppb]')
#plt.title('OC45 LICOR and Extension: Methane vs. Time')
#plt.xticks(rotation=45)
#plt.grid(True)

# Display the average slopes
#plt.text(0.5, 0.85, f'LICOR Slope [ppb/s]: {avg_slope_LICOR:.4f}', 
         #horizontalalignment='center', verticalalignment='top',
         #fontsize=12, color='green', transform=plt.gca().transAxes)
#plt.text(0.5, 0.75, f'Extension Slope [ppb/s]: {avg_slope_extension:.4f}', 
        #horizontalalignment='center', verticalalignment='top',
        #fontsize=12, color='red', transform=plt.gca().transAxes)

# Plot the Short Period Octo Data and calc slope
def plot_slope_for_interval(df, time_interval, title):
    df_filtered = df[(df['PDT_Time'] >= time_interval[0]) & (df['PDT_Time'] <= time_interval[1])]
    
    if not df_filtered.empty:
        df_filtered['Methane_Concentration_ppb'] = df_filtered['Methane_Concentration'].apply(lambda x: x * 1000)
        slope = calculate_average_slope(df_filtered['Methane_Concentration_ppb'])
        
        plt.subplot(1, 2, 2)
        plt.plot(df_filtered['PDT_Time'], df_filtered['Methane_Concentration_ppb'], marker='o', color='b')
        plt.xlabel('Time (PDT)')
        plt.ylabel('Methane Concentration [ppb]')
        plt.title('Octopus Prototype Methane vs. Time (Red-Dashed Line Period, 15mL Organic Carbon Treatment)')
        plt.xticks(rotation=45)
        plt.grid(True)
        
        # Set fewer ticks on the x-axis
        plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=5))  # Control the number of ticks
        
        # Display the slope on the graph
        plt.text(0.5, 0.95, f'Avg Octo Slope [ppb/s]: {slope:.4f}', 
                 horizontalalignment='center', verticalalignment='top',
                 fontsize=12, color='black', transform=plt.gca().transAxes)

# Plot the Extension and LICOR data
plt.subplot(1, 3, 3)
#lt.plot(df3_filtered['PDT_Time'], df3_filtered['Methane_Concentration'], marker='o', linestyle='-', color='r', label='Extension')
#plt.plot(df2_everyother['PDT_Time'], df2_everyother['Methane_Concentration'], marker='o', linestyle='-', color='g', label='LICOR')

plt.xlabel('Time (PDT)')
plt.ylabel('Methane Concentration [ppb]')
plt.title('OC45 LICOR and Extension: Methane vs. Time')
plt.xticks(rotation=45)
plt.grid(True)

# Set fewer ticks on the x-axis for this plot
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=5))

# Display the average slopes
#plt.text(0.5, 0.85, f'LICOR Slope [ppb/s]: {avg_slope_LICOR:.4f}', 
         #horizontalalignment='center', verticalalignment='top',
         #fontsize=12, color='green', transform=plt.gca().transAxes)
#plt.text(0.5, 0.75, f'Extension Slope [ppb/s]: {avg_slope_extension:.4f}', 
         #horizontalalignment='center', verticalalignment='top',
         #fontsize=12, color='red', transform=plt.gca().transAxes)

plot_slope_for_interval(df1, ('10:45:00', '10:55:00'), 'Octo: Methane Concentration vs. Time')

plt.tight_layout()
plt.show()
