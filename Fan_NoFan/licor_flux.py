# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 12:26:44 2024

@author: Admin
"""

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import pytz
from matplotlib.ticker import MaxNLocator
import numpy as np

# Define start and end times for the time interval
start_t = '17:40:00'
end_t = '17:52:00'

# Load datasets
# df1 = pd.read_excel('HighConcentrationTest_MI.xlsx')
df2 = pd.read_excel('10_29_LICOR.xlsx', skiprows=7)

# Define timezone
pdt_zone = pytz.timezone('America/Los_Angeles')

# Function to convert Unix epoch time to PDT
def epoch_to_pdt_time(epoch_time):
    date_obj = datetime.utcfromtimestamp(epoch_time)
    return date_obj.astimezone(pdt_zone).strftime("%H:%M:%S")

# Convert the time columns
# df1['PDT_Time'] = pd.to_datetime(df1.iloc[:, 6], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.strftime('%H:%M:%S')
df2['PDT_Time'] = pd.to_datetime(df2.iloc[:, 1], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.strftime('%H:%M:%S')
print(df2['PDT_Time'].head())
print(df2['PDT_Time'].tail())

# Convert Methane concentration columns to numeric
# df1['Methane_Concentration'] = 1000 * pd.to_numeric(df1.iloc[:, 4], errors='coerce')
df2['Methane_Concentration'] = pd.to_numeric(df2.iloc[:, 10], errors='coerce')

# Filter datasets for the desired intervals using start_t and end_t
# df1_filtered = df1[(df1['PDT_Time'] >= start_t) & (df1['PDT_Time'] <= end_t)]
df2_filtered = df2[(df2['PDT_Time'] >= start_t) & (df2['PDT_Time'] <= end_t)]

# sample LICOR data (every row)
df2_everyother = df2_filtered.iloc[::1, :]

# Check for empty DataFrame after filtering
if df2_everyother.empty:
    print("Warning: No data in the filtered time range.")
else:
    # Calculate average slope in ppb/s using np.polyfit on downsampled data
    def calculate_average_slope(data):
        time_ordinal = np.arange(len(data))
        slope, _ = np.polyfit(time_ordinal, data.values, 1)
        return slope

    avg_slope_LICOR = calculate_average_slope(df2_everyother['Methane_Concentration'])

    # Set figure size and plot data
    plt.figure(figsize=(18, 6))
    # Plot the LICOR data
    plt.plot(df2_everyother['PDT_Time'], df2_everyother['Methane_Concentration'], marker='o', linestyle='-', color='g', label='LICOR')

    plt.xlabel('Time (PDT)')
    plt.ylabel('Methane Concentration [ppb]')
    plt.title('High Concentration Test: LICOR CH4 vs. Time')
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))
    plt.grid(True)

    # Display the average slope
    plt.text(0.5, 0.85, f'LICOR Slope [ppb/s]: {avg_slope_LICOR:.4f}', 
             horizontalalignment='center', verticalalignment='top',
             fontsize=12, color='green', transform=plt.gca().transAxes)

    # Calculate time difference between first and last timestamps in seconds
    start_time = datetime.strptime(df2_everyother['PDT_Time'].iloc[0], "%H:%M:%S")
    end_time = datetime.strptime(df2_everyother['PDT_Time'].iloc[-1], "%H:%M:%S")
    time_difference_seconds = (end_time - start_time).total_seconds()
    #print(time_difference_seconds)

    # Get the first and last methane concentration values in ppb
    first_methane_value = df2_everyother['Methane_Concentration'].iloc[0] / 1e9  # convert ppb to ppb ratio
    last_methane_value = df2_everyother['Methane_Concentration'].iloc[-1] / 1e9

    # Print the first and last values
    #print(f"First Methane Concentration [ppb]: {first_methane_value}")
    #print(f"Last Methane Concentration [ppb]: {last_methane_value}")

    # Constants for flux calculation
    chamberV = 54.417  # liters 
    chamberA = 0.0178  # m^2
    chamberAha =  chamberA * 1e-4  # ha
    chamberT = 25      # Celsius
    chamberP = 1       # atm
    gasconst = 0.08206 # (L*atm)/(mol*K)
    methaneMolMass = 16.04 # g/mol

    # Calculate molar volume based on conditions
    molVol = gasconst * (chamberT + 273) / chamberP

    # Calculate initial and final methane mass in the chamber
    initmethvol = first_methane_value * chamberV
    initmethmol = initmethvol / molVol
    initmethmass = initmethmol * methaneMolMass

    finalmethvol = last_methane_value * chamberV
    finalmethmol = finalmethvol / molVol
    finalmethmass = finalmethmol * methaneMolMass

    # Calculate flux
    ppbpersec = (last_methane_value-first_methane_value)*1e9/time_difference_seconds
    dmdt = (finalmethmass - initmethmass) / time_difference_seconds  # g/s
    flux = dmdt / chamberA  # g/m^2/s
    fluxrate_g_per_ha_per_day = flux * 86400 * 1e4  # Convert to g/ha/day
    print(f"ppb/s : {ppbpersec}")

    # Print results
    #print(f"Flux [g/m^2/s]: {flux}")
    print(f"Flux [g/ha/day]: {fluxrate_g_per_ha_per_day}")

    # Calculate flux using polyfit-based slope in ppb/s
    volmeth = avg_slope_LICOR * chamberV / 1e9  # Convert ppb/s to volumetric change in ppb ratio
    molmeth = volmeth / molVol
    massmeth = molmeth * methaneMolMass  # g/s
    massmethperday = 86400 * massmeth
    polyflux = massmethperday / chamberAha

    print(f"PolyFlux [g/ha/day]: {polyflux}")

plt.legend()
plt.show()
