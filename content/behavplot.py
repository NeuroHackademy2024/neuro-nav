import pandas as pd
import numpy as np
import ipywidgets as widgets
from IPython.display import HTML
from bqplot import Figure, Scatter, Axis, LinearScale

class BehavPlot:

    def __init__(self, df):
        self._df = df[['Subject','PicSeq_AgeAdj','CardSort_AgeAdj','Flanker_AgeAdj','ListSort_AgeAdj','ReadEng_AgeAdj','PicVocab_AgeAdj',		'ProcSpeed_AgeAdj', 'FS_TotCort_GM_Vol','FS_SubCort_GM_Vol','FS_Total_GM_Vol','FS_L_WM_Vol','FS_R_WM_Vol',	'FS_Tot_WM_Vol']].dropna(how='any')
        
        
        print(len(self._df))
        print(self._df.index)
     
        self._measures = self._df.columns[1:]
        print(self._measures)
        
        
        self._x_dropdown = self._create_dropdown(self._measures, 0)
        self._y_dropdown = self._create_dropdown(self._measures, 1)

        x_scale = LinearScale()
        y_scale = LinearScale()

        self._x_axis = Axis(scale=x_scale, label="X")
        self._y_axis = Axis(scale=y_scale, orientation="vertical", label="Y")

        self._scatter = Scatter(
            x=[], y=[], scales={"x": x_scale, "y": y_scale}
        )

        self._figure = Figure(marks=[self._scatter], axes=[self._x_axis, self._y_axis], layout=dict(width="99%"), animation_duration=1000)

        # self._year_slider, year_slider_box = self._create_year_slider(
        #     min(df['Year']), max(df['Year'])
        # )
        _app_container = widgets.VBox([
            widgets.HBox([self._x_dropdown, self._y_dropdown]),
            self._figure,
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
        
        x_measure = self._x_dropdown.value
        y_measure = self._y_dropdown.value
        # year_range = self._year_slider.value

        with self._scatter.hold_sync():          
            
            
            
            x = self._df[x_measure]
            y = self._df[y_measure]

            self._x_axis.label = x_measure
            self._y_axis.label = y_measure
            
            self._scatter.default_opacities = [0.5]

            self._scatter.x = x
            self._scatter.y = y