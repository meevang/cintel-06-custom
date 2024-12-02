# Imports
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # For Gauge Chart
from shinywidgets import render_plotly
from scipy import stats
import folium
from faicons import icon_svg

# Constants
UPDATE_INTERVAL_SECS: int = 3
DEQUE_SIZE: int = 3

# Initialize reactive value
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# Reactive calculation
@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    temp = round(random.uniform(-40, -20), 1)  # More realistic Antarctic temperatures
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}
    reactive_value_wrapper.get().append(new_dictionary_entry)
    deque_snapshot = reactive_value_wrapper.get()
    df = pd.DataFrame(deque_snapshot)
    return deque_snapshot, df, new_dictionary_entry

# UI Definition
ui.page_opts(title="PyShiny Express: Antarctic Explorer", fillable=True)

with ui.layout_columns(fill=True):
    with ui.value_box(showcase=icon_svg("clock"),theme="bg-gradient-blue-purple", fill=False):
        "Current Temperature"
        @render.text
        def display_temp():
            _, _, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} °C"

    # Adding Gauge Chart below the current temperature box
    with ui.card(full_screen= True):
        ui.card_header("Current Temperature Indicator")
        @render_plotly
        def display_gauge():
            _, _, latest_dictionary_entry = reactive_calc_combined()
            temp = latest_dictionary_entry["temp"]

            # Create a gauge chart to display the temperature
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=temp,
                title={'text': "Temperature (°C)", 'font': {'size': 24}},
                gauge={
                    'axis': {'range': [-40, 0]},  # Range for Antarctic temperatures
                    'bar': {'color': "blue"},
                    'steps': [
                        {'range': [-40, -30], 'color': "lightblue"},
                        {'range': [-30, -20], 'color': "lightcyan"},
                        {'range': [-20, 0], 'color': "cyan"}
                    ],
                }
            ))

            fig.update_layout(height=300)
            return fig

    with ui.value_box(showcase=icon_svg("calendar"),theme="bg-gradient-blue-purple", fill=False):
        "Current Date and Time"
        @render.text
        def display_time():
            _, _, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

with ui.card(fill=False):
    ui.card_header("Recent Temperature Readings")
    @render.data_frame
    def display_df():
        _, df, _ = reactive_calc_combined()
        pd.set_option('display.width', None)
        return render.DataGrid(df, width="100%")

with ui.layout_columns(fill=True):
    with ui.card(full_screen=True):
        ui.card_header("Temperature Trend")
        @render_plotly
        def display_plot():
            _, df, _ = reactive_calc_combined()
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                fig = px.scatter(df,
                    x="timestamp",
                    y="temp",
                    title="Temperature Readings with Trend Line",
                    labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                    color_discrete_sequence=["blue"])

                x_vals = range(len(df))
                y_vals = df["temp"]
                slope, intercept, _, _, _ = stats.linregress(x_vals, y_vals)
                df['trend_line'] = [slope * x + intercept for x in x_vals]
                fig.add_scatter(x=df["timestamp"], y=df['trend_line'], mode='lines', name='Trend Line')
                fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
                return fig
            return px.scatter()

    with ui.card(full_screen=True):
        ui.card_header("McMurdo Station Location")
        @render.ui
        def render_map():
            m = folium.Map(location=[-90, 0], zoom_start=3, 
                           min_zoom=1, max_zoom=11,
                           tiles='CartoDB positron')
            
            folium.Marker(
                [-77.85, 166.67],  # McMurdo Station coordinates
                popup="McMurdo Station",
                tooltip="Temperature Sensor Location"
            ).add_to(m)
            
            folium.Circle(
                [-77.85, 166.67],
                radius=50000,  # 50 km radius
                color="red",
                fill=True,
                fillColor="red"
            ).add_to(m)
            
            m.fit_bounds([[-90, -180], [-60, 180]])
            
            return ui.HTML(m._repr_html_())
