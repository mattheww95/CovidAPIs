"""
An initial attempt at reading from the covspectrum api
"""
import requests



# to request something can make a dict of parameters and pass it to requests get

parameters = {
    "nucMutations": "241T",
    "dateFrom": "2020-01-06",
    "country": "Canada"
}

response_ = requests.get("https://lapis.cov-spectrum.org/open/v1/sample/aggregated", params=parameters)



print(response_.json()['data'])