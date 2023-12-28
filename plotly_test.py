import pandas as pd
import plotly.figure_factory as ff

def show_summary():
    # Load the data
    df = pd.read_csv('docs/processed_data.csv', parse_dates=['Datetime'])
    df.set_index('Datetime', inplace=True)

    # Resample to hourly frequency and calculate average statistics
    hourly_data = df['$Net'].resample('H').sum()

    # Group by month and hour to calculate average
    heatmap_data = hourly_data.groupby([hourly_data.index.month, hourly_data.index.hour]).mean()

    # Unstack the data to create a matrix and transpose it
    heatmap_data = heatmap_data.unstack(level=0).T

    # Create a list of month names for y-axis labels
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Create a list of hour labels in 'hh am/pm' format for x-axis labels
    hour_labels = [f"{hour % 12 if hour % 12 != 0 else 12} {'am' if hour < 12 else 'pm'}" for hour in range(24)]

    # Create the heatmap
    fig = ff.create_annotated_heatmap(z=heatmap_data.values, x=hour_labels, y=month_names, colorscale='RdYlGn', showscale=False)

    # Add title
    fig.update_layout(title_text='Energy consumption and generation of the Munnecke home by month and hour')

    # Show the plot
    fig.show()