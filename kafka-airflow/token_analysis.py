import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import pandas as pd
import os
import logging 

# Set up logging to capture messages to a file
logging.basicConfig(filename='token_analysis.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Connect to SQLite database
conn = sqlite3.connect('kafka_data.db')
cursor = conn.cursor()

# Fetch all tokens from the database and order by timestamp
cursor.execute("SELECT * FROM token_data ORDER BY timestamp DESC") 
tokens = cursor.fetchall()

# Close the connection after fetching data
conn.close()

# Calculate the total number of tokens
token_count = len(tokens)

# Get the latest timestamp (max timestamp)
max_timestamp = max([token[1] for token in tokens])

# Get the current time when the data is being logged (for time_measured)
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Prepare data to be written to CSV
new_data = pd.DataFrame({
    'token_count': [token_count],
    'time_measured': [current_time]
})

# Check if the CSV file exists
csv_file = 'token_count.csv'
if os.path.exists(csv_file):
    # If the file exists, append the new data
    new_data.to_csv(csv_file, mode='a', header=False, index=False)
else:
    # If the file does not exist, create it and write the header
    new_data.to_csv(csv_file, mode='w', header=True, index=False)

# Read the data from the CSV for plotting
df = pd.read_csv(csv_file)

logging.info('New row added: {new_data}')

# Convert the 'time_measured' column to datetime
df['time_measured'] = pd.to_datetime(df['time_measured'])

# If there are more than 1 row, calculate the token difference
if len(df) == 1:
    # If there's only one row, set the token_sent to token_count (original value)
    df['token_sent'] = df['token_count']
else:
    # If there are multiple rows, set the first token_sent to token_count
    # For subsequent rows, calculate the difference between consecutive token counts
    df['token_sent'] = df['token_count'].diff()
    df['token_sent'].iloc[0] = df['token_count'].iloc[0] 

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the cumulative_token_count against time_measured
ax.plot(df['time_measured'], df['token_sent'], marker='o', color='b', label='Token Count')

# Set the title and labels
ax.set_title('Token Sent Over Time')
ax.set_xlabel('Timestamp')
ax.set_ylabel('Token Count')

# Format the x-axis to show time more clearly
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
#ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))  # Set the interval to 1 minute

# Rotate the x-axis labels
plt.xticks(rotation=45)

# Display the plot
plt.tight_layout()
plt.legend()
plt.show(block=False)  # Non-blocking
plt.pause(5)  # Pause for 5 seconds to display the plot
plt.close()  # Close the plot after 5 seconds
