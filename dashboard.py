import calendar
import warnings
import numpy as np
import pandas as pd
import holoviews as hv
from bokeh.plotting import show, figure, curdoc, output_file
from bokeh.models.tools import PanTool, SaveTool
from bokeh.io import output_file, show, curdoc
from datetime import datetime, date
from bokeh.layouts import layout, widgetbox, column, row, gridplot
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, LassoSelectTool
from bokeh.models import CustomJS, ColumnDataSource, Slider, DateRangeSlider
from bokeh.models.widgets import Slider, Select, TextInput, Div, DataTable, DateFormatter, TableColumn, Panel, Tabs, Button

hv.extension('bokeh', logo=False)
renderer = hv.renderer('bokeh')
warnings.filterwarnings("ignore")
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
print("Heatmap Live")
'''
from Charts import barchart

bar = barchart.bars(data).plot_barchart()
print("Barchart Live")
'''
from Charts import home

main_page = home.mainplot(data)
sketch = main_page.prepare()
inputs = main_page.final_sketch()
div1 = Div(text = """<html>
   <head>
      <style type="text/css">
         body {
            padding: 0in; 
         }
         .square {
         position: relative;
            background-color: #2097BE;
            width: 1500px;
            height: 80px;
            border: 0px;
         }
         .square p{
          font-size:30pt;
          margin: 0;
          background: #2097BE;
          position: relative;
          top: 20%;
          left: -26%;
          text-align: center;
          margin:auto;
          padding:0;
          height:5%;
          font-family:Comfortaa;
          color:white;
      width:55%;
      transform: translate(50%, 50%)   
         }
      </style>
   </head>
   <body>
      <div class="square">
      <p>ContextGrid Analytics Dashboard</p></div>
   </body>
</html>""")
#plot_layout = layout([[inputs, sketch[0]]], sizing_mode='fixed')
plot_layout = column(div1, inputs, row(sketch[0], sketch[1]), row(hm, sketch[2]))
main_page.update()
print("Home Layout Live")
'''
from Charts import piechart
pie = piechart.pie(data).plot_pie()
print("Pie chart live")
'''




#tab1 = Panel(child = plot_layout, title = "Home")
#tab2 = Panel(child = hm, title = "Heatmap")
#tab3 = Panel(child = bar, title="Bar Chart")
#tabs = Tabs(tabs=[tab1, tab2, tab3])
curdoc().add_root(plot_layout)
curdoc().title = "ContextGrid Dashboard"
