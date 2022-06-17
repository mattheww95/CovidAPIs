"""
An initial attempt at reading from the covspectrum api

Overall this code could benefit from abstraction, with more methods being
and classes being abstracted. But this is working as a quick mockup


Docs can be found here: https://lapis.cov-spectrum.org/#filters
Docs for fields that can be queried:
All six sample endpoints can be filtered by the following attributes:

dateFrom
dateTo
dateSubmittedFrom
dateSubmittedTo
region
country
division
location
regionExposure
countryExposure
divisionExposure
ageFrom
ageTo
sex
host
samplingStrategy
pangoLineage (see section "Filter Pango Lineages")
nextcladePangoLineage
nextstrainClade
gisaidClade
submittingLab
originatingLab
nucMutations (see section "Filter Mutations")
aaMutations (see section "Filter Mutations")
nextcladeQcOverallScoreFrom
nextcladeQcOverallScoreTo
nextcladeQcMissingDataScoreFrom
nextcladeQcMissingDataScoreTo
nextcladeQcMixedSitesScoreFrom
nextcladeQcMixedSitesScoreTo
nextcladeQcPrivateMutationsScoreFrom
nextcladeQcPrivateMutationsScoreTo
nextcladeQcSnpClustersScoreFrom
nextcladeQcSnpClustersScoreTo
nextcladeQcFrameShiftsScoreFrom
nextcladeQcFrameShiftsScoreTo
nextcladeQcStopCodonsScoreFrom
nextcladeQcStopCodonsScoreTo

2022-06-15: Matthew Wells
"""
import requests
from typing import NamedTuple, List
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# to request something can make a dict of parameters and pass it to requests get

parameters = {
    "nucMutations": "241T",
    "dateFrom": "2020-01-06",
    "aaMutations": ...,
    "country": "Canada",
    "pangoLineage": ...,
    "nextstrainClade": ...
}

#response_ = requests.get("https://lapis.cov-spectrum.org/open/v1/sample/aggregated", params=parameters)

class GatherAPIData:
    """
    This class will parse the submission sheet and actually call and process requests
    """

    def __init__(self, vcfparser_sheet: str) -> None:
       self.vcfparser_sheet = vcfparser_sheet
       self.loaded_api = self.gather_api_data()

    def gather_api_data(self):
        """
        Actually call the api and collect the data 
        """
        mutation_queries = IntakeMutationSheet(self.vcfparser_sheet)
        out = CovSpectrumAPICaller(mutation_queries.api_requests)
        return out

class IntakeMutationSheet:
    """
    Intake a vcfparser sheet used and parse out the various nucleotide changes to check
    """
    api_requests = []
    def __init__(self, intake_sheet, debug_mode: bool = True):
        self.intake_sheet = intake_sheet
        self.debug_mode = debug_mode
        self.process_intake_sheet()

    def process_intake_sheet(self):
        """
        Pull out all of the mutations to query in the vcfparser sheet,
        to then hand off to the rest api
        """
        vcfparser_col = "NucName" # the main column on interest
        df = pd.read_csv(self.intake_sheet, sep="\t")
        if self.debug_mode:
            df = df.head()
        # Type is a column in the sheet that hold info about the substitution
        # Del and Insertions are tricky as insertions dont quite exist...
        nucleotides = df[vcfparser_col].loc[df["Type"] == "Sub"]
        nucleotides = nucleotides.apply(lambda x: x[1:]) # removing reference character
        nucleotides = nucleotides.unique() 
        self.positions_to_queries(nucleotides=nucleotides)
    
    def positions_to_queries(self, nucleotides):
        """
        convert the nucleotides into some nice queries!
        """
        for value in nucleotides:
            cur_dt = datetime.today() # requests done so all time six months then 0 months
            dt_six_months = cur_dt + relativedelta(months=-6)
            dt_three_months = cur_dt + relativedelta(months=-3)
            self.api_requests.append(CovSpectrumParameters(fields="pangoLineage", nucMutations=value, dateFrom="2021-01-06"))
            self.api_requests.append(CovSpectrumParameters(fields="pangoLineage", nucMutations=value, dateFrom=str(dt_six_months.strftime("%Y-%m-%d"))))
            self.api_requests.append(CovSpectrumParameters(fields="pangoLineage", nucMutations=value, dateFrom=str(dt_three_months.strftime("%Y-%m-%d"))))


class CovSpectrumParameters(NamedTuple):
    """
    Call the Cov Spectrum api with the input parameters. 
    This class will stage the parameters to query as their may be multiple
    """
    fields: str = None # this guy is special in that it returns a break down of the category provided e.g. pango lineage country etc.
    nucMutations: str = None
    dateFrom: str = None # data appears to be from a string in the api
    aaMutations: str = None
    country: str = None
    pangoLineage: str = None
    nextstrainClade: str = None


class CovSpectrumAPICaller:
    """
    Call the cov spectrum API to return data about each class
    """
    api_uri = "https://lapis.cov-spectrum.org/open/v1/sample/aggregated"
    def __init__(self, api_requests: List[CovSpectrumParameters]):
        self.api_requests = api_requests


    def call_api(self):
        """
        Using the parameters initialized call the cov spectrum api and get some information
        """
        for req in self.api_requests:
            data_ = requests.get(self.api_uri, params=req._asdict())
            if data_.status_code >= 400:
                print(f"Could not get results for request: {req}") # need to prepare a logger for this
                yield None
            else:
                response_info = {}
                response_info["Mutation"] = req.nucMutations
                response_info["data"] = data_.json()['data']
                yield response_info
                #yield response_info
               # print("Response", data_.status_code)
               # print("Info", data_.json()['info'])
               # print("Data", data_.json()['data'])
               # print("Errors", data_.json()['errors'])


if __name__ == "__main__":
    test_list = [
        CovSpectrumParameters(nucMutations="241T"), 
        CovSpectrumParameters(nucMutations="241T", country="Canada"), 
        CovSpectrumParameters(nucMutations="241T", country="Canada", dateFrom="2021-01-06"),
        CovSpectrumParameters(fields="country", pangoLineage="BA.5", dateFrom="2021-01-06"),
        CovSpectrumParameters(fields="pangoLineage", nucMutations="23040G", dateFrom="2021-01-06")]

    #t1 = CovSpectrumAPICaller(test_list)
    #t1.call_api()
    #IntakeMutationSheet("./data/VCFParser_20220601.txt").process_intake_sheet()
    api_data =  GatherAPIData("data/VCFParser_20220601.txt")
    api_data.gather_api_data()