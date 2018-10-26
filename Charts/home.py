import calendar
import datetime as DT
from datetime import datetime, date
import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.plotting import show, figure, curdoc, output_file
from bokeh.models.tools import PanTool, SaveTool
from bokeh.io import output_file, show, curdoc
from bokeh.layouts import layout, widgetbox, column, row
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, LassoSelectTool
from bokeh.models import CustomJS, ColumnDataSource, Slider, DateRangeSlider, DatetimeTickFormatter
from bokeh.models.widgets import Slider, Select, TextInput, Div, DataTable, DateFormatter, TableColumn, Panel, Tabs, Toggle
from bokeh.io import output_file, show
from bokeh.models.widgets import RadioButtonGroup, Button
from bokeh.models.widgets.inputs import DatePicker

class mainplot:
    def __init__(self, df):
        self.data = df
    
    def prepare(self):
        #Creating Sessions data set
        self.daily_sessions = self.data.groupby('start_date').agg({'start_date':'count'}).rename(columns = {'start_date':'Sessions'})
        self.daily_sessions = self.daily_sessions.reset_index()
        self.daily_sessions['start_date'] = self.daily_sessions['start_date'].apply(lambda x:datetime.strptime(x, "%Y-%m-%d"))
        self.daily_sessions['Year'] = self.daily_sessions['start_date'].apply(lambda x:x.year)
        self.daily_sessions['Month'] = self.daily_sessions['start_date'].apply(lambda x:x.month)
        self.daily_sessions['Day'] = self.daily_sessions['start_date'].apply(lambda x:x.day)
        self.daily_sessions['Month_Abb'] = self.daily_sessions['Month'].apply(lambda x: calendar.month_abbr[x])
        self.daily_sessions['Month_Abb'] = str(self.daily_sessions['Month_Abb'])
        self.daily_sessions = self.daily_sessions.sort_values(by = ['Year', 'Month', 'Day'])
        
        #Creating Session Duration data set
        self.avg_time = self.data[['start_date', 'start_time', 'end_time']]
        self.avg_time['Delta'] = self.avg_time['end_time'] - self.avg_time['start_time']
        self.avg_time['Delta'] = self.avg_time['Delta'].apply(lambda x:x.seconds)
        self.avg_time['Day'] = self.avg_time['start_time'].apply(lambda x:x.day)
        self.avg_time['Year'] = self.avg_time['start_time'].apply(lambda x:x.year)
        self.avg_time['Month'] = self.avg_time['start_time'].apply(lambda x:x.month)
        self.avg_time = self.avg_time.groupby(['start_date', 'Day', 'Month', 'Year']).mean().rename(columns = {'Delta':'Avg_Time'})
        self.avg_time['Avg_Time'] = round(self.avg_time['Avg_Time'])
        self.avg_time = self.avg_time.reset_index()
        self.avg_time = self.avg_time.sort_values(by = ['Year', 'Month', 'Day'])
        
        #Creating Users data set
        self.users = self.data.groupby(['start_date', 'device_id']).count().reset_index()
        self.users = self.users.groupby(['start_date', 'device_id']).device_id.count()
        self.users = pd.DataFrame(self.users).rename(columns = {'device_id': 'Users'}).reset_index()
        self.users_final = self.users.groupby('start_date').sum().reset_index()
        
        #Creating Final Data set for CDS
        self.daily_sessions = self.daily_sessions[['start_date', 'Year', 'Month', 'Day', 'Sessions']]
        self.avg_time = self.avg_time[['Year', 'Month', 'Day', 'Avg_Time']]
        self.data_final = self.avg_time
        self.data_final['Sessions'] = self.daily_sessions['Sessions']
        self.data_final['Date'] = self.daily_sessions['start_date']
        self.data_final['Users'] = self.users_final['Users']
        self.data_final = self.data_final.rename(columns = {'Avg_Time':'Session Duration'})
        
        #Adding Widgets
        self.options = Select(title="", options=["Last 7 days", "Last 30 days", "Last 90 days", "Custom.."], value="Last 7 days")
        self.radio_button_group = RadioButtonGroup(labels=["Users", "Sessions", "Session Duration"], active=1)
        self.date_from = DatePicker(title="From", min_date=DT.date(2017,8,29), max_date=DT.date(2018,8,29),
                                    value=DT.date(2018,1,1)
                       )

        self.date_to = DatePicker(title="To", min_date=DT.date(2017,8,29), max_date=DT.date(2018,8,29),
                                    value=DT.date(2018,2,1)
                       )
        self.hover1 = HoverTool(
        tooltips=[('Date', '@x{%a %d %B}'),
                  ('Value', '@y')
        ],
        
        formatters={
        'x' : 'datetime'
        },
        
        mode = 'vline'
        )
        
        #Creating Plot
        self.source = ColumnDataSource(data=dict(x = [], y = [], Year=[], Month=[], Day=[], Date=[]))
        self.plot = figure(plot_width=708, plot_height=405, tools = 'wheel_zoom,box_zoom,reset,save')
                          #x_axis_type="datetime" logo = None,    
        self.plot.toolbar.logo = None
        self.plot.add_tools(self.hover1)
        self.plot.xgrid.visible = False
        self.plot.line(x = 'x', y = 'y', line_width = 3, source=self.source, color = "#2097BE")
        self.plot.circle(x = 'x', y = 'y', source = self.source, size=6, fill_color = "#2097BE", line_color = 'white')
        self.plot.xaxis.formatter=DatetimeTickFormatter(
            hours=["%d %B"],
            days=["%d %B"],
            months=["%d %B"],
    )
        return self.plot, self.radio_button_group
    
    def select_sessions(self):
        today = DT.date(2018,7,20)
        from_date = self.date_from.value
        to_date = self.date_to.value
        week_ago  = []
        month_ago = []
        ninty_ago = []
        custom = pd.date_range(from_date, to_date)
        custom = pd.Series(custom)
        custom = custom.apply(lambda x:x.date())
        if self.options.value == "Custom..":
            self.date_from.disabled = False
            self.date_to.disabled = False
        else:
            self.date_from.disabled = True
            self.date_to.disabled = True
        for i in range(0,7):
            week_ago.append(today - DT.timedelta(days=i))
        for i in range(0,31):
            month_ago.append(today - DT.timedelta(days=i))
        for i in range(0,91):
            ninty_ago.append(today - DT.timedelta(days=i))
        if self.options.value == "Last 7 days":
            self.selected = self.data_final[
                self.data_final['Date'].isin(week_ago)
            ]
        elif self.options.value == "Last 30 days":
            self.selected = self.data_final[
                self.data_final['Date'].isin(month_ago)
            ]
        elif self.options.value == "Last 90 days":
            self.selected = self.data_final[
                self.data_final['Date'].isin(ninty_ago)
            ]
        elif self.options.value == "Custom..":
            self.selected = self.data_final[
                self.data_final['Date'].isin(custom)
            ]
        return self.selected
    
    def update(self):
        df = self.select_sessions()
        x_name = 'Date'
        if self.radio_button_group.active == 0:
            self.y_name = 'Users'
            self.plot.yaxis.axis_label = self.y_name
        elif self.radio_button_group.active == 1:
            self.y_name = 'Sessions'
            self.plot.yaxis.axis_label = self.y_name
        else:
            self.y_name = 'Session Duration'
            self.plot.yaxis.axis_label = 'Session Duration (Sec)'
        self.plot.xaxis.axis_label = x_name
        
        self.source.data = dict(
            x=df[x_name],
            y=df[self.y_name],
            Year=df["Year"],
            Month = df["Month"],
            Day = df["Day"]
        )
        
    def final_sketch(self):
        controls = [self.options, self.date_from, self.date_to]
        for control in controls:
            control.on_change('value', lambda attr, old, new: self.update())
        self.radio_button_group.on_change('active', lambda attr, old, new: self.update())
        columns = [
            TableColumn(field="Date", title="Date", formatter = DateFormatter()),
            TableColumn(field="Sessions", title="Sessions"),
        ]
        self.data_table = DataTable(source=self.source, columns=columns, width=400, height=400)
        self.inputs = widgetbox([self.radio_button_group, *controls], sizing_mode='fixed')

        return self.inputs