"""
First attempt at visualizeing the CovSpectrum in a dashboard using bokeh

2022-06-17: Matthew Wells
"""

from CovSpectrum_api import GatherAPIData
from bokeh.plotting import figure, show, save, output_file


class JsontoFigure:
    """
    Convert the json response from the api to make the data and create some plots
    """
    mut_data = {}
    def __init__(self, api_obj: GatherAPIData) -> None:
        self.api_obj  = api_obj
        self.cov_spectrum_to_axes()
    
    def create_figures(self):
        """
        render each individual bokeh plot
        """
        for key in self.mut_data.keys():
            p = figure(title=key, x_range=self.mut_data[key]["x"], width=1500)
            p.xaxis.major_label_orientation = "vertical"
            p.vbar(x=self.mut_data[key]["x"], top=self.mut_data[key]["y"], width=0.9)
            output_file(filename=f"outputs/{key}.html", title=key)
            save(p)


    def cov_spectrum_to_axes(self):
        """
        Convert the json response to lists for bokeh
        """
        for response in self.api_obj.loaded_api.call_api():
            if response is not None:
                self.mut_data[response["Mutation"]] = {} # make array for muts data
                x = []
                y = []
                for val in response["data"]:
                    pl = val["pangoLineage"]
                    count = int(val['count'])
                    x.append(str(pl))
                    y.append(int(count))
                print("Creating Response data")
                test_sort = zip(x, y)
                test_sort = sorted(test_sort, key = lambda t: t[1], reverse=True)
                self.mut_data[response["Mutation"]]["x"] = [i[0] for i in test_sort] 
                self.mut_data[response["Mutation"]]["y"] = [i[1] for i in test_sort] 


        


if __name__=="__main__":
    data_cs = GatherAPIData("data/VCFParser_20220601.txt")
    JsontoFigure(data_cs).create_figures()