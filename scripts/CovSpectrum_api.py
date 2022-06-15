"""
An initial attempt at reading from the covspectrum api

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

"""
import requests
from typing import NamedTuple, List
import datetime

# to request something can make a dict of parameters and pass it to requests get

parameters = {
    "nucMutations": "241T",
    "dateFrom": "2020-01-06",
    "aaMutations": ...,
    "country": "Canada",
    "pangoLineage": ...,
    "nextstrainClade": ...
}

response_ = requests.get("https://lapis.cov-spectrum.org/open/v1/sample/aggregated", params=parameters)

class CovSpectrumParameters(NamedTuple):
    """
    Call the Cov Spectrum api with the input parameters. 
    This class will stage the parameters to query as their may be multiple
    """
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
            print("Response", data_.status_code)
            print("Info", data_.json()['info'])
            print("Data", data_.json()['data'])
            print("Errors", data_.json()['errors'])

#print(response_.json()['data'])


if __name__ == "__main__":
    test_list = [
        CovSpectrumParameters(nucMutations="241T"), 
        CovSpectrumParameters(nucMutations="241T", country="Canada"), 
        CovSpectrumParameters(nucMutations="241T", country="Canada", dateFrom="2021-01-06"),
        CovSpectrumParameters(pangoLineage="BA.5", dateFrom="2021-01-06")]
    
    t1 = CovSpectrumAPICaller(test_list)
    t1.call_api()