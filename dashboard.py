import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.plotting import show, figure, curdoc, output_file
from bokeh.models.tools import PanTool, SaveTool
from bokeh.io import output_file, show
from bokeh.plotting import figure
from datetime import datetime, date
from bokeh.layouts import layout, widgetbox, column, row
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, LassoSelectTool
from bokeh.models import CustomJS, ColumnDataSource, Slider, DateRangeSlider
from bokeh.models.widgets import Slider, Select, TextInput, Div, DataTable, DateFormatter, TableColumn, Panel, Tabs
from bokeh.io import curdoc, output_file, show
import calendar

hv.extension('bokeh', logo=False)
renderer = hv.renderer('bokeh')

#output_file('ContextGrid_App.html')

def disable_logo(plot, element):
    plot.state.toolbar.logo = None
hv.plotting.bokeh.ElementPlot.finalize_hooks.append(disable_logo)

from main import fetch
query = ("""SELECT * FROM cg_sessions.session_event ORDER BY id""") 
bigquery = fetch.import_data(query)
data = bigquery.data_output()

from Charts import heatmap

hm = heatmap.heatmap(data).plot_heatmap()
hm_plot = renderer.get_plot(hm).state
print("Heatmap Live")

from Charts import barchart

bar = barchart.bars(data).plot_barchart()
bar_plot = renderer.get_plot(bar).state
print("Barchart Live")

from Charts import home

main_page = home.mainplot(data)
sketch = main_page.prepare()
inputs = main_page.final_sketch()
plot_layout = layout([[sketch[0], inputs]], sizing_mode='fixed')
main_page.update()
print("Home Layout Live")

tab1 = Panel(child = plot_layout, title = "Home")
tab2 = Panel(child = hm_plot, title = "Heatmap")
tab3 = Panel(child = bar_plot, title="Bar Chart")
tabs = Tabs(tabs=[tab1, tab2, tab3])
curdoc().add_root(tabs)
