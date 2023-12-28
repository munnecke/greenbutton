from flask import Flask, request, send_from_directory, render_template, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend
import plotly.figure_factory as ff
import seaborn as sns

app = Flask(__name__, static_folder='static')
# Convert the strings to 2D lists of integers for ev tou 5
#12 24 char strings representing the rate codes for the hour of the month per NREL DB
weekday="666666555555555544444555666666555555555544444555666666555566665544444555666666555566665544444555666666555555555544444555333333222222222211111222333333222222222211111222333333222222222211111222333333222222222211111222333333222222222211111222666666555555555544444555666666555555555544444555"
weekend="666666666666665544444555666666666666665544444555666666666666665544444555666666666666665544444555666666666666665544444555333333333333332211111222333333333333332211111222333333333333332211111222333333333333332211111222333333333333332211111222666666666666665544444555666666666666665544444555"
weekday_rates = [list(map(int, weekday[i:i+24])) for i in range(0, len(weekday), 24)]
weekend_rates = [list(map(int, weekend[i:i+24])) for i in range(0, len(weekend), 24)]
TOU_rates = [0, 0.81629, 0.48129, 0.15351, 0.51149, 0.44775, 0.1452] #per EV-TOU-5 rates

def get_rate(timestamp):
    # Check if the timestamp is on a weekday or weekend
    if timestamp.weekday() < 5:
        rates = weekday_rates
    else:
        rates = weekend_rates

    # Calculate the month and hour from the timestamp
    month = timestamp.month - 1  # Months are 1-based in datetime, but 0-based in our list
    hour = timestamp.hour

    # Return the rate
    return TOU_rates[rates[month][hour]]

@app.route('/', methods=['GET'])
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/test', methods=['GET'])
def test_route():
    return 'Test route is working!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'greenbutton-data' not in request.files:
        return 'No file part'
    file = request.files['greenbutton-data']
    if file.filename == '':
        return 'No selected file'
    if file:
        df = pd.read_csv(file)
        # Now you can use the DataFrame `df` to analyze the data
        # Combine Date and Start Time and convert to datetime
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Start Time'])
        # Apply TOU_rate function to each row
        df['TOU_rate'] = df['Datetime'].apply(get_rate) # put the current TOU rate in the TOU_rate column            df['$Consumption'] = df['Consumption'] * df['TOU_rate'] # calculate value of Consumption in dollars
        df['$Generation'] = df['Generation'] * df['TOU_rate'] # value of Generation in dollars
        df['$Consumption'] = df['Consumption'] * df['TOU_rate'] #value of Consumption in dollars
        df['$Net'] = df['Net'] * df['TOU_rate'] # value of Net in dollars
        df.set_index('Datetime', inplace=True)
        df.to_csv('docs/processed_data.csv')
    return 'File successfully uploaded and read into DataFrame'

@app.route('/show', methods=['GET'])
def show_summary():
    # Load the data
    df = pd.read_csv('docs/processed_data.csv', parse_dates=['Datetime'])
    df.set_index('Datetime', inplace=True)

    # Resample to monthly frequency and calculate summary statistics
    monthly_data = df.resample('M').sum()
    annual_total = df.sum()

    # Prepare the data
    monthly_summary = monthly_data[['Consumption', 'Generation', 'Net', '$Net','$Consumption', '$Generation']].rename(columns={'$Net': 'NetDollar', '$Consumption': 'ConsumptionDollar', '$Generation': 'GenerationDollar'}).to_dict('records')
    annual_total = annual_total[['Consumption', 'Generation', 'Net', '$Net','$Consumption', '$Generation']].rename(index={'$Net': 'NetDollar', '$Consumption': 'ConsumptionDollar', '$Generation': 'GenerationDollar'}).to_dict()
    months = [date.strftime('%b %y') for date in monthly_data.index]

    return render_template('summary.html', monthly_summary=monthly_summary, annual_total=annual_total, months=months)


#@app.route('/', methods=['GET'])
#def home():
#    return send_from_directory(app.static_folder, 'heatmap.png')

@app.route('/generate', methods=['GET'])
def generate_heatmap():
    # Load the data
    df = pd.read_csv('docs/processed_data.csv', parse_dates=['Datetime'])
    df.set_index('Datetime', inplace=True)

    # Resample to hourly frequency and calculate average statistics
    hourly_data = df['$Net'].resample('H').sum()

    # Group by month and hour to calculate average
    heatmap_data = hourly_data.groupby([hourly_data.index.month, hourly_data.index.hour]).mean()

    # Unstack the data to create a matrix and transpose it
    heatmap_data = heatmap_data.unstack(level=0).T

    # Generate the heatmap
    plt.figure(figsize=(12, 6))

    # Create a list of month names for y-axis labels
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Create a list of hour labels in 'hh am/pm' format for x-axis labels
    hour_labels = [f"{hour % 12 if hour % 12 != 0 else 12} {'am' if hour < 12 else 'pm'}" for hour in range(24)]

    sns.heatmap(heatmap_data, cmap='RdYlGn_r', linewidths=0.5, yticklabels=month_names, xticklabels=hour_labels, cbar=False)

    plt.ylabel('Month')
    plt.xlabel('Hour')

    # Create a custom title with different colors for 'GENERATION' and 'CONSUMPTION'
    plt.title('Energy ', loc='left', color='black', fontsize=12)
    plt.title('GENERATION', color='red', fontsize=12)
    plt.title(' and ', loc='center', color='black', fontsize=12)
    plt.title('CONSUMPTION', color='green', fontsize=12)
    plt.title(' by Month and Hour of the Munnecke Home', loc='right', color='black', fontsize=12)

    plt.savefig('static/heatmap.png')
 
    return send_from_directory('static', 'heatmap.png')

@app.route('/hexmap')
def generate_hexmap():
    # Load the data
    df = pd.read_csv('docs/processed_data.csv', parse_dates=['Datetime'])
    df.set_index('Datetime', inplace=True)

    # Resample to hourly frequency and calculate average statistics
    hourly_data = df['$Net'].resample('H').sum()

    # Group by month and hour to calculate average
    heatmap_data = hourly_data.groupby([hourly_data.index.month, hourly_data.index.hour]).mean()

    # Unstack the data to create a matrix and transpose it
    heatmap_data = heatmap_data.unstack(level=0).T

    # Convert the DataFrame to a list of dictionaries
    heatmap_data = heatmap_data.reset_index().to_dict('records')

    # Return the data as a JSON object
    print(heatmap_data)

    return jsonify(heatmap_data)

if __name__ == "__main__":
    app.run(debug=True)