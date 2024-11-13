import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import pytz
from matplotlib.ticker import MaxNLocator
import numpy as np

# Read the Excel file, skipping the first 7 rows
df2 = pd.read_excel('Nov12_CNCTest.xlsx', skiprows=7)

# Timezone for PDT conversion
pdt_zone = pytz.timezone('America/Los_Angeles')

# Function to convert Unix epoch time to PDT
def epoch_to_pdt_time(epoch_time):
    date_obj = datetime.utcfromtimestamp(epoch_time)
    return date_obj.astimezone(pdt_zone).strftime("%H:%M:%S")

# Convert Unix time (epoch) to PDT
df2['PDT_Time'] = pd.to_datetime(df2.iloc[:, 1], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles').dt.strftime('%H:%M:%S')

# Convert the Methane concentration data to numeric and convert to ppb
df2['CO2_Concentration'] = pd.to_numeric(df2.iloc[:, 9], errors='coerce')
print(df2['CO2_Concentration'].head())

# Filter the datasets for the desired time interval (PDT)
df2_filtered = df2[(df2['PDT_Time'] >= '12:28:00') & (df2['PDT_Time'] <= '12:38:00')]

# Function to calculate average slope (in ppb/s)
def calculate_average_slope(data):
    time_ordinal = np.arange(len(data))
    slope, intercept = np.polyfit(time_ordinal, data.values, 1)
    return slope / 2, intercept  # Since data is recorded every 2 seconds

# Function to calculate percent loss per minute
def calculate_percent_loss(data):
    first_value = data.iloc[0]
    last_value = data.iloc[-1]
    percent_loss = ((first_value - last_value) / first_value) * 100
    return percent_loss

# Calculate the slope and intercept for LICOR data (in ppb/s)
avg_slope_LICOR, intercept_LICOR = calculate_average_slope(df2_filtered['CO2_Concentration'])

# Calculate percent loss per minute for LICOR data
percent_loss_LICOR = calculate_percent_loss(df2_filtered['CO2_Concentration'])

# Generate the linear fit line
time_ordinal = np.arange(len(df2_filtered))
linear_fit_line = avg_slope_LICOR * time_ordinal * 2 + intercept_LICOR  # Multiply time by 2 because it's in 2-second intervals

# Set figure size for the plot
plt.figure(figsize=(18, 6))

# Plot LICOR data
plt.plot(df2_filtered['PDT_Time'], df2_filtered['CO2_Concentration'], marker='o', linestyle='-', color='g', label='LICOR')

# Plot the linear fit line
plt.plot(df2_filtered['PDT_Time'], linear_fit_line, linestyle='--', color='b', label='Linear Fit')

plt.xlabel('Time (PDT)')
plt.ylabel('CO2 Concentration [ppm]')
plt.title('CNC Proto Leak Test (Fan OFF, As-Is, 30D,Test 3)')
plt.xticks(rotation=45)
plt.grid(True)

# Limit the number of x-axis ticks
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=5))

# Display the average slope and percent loss per minute on the plot
plt.text(0.5, 0.85, f'Percent Loss After 10 Minutes: {percent_loss_LICOR:.4f}%',
         horizontalalignment='center', verticalalignment='top',
         fontsize=12, color='green', transform=plt.gca().transAxes)

# Add legend for the plot
plt.legend()

plt.tight_layout()
plt.show()
