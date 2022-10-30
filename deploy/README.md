# mySocialWatcher
Dockerized pySocialWatcher for easy deployment on LCDS virtual machines.  

#### Current features

1. portable Dockerized deployment  
2. standardized collection specs
3. cron scheduler  
4. session logging  
5. organized data storage for long-term collections
6. compatible format for LCDS database
7. healthchecks.io notifications (email, sms, slack, etc) for server failures and/or python errors

#### Potential future features

1. Airflow monitor (optional if healthchecks are not sufficient)
2. Additional collection specs for various research questions

## Overview of Components

This dockerized pySocialWatcher collector has a few key components that are important to understand.
For the full functionality of this collector (e.g. writing collections into the LCDS SQL database), 
the machine running the container will need to be connected to the socsci network, either directly or using the vpn.
For more information about connecting to the socsci VPN, please read 
[these instructions](https://github.com/OxfordDemSci/docs/wiki/Accessing-socsci-VPN).

### Docker Container
Docker containers make software portable from one machine to another. 
They contain the operating system and any dependencies needed to run the software.
This provides stability through time as dependency updates could cause compatibility issues, etc.
Containerization also makes it easy to reproduce complex server configurations with minimal effort when 
redeploying the container on a new machine.  

The docker container for this pySocialWatcher collector is defined in `./docker-compose.yml` and `./Dockerfile`.

### pySocialWatcher Collection Specs
The folder `./specs/` contains json files with collection specifications for some collections being run at LCDS.
These predefined collection specs are available to use for your own collections and/or to modify to meet your own research goals.  

The script `./collection_specs.py` can be used to generate new collection specs (although with limited functionality at present).
These collection specs were all defined using pySocialWatcher's json builder.
You can find more information from the 
[WorldBank's pySocialWatcher tutorial](https://worldbank.github.io/connectivity_mapping/facebook_nbs/creating_a_json_for_collection.html).
Another resource that could be helpful is [Facebook's Marketing API documentation](https://developers.facebook.com/docs/marketing-api/audiences/reference/advanced-targeting).  

### Environment Variables
There are a few parameters that the collector needs that may contain private information or vary from one machine to another.
For these, we have implemented environment variables in the `./.env` file. 
You must create this file for yourself using your own local context. 
Here is an example of `.env` with some of the data truncated:

```angular2html
TOKEN=EAAqo4nk4Fi0BA...
APP=1026...
DATADIR=/share/data
HEALTHCHECK=18b93269-3198...
SQL_TOKEN=a34b27c3...
```

`TOKEN` is your Facebook Marketing API token.  
`APP` is your Facebook App ID number.  
`DATADIR` is the path where you would like to write pySocialWatcher output files.  
`HEALTHCHECK` is the [healthchecks.io](https://healthchecks.io) ID that you would like to use to monitor the container 
(i.e. get notifications if it crashes).  
`SQL_TOKEN` is your API token for writing new data into the LCDS database.

### Cron Scheduler
The cron scheduler allows you to automate continuous collections and 
to specific which collection specifications should run each day and when.
The cron schedule is defined in `./cronjob`. This includes several important features:  

1. A scheduled ping to healthchecks.io every 5 minutes,
2. Calling `/root/cron_env.sh` (created automatically on Docker build) to load environment variables before running the cron job,
3. A 24 hour timeout on the cron job so it doesn't overlap the next day's collection which could cause the Facebook API token to be disabled,
4. Calling `./collection_run.py` to start the collection with two command line arguments passed to the script:  
   A. The specification json that defines the collection, and   
   B. The data directory where outputs should be written.

### Healthchecks.io Notifications
This is a free external service that helps monitor the health of the container. 
You will need to setup your own free account and configure a health check for your collector.
This process will give you a healthcheck url that your container will ping (e.g. every 5 minutes).
If the healthcheck server does not receive a ping, it will notify you via email, SMS, Slack, Whatsapp, etc.
This dockerized pySocialWatcher container will ping the healthcheck server every 5 minutes. 
It will also send a FAIL notification if the pySocialWatcher collection throws an error (e.g. Facebook token expired).

### SQL Database 
In addition to creating csv files in pySocialWatcher's standard output format, 
this collector will write those data into the LCDS PostgreSQL database using the 
LCDS API endpoint `.../api/v1/social_media_audience/write`. 
To gain write access to the API, you will need to request an API token from the system admin.
Please see the [API documentation](http://10.131.129.27/api) for more information.

## Usage

### Running without docker
The basic collector can be run without docker using the script `./collection_run.py`.
When executing this script from the command line, you must specify two command line arguments that point to 1) your
collection specs .json file and 2) the output data directory you would like to use. Here is an example:
```angular2html
$ python3 collection_run.py ./specs/test.json ./data  
```
Running the collector without docker can be useful for local testing or one-off collections.

### Running with docker

To install and run the dockerized collector, you must first configure Docker on the machine where it will run.
The Linux commands for preparing a machine are provided in `./deploy.sh`.

Once Docker is installed, you will need to:  
1. Clone the mySocialWatcher repository to the machine,
2. Configure a `.env` file with your settings,
3. Include customized collection specs (.json) if needed,
4. Modify `./cronjob` to schedule your collections as needed, and
5. Launch the docker container from the repository directory:

```angular2html
$ cd ~/mySocialWatcher
$ docker-compose up --build -d 
```

It is recommended to run the collector on a dedicated Linux virtual machine.
Please see [these instructions](https://github.com/OxfordDemSci/docs/wiki/LCDS-virtual-machines) for setting up new LCDS virtual machines.  


