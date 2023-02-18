import requests
from flatten_json import flatten

def post_query(url, query):
    response = requests.post(url, '', json={'query':query})
    if response.status_code == 200:
        return response.json()

def parse_results(results):
    new_results = []
    for result in results:
        new_results.append(flatten(result))
    return new_results
