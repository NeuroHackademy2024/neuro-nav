import pandas as pd
import numpy as np
import ipywidgets as widgets
from IPython.display import HTML, display
from bqplot import Figure, Scatter, Axis, LinearScale, OrdinalScale, Hist, Bars, Pie, Tooltip
from io import StringIO, BytesIO
import abc #for abstract classes / observer pattern
from abc import ABC
import bqplot.marks as bqm

class TractPlot:

    def __init__(self, df):
        self._df = df
        ##print(self._df.head())
     
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

    def _notify(self, data):
        '''
        Iterates through and calls update on all of the observers.
        '''
        for i, obj in enumerate(self._observers):
            obj.update(data)



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
    def update(self, data):
        '''
        This is an abstract method and will be overridden by update functions
        that are defined within each child of the abstract observer class.
        Therefore this method is not implemented here.

        Parameters
        -----------
        data : csv in bytes, use pd.read_csv(data)
        '''
        ...


class FileLoader(Subject):
    '''
    This class implements the file loader widget from ipywidgets
    and also defines some functions for monitoring the file loader.
    When the user uses the widget to upload a local CSV file,
    the data are loaded into the class's data attribute.

    Inherits from the Subject class, because it needs to be the one
    to signal and update all the other plot classes.
    '''
    
    def __init__(self):
        super().__init__()
        
        self.data = None
        self._uploader = self._create_uploader()

        _app_container = widgets.VBox([
            widgets.HTML(('<p>Viewing HCP demographics and behavioural data requires you to have registered on <i style="color:blue"><a href="www.humanconnectome.org">the HCP website</a></i>, accepted the data terms, and downloaded the Behavioural Data CSV file.</p>'
                         '<p>If you do have this file, specify its local path below:</p>')),
            self._uploader])
        self.container = widgets.VBox([_app_container])

    def _create_uploader(self): #creates the file uploader widget and observes when there are changes
        uploader = widgets.FileUpload(accept='*.csv')
        uploader.observe(self._on_change, names='value')
        return uploader

    def _on_change(self, _): #called when user uploads file using the widget
        #get the data:
        content = next(iter(self._uploader.value))['content']
        content_to_bytes = BytesIO(content)
        df = pd.read_csv(content_to_bytes)
        self.data = df
        self._notify(self.data) #send notification to observers


class App(Observer):
    '''
    Demo interactive plotter app.

    Inherits from the Observer class, because it needs to
    be notified when there are updates.
    '''
    
    def __init__(self, subject):
        super().__init__(subject) #run init from parent

        df = pd.read_csv('dummy_dataframe.csv') #initialize plot with dummy data
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

        self._year_slider, self._year_slider_box = self._create_year_slider(
            min(df['Year']), max(df['Year'])
        )

        _app_container = widgets.VBox([
            widgets.HBox([self._x_dropdown, self._y_dropdown]),
            self._figure,
            self._year_slider_box
        ], layout=widgets.Layout(align_items='center', flex='3 0 auto'))
        self.container = widgets.VBox([
            widgets.HBox([
                _app_container,
            ])
        ], layout=widgets.Layout(flex='1 1 auto', margin='0 auto 0 auto', max_width='1024px'))
        self._update_app()

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

    def update(self, data):
        '''
        Overriding abstract method.
        Defines new data source and triggers widget update.

        Parameters
        -----------
        data : csv in bytes, use pd.read_csv(data)
        '''
        df = pd.read_csv(data)
        self._df = df
        self._new_data_reset()
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

    def _new_data_reset(self):
        '''
        Reset the app after receiving new data.
        Gets called by the observer update function when new data
        are loaded via the File Loader.
        '''
        df = self._df #set new dta

        #set new dropdown options
        available_indicators = self._df['Indicator Name'].unique()
        self._x_dropdown.options = available_indicators
        self._x_dropdown.value = available_indicators[0]
        
        self._y_dropdown.options = available_indicators
        self._y_dropdown.value = available_indicators[1]

        #reset the range on the year slider
        self._year_slider.min = min(df['Year'])
        self._year_slider.max = max(df['Year'])


