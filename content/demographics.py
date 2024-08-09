import pandas as pd
import numpy as np
import ipywidgets as widgets
from IPython.display import HTML, display
from bqplot import Figure, Scatter, Axis, LinearScale, OrdinalScale, Hist, Bars, Pie, Tooltip
import bqplot.pyplot as plt

class DemPlot:

    def __init__(self, df):
        # Create an Output widget for capturing print output
        self.output_widget = widgets.Output()
        display(self.output_widget)
        
        self._df = df
        print(self._df.head())
     
        age = self._df['Age'] #T1_Count
        gender = self._df['Gender']

        age_counts = age.value_counts()
        gender_counts = gender.value_counts()
        print(age_counts)
        print(age_counts.index)

  #      self._y_measures = {'Fractional Anisotropy':'dki_fa','Mean Diffusivity':'dki_md','Mean Kurtosis':'dki_mk','Axonal Water Fraction':'dki_awf'}
        age_options = ['All ages'] + sorted(age.unique())
        self._x_dropdown = self._create_dropdown(age_options, 0)
   #     self._y_dropdown = self._create_dropdown(list(self._y_measures.keys()), 0)

        x_scale = OrdinalScale()
        y_scale = LinearScale()
        #pie_scale = LinearScale(min=-0.5, max=0.5)

        self._x_axis = Axis(scale=x_scale, label="Age")
        self._y_axis = Axis(scale=y_scale, orientation="vertical", label="N")

        #self._scatter = Scatter(
  #          x=[], y=[], scales={"x": x_scale, "y": y_scale}
   #     )

        print(age.head())
        age.describe()
        self._hist = Hist(sample=age, bins=3, scales={'sample': x_scale, 'count': y_scale})
        print(age_counts)
        print(age_counts.index)
        print(age_counts.values)
        self._age_bars = Bars(x=age_counts.index, y=age_counts.values,
                          scales={'x': x_scale, 'y': y_scale})
        tooltip = Tooltip(fields=['x', 'y'], labels=['Age', 'N'])
        self._age_bars.tooltip = tooltip
        #self._gender_bars = Bars(x=gender_counts.index, y=gender_counts.values,
        #                  scales={'x': x_scale, 'y': y_scale})
        self._gender_pie = Pie(labels=gender_counts.index.tolist(), sizes=gender_counts.values,
                     display_labels='inside')
        tooltip = Tooltip(fields=['label', 'size'], labels=['Gender', 'N'])
        self._gender_pie.tooltip = tooltip


#       self._figure = Figure(marks=[self._scatter], axes=[self._x_axis, self._y_axis], layout=dict(width="99%"), animation_duration=1000)
        self._age_figure = Figure(marks=[self._age_bars], axes=[self._x_axis, self._y_axis],
                             layout=dict(width="99%"), title='Age brackets')
        self._gender_figure = Figure(marks=[self._gender_pie],
                                    layout=dict(width="300px"), title='Gender')

        # Define a function to update the radius dynamically
        def update_pie_radius(change=None):
            # Get the current width and height of the figure
            width = int(self._gender_figure.layout.width.replace('px', ''))
            height = int(self._gender_figure.layout.height.replace('px', '')) if self._gender_figure.layout.height else width
            
            # Calculate the new radius as a percentage of the smaller dimension
            new_radius = 0.4 * min(width, height) / 2
            
            # Update the pie chart's radius
            self._gender_pie.radius = new_radius
        
        # Initialize the pie chart with the correct radius
        update_pie_radius()
        
        # Observe changes to the figure's layout and update the radius
        self._gender_figure.layout.observe(update_pie_radius, names=['width', 'height'])
        

        # self._year_slider, year_slider_box = self._create_year_slider(
        #     min(df['Year']), max(df['Year'])
        # )
        _app_container = widgets.VBox([
            widgets.HBox([self._x_dropdown]),
            self._age_figure,
            self._gender_figure,
            # year_slider_box
        ], layout=widgets.Layout(align_items='center', flex='3 0 auto'))
        self.container = widgets.VBox([
            # widgets.HTML(
            #     (
            #         '<h1>Development indicators. A Voici dashboard, running entirely in your browser!</h1>'
            #         '<h2 class="app-subtitle"><a href="https://github.com/pbugnion/voila-gallery/blob/master/country-indicators/index.ipynb">Link to code</a></h2>'
            #     ),
            #     layout=widgets.Layout(margin='0 0 5em 0')
            # ),
            widgets.HBox([
                _app_container,
                #widgets.HTML(EXPLANATION, layout=widgets.Layout(margin='0 0 0 2em'))
            ])
        ], layout=widgets.Layout(flex='1 1 auto', margin='0 auto 0 auto', max_width='1024px'))
        self._update_app()

    @classmethod
    def from_csv(cls, path):
        df = pd.read_csv(path)
        return cls(df)

    def _create_dropdown(self, options, initial_index):
        dropdown = widgets.Dropdown(options=options, value=options[initial_index])
        dropdown.observe(self._on_change, names=['value'])
        return dropdown

    # def _create_year_slider(self, min_year, max_year):
    #     year_slider_label = widgets.Label('Year range: ')
    #     year_slider = widgets.IntRangeSlider(
    #         min=min_year, max=max_year,
    #         layout=widgets.Layout(width='500px'),
    #         continuous_update=False
    #     )
    #     year_slider.observe(self._on_change, names=['value'])
    #     year_slider_box = widgets.HBox([year_slider_label, year_slider])
    #     return year_slider, year_slider_box

    def _on_change(self, _):
        self._update_app()

    def _update_app(self):
        age_selected = self._x_dropdown.value

        default_color = 'steelblue'
        highlight_color = 'red'
        colors = [highlight_color if val == age_selected else default_color for val in self._age_bars.x]
        print(colors)
        self._age_bars.colors = colors

        #TROUBLESHOOTING:
        # Create an Output widget
        output_widget = widgets.Output()
        
        # Example usage: Capture print output
        with output_widget:
            print("This will be displayed in the browser!")
            # Any other print statements or operations you want to capture
            print("Another message to capture.")
            print(age_selected)
        
        # Display the output widget in the notebook
        display(output_widget)


        with self._hist.hold_sync():
            pass
#        tract = self._x_dropdown.value
 #       # x_indicator = self._x_dropdown.value
  #      y_indicator = self._y_dropdown.value
   #     # year_range = self._year_slider.value
#
 #       with self._scatter.hold_sync():          
  #          
   #         df = self._df.loc[self._df['tractID'] == tract]
    #        
     #       x = df['nodeID']
      #      y = df[self._y_measures[y_indicator]]
#
 ##           self._x_axis.label = 'node'
   #         self._y_axis.label = y_indicator
    #        
     #       self._scatter.default_opacities = [0.5]
#
 #           self._scatter.x = x
  #          self._scatter.y = y