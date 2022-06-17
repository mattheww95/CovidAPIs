"""
First attempt at visualizeing the CovSpectrum in a dashboard using bokeh

2022-06-17: Matthew Wells
"""


from CovSpectrum_api import GatherAPIData
from bokeh.plotting import figure, show, save, output_file
from bokeh.models import Legend
from bokeh.palettes import Category20c_20 as pallette
import pandas as pd
from typing import NamedTuple
import random


class data_point(NamedTuple):
    pl: str
    count: int
    proportion: float

class JsontoFigure:
    """
    Convert the json response from the api to make the data and create some plots
    """
    mut_data = {}
    plot_data = {}
    def __init__(self, api_obj: GatherAPIData) -> None:
        self.api_obj  = api_obj
        self.cov_spectrum_to_axes()
    
    def create_figures(self):
        """
        render each individual bokeh plot

        """
        
        for key in self.mut_data.keys():
            #self.rearrange_time_data(self.mut_data[key])
           
            for plit in self.plot_data.keys():
                data_plot = {
                    "dates": [i for i in self.plot_data[plit].columns],
                }
                for idx in self.plot_data[plit].index:
                    data_plot[idx] = [i for i in self.plot_data[plit].loc[idx, :]]
                lineages = [i for i in self.plot_data[plit].index]
                p = figure(x_range=data_plot["dates"], title=f"Lineage changes over time ({key})", 
                tools="hover", tooltips="$name @$name %", width=1000, height=1000)
                p.add_layout(Legend(), 'right')
                p.vbar_stack([i for i in self.plot_data[plit].index], x="dates", source=data_plot, width=0.9, 
                color=[pallette[i] for i in range(len(lineages))], 
                legend_label=[i for i in self.plot_data[plit].index]) # get random colurs for each lineage
                p.xaxis.major_label_orientation = "vertical"
                output_file(filename=f"outputs/{key}.html", title=key)
                save(p)
    
    def create_random_colors(self, N):
        """
        Quickly come up with a fake colour scheme:
        copied form answer here: https://stackoverflow.com/questions/13998901/generating-a-random-hex-color-in-python
        """
        chars = '0123456789ABCDEF'
        return ['#'+''.join(random.sample(chars,6)) for i in range(N)]
        

    def rearrange_time_data(self, time_data: dict):
        """
        Convert the time data into the format bokeh requires

        need to hold the data keys as x-axis points
        legend keys in lineages (also the category)
        y-axis is the proportion as well
        """

        # data structure to fill
        data_out = {
            'dates': [i for i in time_data.keys()],
            # need to fill each lineage in here, with their data ordered to each x value
            # each category goes in here aftewards as well
            'other': []
        }
        lineages_tracked = {'other'}
        cut_off = 0.05
        other_tracking = {} # to hold the date, and the sum of "other categor"
        for key in time_data.keys():
            for k, key_ in enumerate(time_data[key]['data']):

                if key_.proportion > cut_off: # cut of value to convert a lineage to other
                    data_out[key_.pl] = []
                else:
                    key_ = key_._replace(pl="other")
                    time_data[key]['data'][k] = key_
                    if other_tracking.get(key) is None:
                        other_tracking[key] = 0.0
                    other_tracking[key] += key_.proportion

                if key_.pl not in lineages_tracked:
                    lineages_tracked.add(key_.pl) # tracking missing values from sets to initiate missing values
        
        for date in data_out["dates"]:
            # dates will hold order for iteration
            for val in time_data[date]['data']:
                if val.pl != "other": # replace was not working
                    data_out[val.pl].append(val.proportion)
        
        data_out["other"] = [other_tracking[i] for i in data_out["dates"]]
        print(data_out)
            
        return data_out 


    def cov_spectrum_to_axes(self):
        """
        Convert the json response to lists for bokeh
        """
        lineages = []
        for response in self.api_obj.loaded_api.call_api():
            if response is not None:
                if self.mut_data.get(response["Mutation"]) is None:
                    self.mut_data[response["Mutation"]] = {} # make array for muts data
                val_data = []
                sum_counts = sum([int(i['count']) for i in response['data']]) # cleaner way to do this exists
                for val in response["data"]:
                    pl = val["pangoLineage"]
                    count = int(val['count'])
                    proportion = (count / float(sum_counts)) * 100
                    if proportion < 5.0:
                        pl = "other"
                    lineages.append(pl)
                    val_data.append(data_point(pl, count, proportion))
                print("Creating Response data")
                test_sort = sorted(val_data, key = lambda t: t[1], reverse=True)
                self.mut_data[response["Mutation"]][response['Date']] = {}
                self.mut_data[response["Mutation"]][response["Date"]]["Sum"] = sum_counts
                self.mut_data[response["Mutation"]][response['Date']]["data"] = test_sort
        self.api_response_to_df(lineages)   
    
    def api_response_to_df(self, list_of_pl: list):
        """
        from the intaken data make sure every value has a data point
        """
        for mut in self.mut_data.keys():
            df = pd.DataFrame(0.0, index=list(set(list_of_pl)), columns=[i for i in self.mut_data[mut]]) # make a df of date values
            for dates in self.mut_data[mut].keys(): # iterate throught the dates
                for val in self.mut_data[mut][dates]['data']:
                    df.at[val.pl, dates] = val.proportion
            df.loc["other", :] = 0.0
            for col in df.columns: # Set the other column to the difference of whats included
                df.at["other", col] = 100.0 - df[col].sum()
            self.plot_data[mut] = df

if __name__=="__main__":
    data_cs = GatherAPIData("data/VCFParser_20220601.txt")
    JsontoFigure(data_cs).create_figures()