class DemPlot(Observer):
    def __init__(self, subject):
        super().__init__(subject)
        
        # Create an Output widget for capturing print output
        #self.output_widget = widgets.Output()
        #display(self.output_widget)

        df = pd.DataFrame({
            'Age': [np.nan],
            'Gender': [np.nan]
        })
        self._df = df
     
        age = self._df['Age'] #T1_Count
        gender = self._df['Gender']

        age_counts = age.value_counts()
        gender_counts = gender.value_counts()

        age_options = ['All ages'] + sorted(age.unique())
        self._x_dropdown = self._create_dropdown(age_options, 0)

        x_scale = OrdinalScale()
        y_scale = LinearScale()

        self._x_axis = Axis(scale=x_scale, label="Age")
        self._y_axis = Axis(scale=y_scale, orientation="vertical", label="N")

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

    def _create_dropdown(self, options, initial_index):
        dropdown = widgets.Dropdown(options=options, value=options[initial_index])
        dropdown.observe(self._on_change, names=['value'])
        return dropdown

    def _on_change(self, _):
        self._update_app()

    def update(self, data):
        '''
        Overriding abstract method.
        Defines new data source and triggers widget update.

        Parameters
        -----------
        data : csv in bytes, use pd.read_csv(data)
        '''
        #print(data)
        #df = pd.read_csv(data)
        #self._df = df
        self._df = data
        #print(self._df)


        age = self._df['Age'] #T1_Count
        gender = self._df['Gender']
        #print(age)

        age_counts = age.value_counts()
        # Sort age_counts by index to ensure alphanumerical order
        age_counts = age.value_counts().sort_index()
        gender_counts = gender.value_counts()

        age_options = ['All ages'] + sorted(age.unique())

        x_scale = OrdinalScale()
        y_scale = LinearScale()

        self._x_axis = Axis(scale=x_scale, label="Age")
        self._y_axis = Axis(scale=y_scale, orientation="vertical", label="N")

        self._x_dropdown.options = age_options

        self._age_bars.x = age_counts.index
        self._age_bars.y = age_counts.values
        self._age_bars.scales = {'x': x_scale, 'y': y_scale}

        self._age_figure.axes = [self._x_axis, self._y_axis]

        self._gender_pie.labels = gender_counts.index.tolist()
        self._gender_pie.sizes = gender_counts.values


     #   self._new_data_reset()
        self._update_app()

    def _update_app(self):
        age_selected = self._x_dropdown.value

        default_color = 'steelblue'
        highlight_color = 'red'
        colors = [highlight_color if val == age_selected else default_color for val in self._age_bars.x]
        self._age_bars.colors = colors

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
    

