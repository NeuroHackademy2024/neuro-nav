import pandas as pd
import numpy as np
import ipywidgets as widgets
from IPython.display import HTML
from bqplot import Figure, Scatter, Axis, LinearScale

class TractPlot:

    def __init__(self, df):
        self._df = df
        print(self._df.head())
     
        available_tracts = self._df['tractID'].unique()

        self._measures = {'Fractional Anisotropy':'dki_fa','Mean Diffusivity':'dki_md','Mean Kurtosis':'dki_mk','Axonal Water Fraction':'dki_awf'}
        self._tract_dropdown = self._create_dropdown(available_tracts, 0)
        self._y_dropdown = self._create_dropdown(list(self._measures.keys()), 0)

        x_scale = LinearScale()
        y_scale = LinearScale()

        self._x_axis = Axis(scale=x_scale, label="X")
        self._y_axis = Axis(scale=y_scale, orientation="vertical", label="Y")

        self._scatter = Scatter(
            x=[], y=[], scales={"x": x_scale, "y": y_scale}
        )

        self._figure = Figure(marks=[self._scatter], axes=[self._x_axis, self._y_axis], layout=dict(width="99%"), animation_duration=1000)


        _app_container = widgets.VBox([
            widgets.HBox([self._tract_dropdown, self._y_dropdown]),
            self._figure,
            # year_slider_box
        ], layout=widgets.Layout(align_items='center', flex='3 0 auto'))
        self.container = widgets.VBox([
            widgets.HBox([
                _app_container,
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

    def _on_change(self, _):
        self._update_app()

    def _update_app(self):
        tract = self._tract_dropdown.value
        y_indicator = self._y_dropdown.value

        with self._scatter.hold_sync():          
            
            df = self._df.loc[self._df['tractID'] == tract]
            
            x = df['nodeID']
            y = df[self._measures[y_indicator]]

            self._x_axis.label = 'node'
            self._y_axis.label = y_indicator
            
            self._scatter.default_opacities = [0.5]

            self._scatter.x = x
            self._scatter.y = y