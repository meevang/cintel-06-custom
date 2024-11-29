import pandas as pd
import requests
from io import StringIO
import shiny

# Correct URL of the CSV file (raw content)
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv"  # Raw URL

# Define custom headers if necessary
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# Fetch the CSV data
try:
    # Send a GET request to the URL with custom headers
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error if the request failed
    
    # Read the CSV content directly from the response text
    df = pd.read_csv(StringIO(response.text))
    print("CSV file loaded successfully.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching the URL: {e}")
except Exception as e:
    print(f"Error: {e}")

# Define the UI for the app with a layout
app_ui = shiny.ui.page_fluid(
    # Title for the page
    shiny.ui.h2("Data Grid Example with Layout"),
    
    # Layout: Sidebar and Main content area
    shiny.ui.page_sidebar(
        shiny.ui.sidebar_panel(
            shiny.ui.h3("Sidebar"),  # Sidebar content
            shiny.ui.p("This is a sidebar with additional information.")
        ),
        shiny.ui.main_panel(
            shiny.ui.h3("Main Content"),
            shiny.ui.output_table("data_table")  # Placeholder for displaying the data table
        )
    )
)

# Define the server logic
def server(input, output, session):
    # Render the dataframe as a table in the UI
    @output
    @shiny.render_table
    def data_table():
        return df  # Return the pandas dataframe to be rendered as a table

# Create the Shiny app
app = shiny.App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()

