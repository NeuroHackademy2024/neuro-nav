import pandas as pd
import numpy as np
import ipywidgets as widgets
from IPython.display import HTML
from bqplot import Figure, Scatter, Axis, LinearScale
import io
import abc #for abstract classes / observer pattern
from abc import ABC

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

        # self._year_slider, year_slider_box = self._create_year_slider(
        #     min(df['Year']), max(df['Year'])
        # )
        _app_container = widgets.VBox([
            widgets.HBox([self._tract_dropdown, self._y_dropdown]),
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
        tract = self._tract_dropdown.value
        # x_indicator = self._x_dropdown.value
        y_indicator = self._y_dropdown.value
        # year_range = self._year_slider.value

        with self._scatter.hold_sync():          
            
            df = self._df.loc[self._df['tractID'] == tract]
            
            x = df['nodeID']
            y = df[self._measures[y_indicator]]

            self._x_axis.label = 'node'
            self._y_axis.label = y_indicator
            
            self._scatter.default_opacities = [0.5]

            self._scatter.x = x
            self._scatter.y = y



class Subject:
    '''
    Watches and updates all registered observer objects.
    '''
    observers = []

    def __init__(self):
        self._observers = []

    def _register_observer(self, observer):
        '''
        Add an observer to the observer list if it's not already there.
        '''
        if observer not in self._observers:
            self._observers.append(observer)

    def _unregister_observer(self, observer):
        '''
        Remove an observer from the observer list if it's in the list.
        '''
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self):
        '''
        Iterates through and calls update on all of the observers.
        '''
        for i, obj in enumerate(self._observers):
            obj._update()



class Observer(ABC):
    '''
    Abstract class.
    '''
    
    def __init__(self, subject):
        '''
        Register an observer with the subject.
        '''
        self._subject = subject
        subject._register_observer(self)

    @abc.abstractmethod
    def update(self):
        '''
        This is an abstract method and will be overridden by update functions
        that are defined within each child of the abstract observer class.
        Therefore this method is not implemented here.
        '''
        ...


class FileLoader:
    '''
    This class implements the file loader widget from ipywidgets
    and also defines some functions for monitoring the file loader.
    When the user uses the widget to upload a local CSV file,
    the data are loaded into the class's data attribute.
    '''
    
    def __init__(self):
        self.data = None
        self._uploader = self._create_uploader()

        _app_container = widgets.VBox([
            widgets.HTML(('<p>Viewing HCP demographics and behavioural data requires you to have registered on <i style="color:blue"><a href="www.humanconnectome.org">the HCP website</a></i>, accepted the data terms, and downloaded the Behavioural Data CSV file.</p>'
                         '<p>If you do have this file, specify its local path below:</p>')),
            self._uploader])
        self.container = widgets.VBox([_app_container])

    def _create_uploader(self): #creates the file uploader widget and observes when there are changes
        uploader = widgets.FileUpload(accept='.csv', multiple=False)
        uploader.observe(self._on_change, names='value')
        return uploader

    def _on_change(self, _): #called when user uploads file using the widget
        #get the data:
        content = self._uploader.value[0].content
        content_to_bytes = io.BytesIO(content)
        #dataframe = pd.read_csv(content_to_bytes)
        self.data = content_to_bytes


class App:
    '''
    Demo interactive plotter app.
    '''
    
    def __init__(self, df):
        self._df = df
        available_indicators = self._df['Indicator Name'].unique()
        self._x_dropdown = self._create_indicator_dropdown(available_indicators, 0)
        self._y_dropdown = self._create_indicator_dropdown(available_indicators, 1)

        x_scale = LinearScale()
        y_scale = LinearScale()

        self._x_axis = Axis(scale=x_scale, label="X")
        self._y_axis = Axis(scale=y_scale, orientation="vertical", label="Y")

        self._scatter = Scatter(
            x=[], y=[], scales={"x": x_scale, "y": y_scale}
        )

        self._figure = Figure(marks=[self._scatter], axes=[self._x_axis, self._y_axis], layout=dict(width="99%"), animation_duration=1000)

        self._year_slider, year_slider_box = self._create_year_slider(
            min(df['Year']), max(df['Year'])
        )
        _app_container = widgets.VBox([
            widgets.HBox([self._x_dropdown, self._y_dropdown]),
            self._figure,
            year_slider_box
        ], layout=widgets.Layout(align_items='center', flex='3 0 auto'))
        self.container = widgets.VBox([
            # widgets.HTML(
            #     (
            #         '<h1>Explore the Human Connectome Project Young Adult dataset!</h1>'
            #         '<h2 class="app-subtitle"><a href="https://github.com/NeuroHackademy2024/neuro-nav">Link to code</a></h2>'
            #     ),
            #     layout=widgets.Layout(margin='0 0 5em 0')
            # ),
            widgets.HBox([
                _app_container,
                # widgets.HTML(EXPLANATION, layout=widgets.Layout(margin='0 0 0 2em'))
            ])
        ], layout=widgets.Layout(flex='1 1 auto', margin='0 auto 0 auto', max_width='1024px'))
        self._update_app()

    @classmethod
    def from_csv(cls, path):
        df = pd.read_csv(path)
        return cls(df)

    def _create_indicator_dropdown(self, indicators, initial_index):
        dropdown = widgets.Dropdown(options=indicators, value=indicators[initial_index])
        dropdown.observe(self._on_change, names=['value'])
        return dropdown

    def _create_year_slider(self, min_year, max_year):
        year_slider_label = widgets.Label('Year range: ')
        year_slider = widgets.IntRangeSlider(
            min=min_year, max=max_year,
            layout=widgets.Layout(width='500px'),
            continuous_update=False
        )
        year_slider.observe(self._on_change, names=['value'])
        year_slider_box = widgets.HBox([year_slider_label, year_slider])
        return year_slider, year_slider_box

    def _on_change(self, _):
        self._update_app()

    def _update_app(self):
        x_indicator = self._x_dropdown.value
        y_indicator = self._y_dropdown.value
        year_range = self._year_slider.value

        with self._scatter.hold_sync():
            df = self._df[self._df['Year'].between(*year_range)].dropna()
            x = df[df['Indicator Name'] == x_indicator]['Value']
            y = df[df['Indicator Name'] == y_indicator]['Value']

            self._x_axis.label = x_indicator
            self._y_axis.label = y_indicator

            self._scatter.default_opacities = [0.2]

            self._scatter.x = x
            self._scatter.y = y