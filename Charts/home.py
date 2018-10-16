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
from bokeh.models.widgets import Slider, Select, TextInput, Div, DataTable, DateFormatter, TableColumn, Panel, Tabs, CheckboxButtonGroup
from bokeh.io import curdoc, output_file, show
import calendar
from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import RadioButtonGroup


class mainplot:
    def __init__(self, df):
        self.data = df
    
    def prepare(self):
        #Creating Daily session data set
        self.daily_sessions = self.data.groupby('start_date').agg({'start_date':'count'}).rename(columns = {'start_date':'Sessions'})
        self.daily_sessions = self.daily_sessions.reset_index()
        self.daily_sessions['start_date'] = self.daily_sessions['start_date'].apply(lambda x:datetime.strptime(x, "%Y-%m-%d"))
        self.daily_sessions['Year'] = self.daily_sessions['start_date'].apply(lambda x:x.year)
        self.daily_sessions['Month'] = self.daily_sessions['start_date'].apply(lambda x:x.month)
        self.daily_sessions['Day'] = self.daily_sessions['start_date'].apply(lambda x:x.day)
        #self.daily_sessions['Month_Abb'] = self.daily_sessions['Month'].apply(lambda x: calendar.month_abbr[x])
        #self.daily_sessions['Month_Abb'] = str(self.daily_sessions['Month_Abb'])
        #self.daily_sessions['Type'] = 'Sessions'
        self.daily_sessions = self.daily_sessions.sort_values(by = ['Year', 'Month', 'Day'])
        #print(self.daily_sessions)
        
        #Creating Average Time data set
        self.avg_time = self.data[['start_time', 'end_time']]
        self.avg_time['Delta'] = self.avg_time['end_time'] - self.avg_time['start_time']
        self.avg_time['Delta'] = self.avg_time['Delta'].apply(lambda x:x.seconds)
        self.avg_time['Day'] = self.avg_time['start_time'].apply(lambda x:x.day)
        self.avg_time['Year'] = self.avg_time['start_time'].apply(lambda x:x.year)
        self.avg_time['Month'] = self.avg_time['start_time'].apply(lambda x:x.month)
        self.avg_time = self.avg_time.groupby(['Day', 'Month', 'Year']).mean().rename(columns = {'Delta':'Avg_Time'})
        self.avg_time['Avg_Time'] = round(self.avg_time['Avg_Time'])
        self.avg_time = self.avg_time.reset_index()
        #self.avg_time['Type'] = 'Avg_Time'
        self.avg_time = self.avg_time.sort_values(by = ['Year', 'Month', 'Day'])
        #print(self.avg_time)
        
        self.daily_sessions = self.daily_sessions[['Year', 'Month', 'Day', 'Sessions']]
        self.avg_time = self.avg_time[['Year', 'Month', 'Day', 'Avg_Time']]
        self.data_final = self.avg_time
        self.data_final['Sessions'] = self.daily_sessions['Sessions']
        self.data_final = self.data_final.rename(columns = {'Avg_Time':'Average Time'})
        #print(self.data_final.info())

        self.year_select = Select(title="Year", options=["2017", "2018"], value="2018")
        self.month_slider = Slider(title="Month", start = 1, end = 12, value = 1)
        self.yaxis = Select(title = 'Y-axis', options=['Sessions', 'Average Time'], value = 'Sessions')
        
        self.source = ColumnDataSource(data=dict(x = [], y = [], Year=[], Month=[]))
        #self.source = ColumnDataSource(data=dict(Year=[], Month=[], Day=[], Sessions=[]))
        #self.source2 = ColumnDataSource(data=dict(Year=[], Month=[], Day=[], Avg_Time=[]))
        
        self.hover1 = HoverTool(
        tooltips=[('Day', '@x'), ('Sessions', '@y')]
        )
        
        self.hover2 = HoverTool(
        tooltips=[('Day', '@x'), ('Average Time', '@y')]
        )

        self.plot = figure(plot_width=1100, plot_height=400, logo = None, tools = 'pan,wheel_zoom,box_zoom,reset,save')
        #self.plot.vbar('Day', top = 'Sessions', source = self.source, width = 0.7, color = '#FBA40A', name = 'don')
        self.plot.line(x = 'x', y = 'y', line_width = 4, source=self.source, color = "#2097BE")
        self.plot.circle(x = 'x', y = 'y', source = self.source, size=12, fill_color = "#2097BE", line_color = 'white')
        return self.plot, self.year_select, self.month_slider, self.source, self.data_final, self.hover1, self.hover2
    
    def select_sessions(self):
        y = int(self.year_select.value)
        m = self.month_slider.value
        self.selected = self.data_final[
            (self.data_final['Year'] == y) &
            (self.data_final['Month'] == m)
        ]
        #print(self.selected)
        return self.selected
    
    def update(self):
        df = self.select_sessions()
        x_name = 'Day'
        self.yvar = self.yaxis.value
        self.plot.xaxis.axis_label = x_name
        self.plot.yaxis.axis_label = self.yvar
        self.source.data = dict(
            x=df[x_name],
            y=df[self.yvar],
            Year=df["Year"],
            Month = df["Month"]
        )
        if self.yvar == 'Sessions':
            self.plot.add_tools(self.hover1)
        else:
            self.plot.add_tools(self.hover2)


    
    def final_sketch(self):
        #fig = home_plot()
        controls = [self.yaxis, self.year_select, self.month_slider]
        for control in controls:
            control.on_change('value', lambda attr, old, new: self.update())
        columns = [
            TableColumn(field="Date", title="Date", formatter = DateFormatter()),
            TableColumn(field="Sessions", title="Sessions"),
        ]
        self.data_table = DataTable(source=self.source, columns=columns, width=400, height=400)
        self.inputs = widgetbox(*controls, sizing_mode='fixed')

        return self.inputs