library(dplyr)
library(tidyr)
library(readr)
library(here)
library(ggmap) # to geolocate with mutate_geocode through Google API
#library(tmaptools) # to geolocate with geocode_OSM through Open Street Map API
#library(fedmatch) # to clean names of locations with clean_strings

# Read csv file with names of locations to be geolocated

geo_keys <- read_csv(here("targets_csv", "city.csv"))

# Manually clean Cote d'Ivoire

geo_keys$country_name[geo_keys$country_name == "Côte d&#039;Ivoire"] <- "Côte d'Ivoire"

# Add a column that concatenates city, region, and country name

geo_keys <- geo_keys %>% 
  mutate(city_country = paste0(name, ", ", region, ", ", country_name))

# Set Google API key

register_google(key = "[your Google API key]")


# Add locations' coordinates (lat, lon) using Google Geocoding API

cities_google <- mutate_geocode(geo_keys, 
                                city_country,
                                output = "latlon") # possible to change to get +- info


# Add locations' coordinates (loat, lon) using Open Street Map (OSM) API

#geo_keys$clean_city_name <- clean_strings(geo_keys$city_country)

#cities_osm <- geocode_OSM(geo_keys$city_country[1:10],
#                                 details = FALSE, as.data.frame = TRUE)


# Save output as a csv file

#write_csv(cities_google, here("data_processed",
#                              "cities_google.csv"))




