# -*- coding: utf-8 -*-
from bokeh.core.properties import field
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import (ColumnDataSource, HoverTool, SingleIntervalTicker,
                          Slider, Button, Label, CategoricalColorMapper)
from bokeh.palettes import Inferno256
from bokeh.plotting import figure

import numpy as np
import pandas as pd
import pickle
import random


# Read the data
df = pd.read_csv('covid-19/data/countries-aggregated.csv')

# Restrict to countries with at least 100 confirmed cases
df = df[df.Confirmed > 100]


def set_radius(df):
    """Calculate bubble radius from number of deaths"""
    radius = df.Deaths
    radius_size = np.sqrt(radius / np.pi) / 0.4
    min_size = 3
    radius_size = radius_size.where(radius_size >= min_size).fillna(min_size)
    df["Radius"] = radius_size
    return df

# Add bubble radius to the data frame
df = set_radius(df)

# Compute recovered by confirmed ratio (replace NaNs by 0.0)
df["RecoveredRatio"] = df.Recovered / df.Confirmed
df["RecoveredRatio"] = df.RecoveredRatio.fillna(0.0)

# Determine unique countries and dates
countries = list(df.Country.unique())
dates = sorted(list(df.Date.unique()))

# Collect data points as dictionaries with date key
data = {}
for date in dates:
    df_date = df[df.Date == date]
    df_date.drop(('Date'), axis=1, inplace=True)
    parts = date.split("-")
    # We store dates as int for easier processing
    date = int("".join(parts))
    data[date] = df_date.to_dict('series')

# Define basic plot outline (axes, ranges and title)
plot = figure(x_range=(0, 650000), y_range=(0, 1), title='COVID-19 Development', plot_height=250)
plot.xaxis.ticker = SingleIntervalTicker(interval=40000)
plot.xaxis.axis_label = "Number of positively tested patients"
plot.yaxis.ticker = SingleIntervalTicker(interval=0.05)
plot.yaxis.axis_label = "Percentage of recovered patients"

# Disable scientific notation for the x-axis (confirmed cases)
plot.below[0].formatter.use_scientific = False

# Add a large date label on the top left
label = Label(x=2000, y=0.85, text=str(dates[0]), text_font_size='70pt', text_color='#eeeeee')
plot.add_layout(label)

# Define and shuffle the color palette for better visuals
# Note that this will work fine as long as we have less than 256 nations
# on the planet (let's hope the nationalists fade again).
palette = list(Inferno256)
random.seed(42)
random.shuffle(palette)
color_mapper = CategoricalColorMapper(palette=palette[:len(countries)], factors=countries)

# Set the data source for the plot
dates = list(data.keys())
source = ColumnDataSource(data=data[dates[0]])

# The main component: adding colored circles or correct radius where they belong.
plot.circle(
    x='Confirmed',
    y='RecoveredRatio',
    size='Radius',
    source=source,
    fill_color={'field': 'Country', 'transform': color_mapper},
    fill_alpha=0.8,
    line_color='#7c7e71',
    line_width=0.5,
    line_alpha=0.5,
    legend_field='Country',
)

# Adding a little Hover tool for our circles
plot.add_tools(HoverTool(tooltips=[
    ("Country", "@Country"),
    ("Number of of confirmed cases", "@Confirmed"),
    ("Percentage of recovered cases", "@RecoveredRatio"),
    ("Deaths", "@Deaths"),
], show_arrow=False, point_policy='follow_mouse'))


num_dates = len(dates)
date_range = range(num_dates)

def animate_update():
    """Flip through dates by index."""
    date = slider.value + 1
    if date > date_range[-1]:
        date = date_range[-1]
    slider.value = date


def slider_update(attrname, old, new):
    """Update slider source data according to current date."""
    date_idx = slider.value
    date = dates[date_idx]

    # Transform the int date to a human-readable string again
    str_date = str(date)
    label_date = str_date[:4] + "-" + str_date[4:6] + "-" + str_date[6:]
    label.text = label_date
    source.data = data[date]

# Add a date slider
slider = Slider(start=date_range[0], end=date_range[-1], value=date_range[0], step=1, show_value=False)
slider.on_change('value', slider_update)

callback_id = None
def animate():
    """Animate on button click"""
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update, 800)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)
button = Button(label='► Play', width=60)
button.on_click(animate)

# Define the layout for the plot...
layout = layout([
    [plot],
    [slider, button],
], sizing_mode='scale_width')

# ... and add it to this document's root.
curdoc().add_root(layout)
curdoc().title = "COVID-19 Development"
