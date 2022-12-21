---
title: API Docs
output: rmdformats::readthedown
---

# Social Media Audience

The API endpoints located at `http://18.135.72.18/api/v1/[endpoint]` 
provide access to the LCDS database containing counts of social media users for 
specific locations, time periods, and demographic groups. This API requires 
approved credentials for access.  

**Note:** By accessing any Meta Platform Data returned by this API, you are agreeing to comply with 
<a href="https://developers.facebook.com/terms" target="_blank">Meta's Platform Terms</a>.

## Overview of all endpoints

**./api/v1/query**  
Returns social media audience estimates for specific locations, dates, and demographic groups.

**./api/v1/write**  
Write new data into the database (requires authentication with write-access).


## Endpoint: query

This API endpoint is for querying data from *social_media_audience* database. 
You can use it to pull a subset of data directly into R or Python (examples below).  

**Note:** If your query results exceed 100,000 rows, then only the first 100,000 
will be returned along with a status code of 206 (partial content) rather than a 
success code (200).

URL: `http://18.135.72.18/api/v1/query`  

Arguments syntax: `http://18.135.72.18/api/v1/query?argument1=value1&argument2=value2`  


**API Arguments**  

*Required Arguments*  

Argument | Description
|:-- |:-----------
token | API token for read access (contact [douglas.leasure@demography.ox.ac.uk](mailto:douglas.leasure@demography.ox.ac.uk))
platform | Name of platform where data were collected. Acceptable values: facebook, instagram

*Optional Arguments*  

