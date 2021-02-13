import pandas as pd
import datetime
import time
import pdb

from data_extract import *

# create dataframe format
columns_list = ["Outside Temperature", "High Out Temperature", "Low Out Temperature", "Rainfall", "High Rain Rate", "Barometer", "Solar Radiation", "Number of Wind Samples", "Inside Temperature", "Inside Humidity", "Outside Humidity",
                "Average Wind Speed", "High Wind Speed", "Direction of Hi Wind Speed", "Prevailing Wind Direction", "Average UV", "ET", "Invalid data", "Soil Moistures", "Soil Temperatures", "Leaf Wetnesses", "Extra Temperatures", "Extra Humidity", "Reed Closed", "Reed Opened"]

date_columns = ["Datetime", "Date Stamp"]
temp_columns = ["Outside Temperature", "High Out Temperature", "Low Out Temperature", "Inside Temperature", "Soil Temperatures", "Extra Temperatures"]

# df = pd.read_csv("webdl.csv", parse_dates=date_columns)
df = get_df().copy()

# plot graph with bokeh

# import
from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import RangeTool, ColumnDataSource, Range1d
from bokeh.models.widgets import Slider, RadioButtonGroup, Select, DateRangeSlider, DatePicker
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter

# widgets variable
start_date = df.loc[0,"Date Stamp"]
end_date = df.loc[df.index[-1], "Date Stamp"]

plot_source = ColumnDataSource(data=dict(x=[], y=[]))
select_source = ColumnDataSource(data=dict(x=[], y=[]))

# Set up plot
plot = figure(plot_height=400, plot_width=800,
            tools="ypan,reset,save,ywheel_zoom",
            x_axis_type="datetime", x_axis_location="above",
            x_range=(df.loc[int(df.index[-1]*0.4),"Datetime"], df.loc[int(df.index[-1]*0.6),"Datetime"]),
            background_fill_color="#efefef")

plot.xaxis.formatter = DatetimeTickFormatter(
    hours=["%R"],
    days=["%d %B %R"]
)

plot.line(x="x", y="y", source=plot_source)
plot_source.data = dict(
    x = df["Datetime"].tolist(),
    y = df["Outside Temperature"].tolist()
)

# Set up range select subplot
select = figure(title="Drag the middle and edges of the selection box to change the range above",
                plot_height=130, plot_width=800, y_range=plot.y_range,
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef")

range_tool = RangeTool(x_range=plot.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select_source.data = dict(
    x = df["Datetime"].tolist(),
    y = df["Outside Temperature"].tolist()
)

select.line(x="x", y="y", source=select_source)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool

select.xaxis.formatter = DatetimeTickFormatter(
    hours=["%R"],
    days=["%d %B %R"]
)

# Set up callbacks
def update():
    # update plots
    # pdb.set_trace()
    start = datetime.date.fromordinal(start_date_pick.value.toordinal()) 
    end = datetime.date.fromordinal(end_date_pick.value.toordinal())

    mask = (df["Datetime"] >= start) & (df["Datetime"] <= end)
    _df = df[mask]

    # pdb.set_trace()
    plot_source.data = dict(
        x=_df["Datetime"].tolist(),
        y=_df[yaxis_select.value].tolist()
    )

    select_source.data = dict(
        x=_df["Datetime"].tolist(),
        y=_df[yaxis_select.value].tolist()
    )

    # update range tool range
    # plot.x_range = Range1d(start, end)
    # select.x_range = plot.x_range

def temp_unit_update(attrname, old, new):
    # print("[INFO] update temperature units")
    global df
    if new == 1:
        # deg C is selected
        for c in temp_columns:
            df[c] = (df[c]-32)*5/9
            update()
    elif new == 0:
        # deg F is selected
        for c in temp_columns:
            df[c] = df[c]*9/5+32
            update()

def yaxis_select_update(attrname, old, new):
    update()

def date_range_update(attrname, old, new):
    update()

# Set up widgets
yaxis_select = Select(
    value="Outside Temperature", title='Y-axis Data', options=columns_list)

start_date_pick = DatePicker(title="Start date", min_date=start_date, max_date=end_date, value=start_date)
end_date_pick = DatePicker(title="End date", min_date=start_date, max_date=end_date, value=end_date)
temp_unit_button = RadioButtonGroup(labels=["°F", "°C"], active=0)

# hook up events
temp_unit_button.on_change('active', temp_unit_update)
yaxis_select.on_change('value', yaxis_select_update)
start_date_pick.on_change('value', date_range_update)
end_date_pick.on_change('value', date_range_update)


inputs = column(yaxis_select, temp_unit_button, start_date_pick, end_date_pick)
plots = column(plot, select)
curdoc().add_root(row(inputs, plots, width=1200))
curdoc().title = "Observatory Data Plot"