class BehavPlot(Observer):

    def __init__(self, subject):
        super().__init__(subject)
        
        # df = pd.read_csv('hcp_dummy.csv') #initialize plot with dummy data
        df = pd.DataFrame({'PicSeq_AgeAdj':[np.nan],
                           'CardSort_AgeAdj':[np.nan],
                           'Flanker_AgeAdj':[np.nan],
                           'ListSort_AgeAdj':[np.nan],
                           'ReadEng_AgeAdj':[np.nan],
                           'PicVocab_AgeAdj':[np.nan],
                           'ProcSpeed_AgeAdj':[np.nan], 
                           'FS_TotCort_GM_Vol':[np.nan],
                           'FS_SubCort_GM_Vol':[np.nan],
                           'FS_Total_GM_Vol':[np.nan],
                           'FS_L_WM_Vol':[np.nan],
                           'FS_R_WM_Vol':[np.nan],	
                           'FS_Tot_WM_Vol':[np.nan]})
        self._df = df
        
        
        # print(len(self._df))
        # print(self._df.index)
     
        self._measures = self._df.columns
        
        #print(self._measures)

        age_options = [0]#['All Ages'] + list(df['Age'].unique())
        sex_options = [0]#['All'] + list(df['Gender'].unique())
        
        
        self._x_dropdown = self._create_dropdown(self._measures, 0)
        self._y_dropdown = self._create_dropdown(self._measures, 1)
        self._age_dropdown = self._create_toggle(age_options, 0)
        self._sex_dropdown = self._create_toggle(sex_options, 0)
        self._checkbox = self._create_checkbox('show regression line', False)

        x_scale = LinearScale()
        y_scale = LinearScale()

        self._x_axis = Axis(scale=x_scale, label="X")
        self._y_axis = Axis(scale=y_scale, orientation="vertical", label="Y", label_offset = '3.9em')

        self._scatter = Scatter(
            x=[], y=[], scales={"x": x_scale, "y": y_scale}
        )

        self._line = bqm.Lines(scales={'x': x_scale, 'y': y_scale}, colors = ['black'])

        self._figure = Figure(marks=[self._scatter, self._line], axes=[self._x_axis, self._y_axis], layout=dict(width="95%"),animation_duration=500)

        # self._year_slider, year_slider_box = self._create_year_slider(
        #     min(df['Year']), max(df['Year'])
        # )
        _app_container = widgets.VBox([
            self._age_dropdown, self._sex_dropdown,
            widgets.HBox([self._x_dropdown, self._y_dropdown]),
            self._checkbox,
            self._figure,
            # year_slider_box
        ], layout=widgets.Layout(align_items='center', flex='3 0 auto'))
        self.container = widgets.VBox([
            widgets.HBox([
                _app_container,
            ])
        ], layout=widgets.Layout(flex='1 1 auto', margin='0 auto 0 auto', max_width='1024px'))
        
        self._update_app()

    # @classmethod
    # def from_csv(cls, path):
    #     df = pd.read_csv(path)
    #     return cls(df)

    def _create_dropdown(self, options, initial_index):
        dropdown = widgets.Dropdown(options=options, value=options[initial_index])
        dropdown.observe(self._on_change, names=['value'])
        return dropdown

    def _create_toggle(self, options, initial_index):
        toggle = widgets.ToggleButtons(options=options, value=options[initial_index])
        toggle.observe(self._on_change, names=['value'])
        return toggle


    def _create_checkbox(self, desc, initial_value):
        checkbox = widgets.Checkbox(value=initial_value, description=desc, disabled=False, indent=False)
        checkbox.observe(self._on_change, names=['value'])
        return checkbox

    def _on_change(self, _):
        self._update_app()
    
    def update(self, data):
        '''
        Overriding abstract method.
        Defines new data source and triggers widget update.

        Parameters
        -----------
        data : csv in bytes, use pd.read_csv(data)
        '''
        #df = pd.read_csv(data)
        #self._df = df
        self._df = data
        #print(self._df)
        self._new_data_reset()
        
        self._update_app()
    
    def _update_app(self):
        
        x_measure = self._x_dropdown.value
        y_measure = self._y_dropdown.value
        #print(self._df.head())
        #print(self._x_dropdown.options)
        #print(self._y_dropdown.options)
        # year_range = self._year_slider.value

        showreg = self._checkbox.value

        with self._scatter.hold_sync():          
            with self._line.hold_sync():
            
            
                x = self._df[x_measure]
                #print(x_measure)
                #print(y_measure)
                y = self._df[y_measure]

                #print(x.head())
                #print(y.head())

                        
                x_scale = LinearScale()
                y_scale = LinearScale()
        
                self._x_axis = Axis(scale=x_scale, label="X")
                self._y_axis = Axis(scale=y_scale, orientation="vertical", label="Y", label_offset = '3.9em')
        
                self._scatter.scales = {"x": x_scale, "y": y_scale}
                
                        
                self._x_axis.label = x_measure
                self._y_axis.label = y_measure
                
                self._scatter.default_opacities = [0.5]
    
                self._scatter.x = x
                self._scatter.y = y

                #print(self._scatter)
            

                if showreg:
                    self._line.x = [np.min(x), np.max(x)]
                    poly = np.polyfit(self._scatter.x, self._scatter.y, 1)
                    self._line.y = np.polyval(poly, self._line.x)
    
                if showreg == False:
                    self._line.x = []
                    self._line.y = []
                self._line.scales= {"x": x_scale, "y": y_scale}
                self._figure.axes =[self._x_axis, self._y_axis]
                self._figure.animation_duration=500

    def _new_data_reset(self):
        '''
        Reset the app after receiving new data.
        Gets called by the observer update function when new data
        are loaded via the File Loader.
        '''
        df = self._df #set new dta
        
        self._df = df[['Subject','Age','Gender','PicSeq_AgeAdj','CardSort_AgeAdj','Flanker_AgeAdj','ListSort_AgeAdj','ReadEng_AgeAdj','PicVocab_AgeAdj','ProcSpeed_AgeAdj', 'FS_TotCort_GM_Vol','FS_SubCort_GM_Vol','FS_Total_GM_Vol','FS_L_WM_Vol','FS_R_WM_Vol',	'FS_Tot_WM_Vol']].dropna(how='any')

        #set new dropdown options
        # available_indicators = self._df['Indicator Name'].unique()
        # self._x_dropdown.options = available_indicators
        # self._x_dropdown.value = available_indicators[0]
        
        self._measures = self._df.columns[3:]
        age_options = ['All Ages'] + list(self._df['Age'].unique())
        sex_options = ['All'] + list(self._df['Gender'].unique())
        
        self._x_dropdown.options = self._measures
        self._x_dropdown.value = self._measures[0]
        self._y_dropdown.options  = self._measures
        # print(self._y_dropdown.options)
        self._y_dropdown.value = self._measures[1]
        
        self._age_dropdown.options =  age_options
        self._sex_dropdown.options = sex_options
        