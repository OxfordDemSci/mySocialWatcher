# mySocialWatcher

This repository contains a scaleable and containerised version of pySocialWatcher ([Araujo et al. 2017](https://doi.org/10.1145/3091478.3091513)). pySocialWatcher is a Python package that makes it easier to query the Meta Marketing API to get counts of active users on Meta's social media platforms (e.g. Facebook, Instagram). This repository containerises pySocialWatcher so that many instances can be run simultaneously. It also includes a containerised PostgreSQL database and REST API where all the data can be stored centrally to be easily queried later from the database or API. 

## Components

**Collectors:** Each mySocialWatcher collector is a docker container that runs an instance of pySocialWatcher to query Meta's marketing API and save the responses in .csv format. Many collectors can be orchestrated in a single `docker-compose.yml` file and these can be scheduled to launch at defined intervals using a compute scheduler such as cron. 

The pySocialWatcher version used here has been modified from the original (Araujo et al. 2017) to include error handling and minor updates to maintain compatibility with new versions of Meta's marketing API. The specifications for individual collections (e.g. geographies, demographics, and other targeting characteristics) are defined as JSON files using the pySocialWatcher format. 

**Datahub database:** The centralised database runs as as dockerised PostgreSQL database that stores data collected by the entire constellation of collectors. The database maintains the pySocialWatcher data format for compatibility with other pySocialWatcher collections. It stores the original unmodified JSON responses from Meta's marketing API and extrapolates additional data columns for easy filtering. The database can be directly queried to filter data by geography, demographics, and behaviours of Meta audiences. 

**Datahub API:** The API is a dockerised Flask API that serves two primary functions: writing data into the database and querying data from the database. The API can easily be replicated to increase capacity, service multiple clusters of collectors, or to write into more than one database instance.

The `write` endpoint conducts checks of data integrity before writing it into the database. The `query` endpoint provides arguments allowing historical data collections to be easily queried for a range of dates or other data characteristics. Additional endpoints are provided that provide queried data in cleaner formats and to provide basic monitoring of ongoing collections.

**Crawler:** The crawler is a dockerised Python process that simply reads the csv files from one or more collectors, processes each row of data, and writes it into the database through the API while keeping logs of any errors that arise for individual rows of data. The crawler can be launched with numerous replicas defined in its `docker-compose.yml` to increase crawl capacity. 

# Repo Organisation

**./config/**  The config folder contains files need to configure data collection specifications and API access credentials. 

**./config/collections/** The collections folder contains scripts that generate all of the files needed to configure a mySocialWatcher collector. 

**./config/specs/** The specs folder contains examples of collection specs that have been used to configure collectors for various projects to provide templates for future work. 

**./config/private/** This folder is excluded from GitHub for privacy reasons. It contains access tokens for Meta's API, datahub credentials, and datahub API tokens needed for write-access to the database. It may also include email configurations for email-based notifications of collector warnings and errors. The folder `./config/_example_private/` provides an example of the files that may be included here. 

**./data/** This folder is excluded from GitHub for data protection purposes. Data created by collectors and crawlers are saved here. 

**./docker/** The docker folder contains all of the docker files to build collecters, crawlers, datahub databases, and datahub APIs for specific projects. 

**./mySocialWatcher/** Source code for all mySocialWatcher components.

**./pySocialWatcher/** Source code for all pySocialWatcher components, built on top of the original source code from Aruajo et al. (2017).

**./scratch/** Scratch workspace for code used in testing or other purposes. 

**./utils/** Bash scripts used to help monitor servers running mySocialWatcher components.

# Usage

### Collectors

One or more collectors can be configured using the following steps (see existing collectors for specific examples):
1. Create a folder for your new collector in `./docker/collectors/`. 
2. Create a `docker-compose.yml` to define one or more containers that will each run a collector. 
3. Create a sub-folder for each collector using the same path that you defined for the collector in the `docker-compose.yml`. 
4. Add one or more collection specs in JSON format into the collector sub-folders. See `./config/specs/` for examples. 
5. Add a file named `credentials.csv` to each collector sub-folder. This should contain the Meta API token and app ID--separated by a comma--that you want to use for this collection. 
6. If you specified the build arg `email_notification=TRUE` in your docker-compose, then you must include a `yagmail.csv` in the collector sub-folder to provide credentials for sending email notifications. See `./config/_example_private/yagmail.csv` for an example. 
7. (optional) Create a bash script `deploy.sh` in your primary collector folder to document steps used to configure the collectors on a remote server.
8. (optional) Create a `collector_crontab` file to document the cron scheduling used for the collector. 
9. (optional) Collection specs (JSON) and scripts used to generate all of the required collector configuration files can be saved into `./config/` for future use.  

Once all of the collector configuration files are in place, you can launch the containers as background instances using `docker compose up -d` from within the collector directory.

### Datahub (database + API)
The datahub requires an environment file to exist in `./docker/datahub/.env` that defines database and API credentials. See `./docker/datahub/env_example` for an example. 

The database and API can be launched as background processes by executing `docker compose up -d` from within `./docker/datahub/`. 

Once running the API can be accessed from `https://localhost/api/v1` and the database connection is available on localhost port 5432.

### Crawlers
The crawlers require an environment file to exist in `./docker/crawler/.env` to define a data directory and datahub API credentials.

A single crawler can be launched by launched as a background process by executing `docker compose up -d` from `./docker/crawler/`. 

Many crawlers can be launched simultaneously using `docker compose -f docker-compose-with-replicas.yml up -d`. Be sure to edit `./docker/crawlers/docker-compose-with-replicas.yml` to define how many replica crawlers you want to launch. Crawlers will create temporary files in the appropriate sub-folder of `./data/crawler/` to indicate files that are currently being crawled for coordination across crawlers. If the processes are killed before finishing (e.g. reboot), then these temporary files need to be deleted or the files will never be recrawled. 

# Contributing

Contributions are welcome! Thanks to everyone who has contributed already, particularly [@caseybreen](https://github.com/caseybreen), [@edarin](https://github.com/edarin), [@vallerrr](https://github.com/vallerrr), and [@mfatehkia](https://github.com/mfatehkia)!

Please feel free to fork the repo, open issues, and submit pull requests to help resolve issues. 

# License
You are free to use, modify, and share the code in this repository under the terms of a [GNU General Public License v3](https://www.gnu.org/licenses/quick-guide-gplv3.html) (see `./LICENSE` file for full terms of license). 