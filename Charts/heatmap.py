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

#hv.extension('bokeh', logo=False)
#renderer = hv.renderer('bokeh')

class heatmap:
    def __init__(self, df):
        self.data = df
    def plot_heatmap(self):
        ##Stacked Bar chart for Day and Event Type
        self.day_hour = self.data.groupby(by = ['start_day', 'start_hour']).agg({'start_day': 'count'}).rename(columns = {'start_day':'Sessions'})
        self.day_hour = self.day_hour.reset_index()
        key_dimensions_hm = [('start_day', 'Day'), ('start_hour', 'Hour')]
        value_dimensions_hm = [('Sessions')]
        macro_hm = hv.Table(self.day_hour, key_dimensions_hm, value_dimensions_hm)
        self.hm = macro_hm.to.heatmap(['Day', 'Hour'], 'Sessions', []).options(width=1100, show_legend=False, height = 600, 
                                                                               color=hv.Cycle('Category20b'), tools = ['hover'])
        return self.hm