Argument | Description 
|:-- |:----------- 
country | A single country code using ISO-2 format (see <a href="https://www.iban.com/country-codes">https://www.iban.com/country-codes</a>). If omitted, all countries will be returned, but please note that this may result in longer processing time.
gender | Gender of the population represented by data. Acceptable values: 0, 1, 2, where 0=all, 1=male, 2=female.
age_min | Lower bound of age of the audience size reported. Default = 0.
age_max | Upper bound of age of the audience size reported. Default = 999.
date_start | Earliest date to include in the query result
date_end | Latest date to include in the query result
collection | The name of a collection from which you would like to return data. The names of all collections can be obtained from the [collections endpoint](#endpoint-collections).
contributor_id | ID number of contributor whose data you would like to return
valid | Return only data marked as valid by contributors? Default = true. Acceptable values: true, t, yes, y, on, 1. All other values will be treated as: false.

**API Response**  
The API will return a json response with four elements:

Element | Description 
|:-- |:----------- 
status | http status code
message | Message describing outcome of operation writing to the database
timestamp | Date and time of response
data | Data resulting from query in json format

For example:
```
{
  "message": "OK: Data successfully selected from database.",
  "status": "200",
  "timestamp": "2022-01-03 18:30:26+00",
  "data": '{"id":{"0":1362778,"1":1362779,"2":1362780,"3":1362781, ... }'
}
```

**Examples**

*Query data using a url:*  
```
http://18.135.72.18/api/v1/query?platform=facebook&country=GB&gender=0&date_start=2020-03-11
```

*Query data from Python:*  
```
# import packages
import requests
import pandas as pd

# query arguments
args = {
  "token": "xxxxxxxxx",
  "platform": "facebook",
  "country": "GB",
  "gender": "0",
  "date_start": "2020-03-11"
  }

# submit query as GET request
response = requests.get(url='http://18.135.72.18/api/v1/query', params=args)

# format response as dictionary
response = response.json()

# check status
print(response.get('status'))
print(response.get('message'))

# extract data as pandas dataframe
if response.get('status') == 200:
  data = pd.DataFrame(json.loads(response.get('data')))
```

**Query data from R:**  

```
# import packages
library('httr')
library('jsonlite')
options(scipen = 999)

# query arguments
args <- list(token = "xxxxxxxxx",
             platform = "facebook",
             country = "GB",
             gender = 0,
             date_start = "2020-03-11")

# submit query as GET request
response <- httr::GET(url = 'http://18.135.72.18/', 
                      path = 'api/v1/query',
                      query = args)

# format response as list
response <- jsonlite::fromJSON(httr::content(response, as='text'))

# check status
print(response$status)
print(response$message)

# extract data in various formats
if(response$status == 200){
  
  # json string
  data <- response$data
  
  # json -> list of lists
  data <- jsonlite::fromJSON(data)
  
  # list of lists -> data.frame with cells containing lists
  # note: this is a convenient format for dealing with JSONs for some data.frame cells in R.
  data <- as.data.frame(do.call(cbind, data))
  
  #-- unlist data --#
  
  # identify columns storing json objects
  json_cols <- c('geo_locations','all_fields','targeting','response')
  
  # non-json cells: unlist
  for(name in names(data)[!names(data) %in% json_cols]){
    data[,name] <- unlist(data[,name])
  }
  
  # json cells: lists -> json strings
  for(name in json_cols){
    data[,name] <- unlist(lapply(data[,name], jsonlite::toJSON))
  }
}
```


## Endpoint: list_collections

This API endpoint returns a list of all collection names that you currently have 
access to in the *social_media_audience* database. 

URL: `http://18.135.72.18/api/v1/list_collections`  

Arguments syntax: `http://18.135.72.18/api/v1/list_collections?token=12345`  

**Note:** An API token is required to access this endpoint. Please contact [douglas.leasure@demography.ox.ac.uk](mailto:douglas.leasure@demography.ox.ac.uk) for more information.


**API Arguments**  

*Required Arguments*  

Argument | Description
|:-- |:-----------
token | API access token (contact [douglas.leasure@demography.ox.ac.uk](mailto:douglas.leasure@demography.ox.ac.uk))


*Optional Arguments*  

None

**API Response**  
The API will return a json response with four elements:

Element | Description 
|:-- |:----------- 
status | http status code
message | Message describing outcome of operation writing to the database
timestamp | Date and time of response
data | Data resulting from query in json format

For example:
```
{
  "message": "OK: Collections successfully queried from database.",
  "status": "200",
  "timestamp": "2022-01-03 18:30:26+00",
  "data": '{"0": {"collection_id":1, "collection_name":"my_collection", ...}}'
}
```


## Endpoint: monitor_collections

This API endpoint returns a count of new data for each of your collections that 
were written into the database over the past several days. 

URL: `http://18.135.72.18/api/v1/monitor_collections`  

Arguments syntax: `http://18.135.72.18/api/v1/monitor_collections?token=12345&days=7`  

**Note:** An API token is required to access this endpoint. Please contact [douglas.leasure@demography.ox.ac.uk](mailto:douglas.leasure@demography.ox.ac.uk) for more information.


**API Arguments**  

*Required Arguments*  

Argument | Description
|:-- |:-----------
token | API access token (contact [douglas.leasure@demography.ox.ac.uk](mailto:douglas.leasure@demography.ox.ac.uk))


*Optional Arguments*  

Argument | Description
|:-- |:-----------
days | (default=7) Number of prior days leading up to today to include with the monitoring summary. 

**API Response**  
The API will return a json response with four elements:

Element | Description 
|:-- |:----------- 
status | http status code
message | Message describing outcome of operation writing to the database
timestamp | Date and time of response
data | Data resulting from query in json format

For example:
```
{
  "message": "OK: Your collections successfully queried.",
  "status": "200",
  "timestamp": "2022-01-03 18:30:26+00",
  "data": '{"migrationuk_tue_men": {"collection_id": 12, "2022-12-21": {"facebook": 0, "instagram": 0}, ...}}'
}
```


## Endpoint: write

URL: `http://18.135.72.18/api/v1/write`  

Arguments syntax: `http://18.135.72.18/api/v1/write?argument1=value1&argument2=value2`  

This API endpoint is for writing data into the *social_media_audience* database. 
You can use it to write data into the database directly from R or Python (example below).  

**Note:** An API token is required to access this endpoint. Please contact [douglas.leasure@demography.ox.ac.uk](mailto:douglas.leasure@demography.ox.ac.uk) for more information.

**API Arguments**  

*Required arguments*  

Argument | Description
|:-- |:-----------
token | API token for write access (contact [douglas.leasure@demography.ox.ac.uk](mailto:douglas.leasure@demography.ox.ac.uk)).
valid | Indicates if data are valid. Invalid data will not persist in the database. Default="False". Acceptable values (not case sensitive): "true", "t", "y", "yes", "on", "1". All other values will be interpreted as "False".
platform | Name of platform where data were collected. Acceptable values: "facebook", "instagram".
timestamp | Timestamp in Unix epoch format (seconds since 1 JAN 1970 UTC) corresponding to the time of the original data collection.
country | Country code of data collection using ISO-2 format (see <a href="https://www.iban.com/country-codes">https://www.iban.com/country-codes</a>).
gender | Gender of the population represented by data. Acceptable values: "0", "1", "2", where 0=all, 1=male, 2=female.
geo_locations | Definition of geolocation in json format. See docs for pySocialWatcher or Facebook Marketing API for more information.

*Require at least one of these arguments*  

Argument | Description 
|:-- |:----------- 
dau | Daily active users
mau | Monthly active user
mau_lower | Lower bound of monthly active users
mau_upper | Upper bound of monthly active users

*Optional arguments*  

Argument | Description 
|:-- |:----------- 
collection | (recommended) The name of the collection. This is will help filter results later. The [collections endpoint](#endpoint-collections) provides a list of existing collections names, or a new collection name can be created when writing new data. 
all_fields | (recommended) All fields of special targeting audience specification. This is a default field returned from pySocialWatcher as a string representation of a Python tuple of tuples.
targeting | (recommended) Audience targeting json as submitted to Facebook API. This is a default field returned from pySocialWatcher.
response | (recommended) Response from Facebook API. This is a default field returned from pySocialWatcher as a string representation of a Python bytes array.
age_min | (default = 0) Lower bound of age of the audience size reported. 
age_max | (default = 999) Upper bound of age of the audence size reported. 

**API Response**  
The API will return a json response with three elements:

Element | Description 
|:-- |:----------- 
status | http status code
message | Message describing outcome of operation writing to the database
timestamp | Date and time of response

For example:  
```
{
  "message": "OK: Data successfully written to database.",
  "status": "200",
  "timestamp": "2022-01-03 18:30:26+00"
}
```

**Examples**  

*Submit data as a url:*    

```
http://18.135.72.18/api/v1/write?token=[your token]&valid=true&platform=facebook&timestamp=1640574003&country=GB&gender=0&dau=1000&geo_locations={'name': 'countries', 'values': ['GB'], 'location_types': ['home']}
```

*Submit data from Python:*  

```
import requests

args = {
  "token": "[your token]",
  "valid": "true",
  "platform": "facebook",
  "timestamp": "1640574003",
  "country": "GB",
  "gender": "0",
  "dau": "345",
  "mau_lower": "1000",
  "mau_upper": "3000",
  "geo_locations": "{'name': 'countries', 'values': ['GB'], 'location_types': ['home']}"
  }

response = requests.get(url='http://18.135.72.18/api/v1/write', params=args)
response.text
```

**Note:** The `valid` argument will default to `false` if you do not explicitly set it to `true`. If `false`, the data you submit will be removed from the database at midnight. This is intended to allow for testing and to require data contributors to explicitly verify when valid data are being submitted that should be retained indefinitely.  

## PostgreSQL

In most cases, it is preferable to query the PostgreSQL server using the API 
endpoints above, but it can be useful to connect directly to the SQL server (read-only) to:  

1. Browse the database using a GUI like [DBeaver](https://dbeaver.io)  
2. Submit advanced SQL queries not currently supported by the `/query` API endpoint (see [query section](#query)).  

**Note:** You must be connected to the University of Oxford VPN 
(i.e. Cisco Anyconnect client) to connect directly to the database.

**SQL Server Information**  

Attribute | Value
|:--|:-----|
Hostname | 18.135.72.18
Port | 5432
Database | social_media_audience
User | reader
Password | [contact douglas.leasure@demography.ox.ac.uk]

**Examples**  

*SQL query from Python*  

```
# import packages
import psycopg2
import pandas as pd

# connect to database
conn = psycopg2.connect(host='18.135.72.18', database='social_media_audience', user='reader', password='#####')

# SQL query
sql_query = "SELECT * FROM facebook WHERE country = 'GB' AND platform = 'facebook' AND date = '2022-01-01'"

# retrieve data as pandas dataframe
data = pd.read_sql(sql_query, conn)
```

See this excellent [PostgreSQL Tutorial](https://www.postgresqltutorial.com/what-is-postgresql/) or the official [PostgreSQL documentation](https://www.postgresql.org/) for more information about syntax for advanced SQL queries. Of particular interest, may be [querying data stored in JSON format](https://www.postgresqltutorial.com/postgresql-json/) such as the specific social media audience targeting parameters found in the following columns in the *social_media_audience* database: *geo_locations*, *all_fields*, *targeting*, and *response*.

See the [psycopg2 documentation](https://www.psycopg.org/docs/) for more information about the *psycopg2* Python module. Of particular interest may be using cursors rather than pandas (as the example above) to better handle large SQL results. See a basic example [here](https://www.psycopg.org/docs/usage.html)).
