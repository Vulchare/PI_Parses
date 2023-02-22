import requests

import json
from functools import reduce
from typing import Union

apiURL = "https://www.warcraftlogs.com/api/v2/client"
tokenURL = "https://www.warcraftlogs.com/oauth/token"
userID = "9887d24a-67a8-4b97-9087-310af0f78535"
userSecret = "OLb1yI1figyy7I7ssjnijTUTJ2A1UDqtk7kImICF"


def get_token(store : bool = False) -> requests.models.Response:
    """Retrieves access token for a given client id and secret."""
    data = {"grant_type": "client_credentials"}


    auth = userID, userSecret
    with requests.Session() as session:
        response = session.post(tokenURL ,
                                                data = data ,
                                                auth = auth)

    ##stores the token if the the request was authorized
    if store and response.status_code == 200:
        store_token(response)
    return response

def store_token(response : requests.models.Response) -> None:
    """Stores token to a hidden json file."""
    try:
        with open(".credentials.json" , mode = "w+" , encoding = "utf-8") as file:
            json.dump(response.json() , file)
    except OSError as e:
        print(e)
        print("Could not create the file!")


def retrieve_token() -> Union[None , dict[str , str]]:
    """Extracts access token from json file."""
    try:
        with open(".credentials.json" , mode = "r+" , encoding = "utf-8") as file:
            return json.load(file)
    except OSError as e:
        print(e)
        return None

def retrieve_headers() -> dict[str , str]:
    """Retrieves authorization headers to use the public wclogs API."""
    return {"Authorization":f"Bearer {retrieve_token().get('access_token')}"}

##Specify a query

reportData = """{
  worldData 
  {
    encounter(id:747) 
    {
        characterRankings
    }
  }
}"""


def getData(query : str , **kwargs) -> Union[list[dict[str , Union[str , int]]] , str]:
    """Sends a general query to wclogs API to retrieve report data. The kwargs contain information about the particular endpoint.
    we wish to extract data from. For instance, if we want to extract reportData we must specify as keyword argument the code
    for the report. In general, we the kwargs must contain all the arguments of the query otherwise an exception will be raised.
    Furthermore, you can also specify a ditchItems key which drops unnecessary information."""

    ditchItems = kwargs.pop("ditchItems") if "ditchItems" in kwargs else None
    data = {"query" : query , "variables" : kwargs}
    with requests.Session() as session:
        session.headers = retrieve_headers()
        response = session.get(apiURL , json = data)
    if response.status_code == 200:
        response = response.json()
        return reduce(lambda acc , val : acc.get(val) , ditchItems , response) if ditchItems else response
    return response.json().get("error")

def main():
    ##Step I: retrieve access token for our application
    response = get_token(store = True)
    #Step II: get data for our application
    #example code
    code = "Ly9Q1NCXtYzaK7cR"
    print(getData(reportData, code = code))

if __name__ == "__main__": main()