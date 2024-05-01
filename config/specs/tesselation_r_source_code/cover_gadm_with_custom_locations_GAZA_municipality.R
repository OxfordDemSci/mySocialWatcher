
options(scipen=999)

# libraries
library(cleangeo)
library(raster)
library(tmap)
library(geodata)

# working directory
setwd(file.path(dirname(rstudioapi::getActiveDocumentContext()$path), 'wd'))

# define paths
credential_path <- file.path('GAZA', 'in', 'credentials.csv')
countries_df_path <- file.path('GAZA', 'in', 'countries.csv')
results_folder_path <- file.path('GAZA', 'out')

# load functions
source(file.path('..', 'Functions_to_create_overlapping_circles_tess_for_shape_files.R'))

## ----
## Set parameters
## ----

# load csv file containing FB credentials (token and account)
# this is needed to validate the custom locations
creds_file <- read.csv(credential_path,stringsAsFactors = FALSE)
token <- creds_file$token[1]
act <- creds_file$account[1]

set_fb_credentials(token = token, act = act, version = "v17.0", min_fb_mau=1000)
SHAPE_TESS_PARAMS$query_sleep_time <- 0.1 # you can use a smaller sleep time between queries with a standard access token
SHAPE_TESS_PARAMS$sparse_query_size <- 0 # use only interior method

# specific params for Gaza collections
expanded <-  'FALSE'
location_type <- 'recent'

## ----
## 1. Generate custom locations targeting for shape files
## ----

## Required inputs

# The list of countries
# This is a .csv file with three columns: 
# (i) 'country': Name of the country
# (ii) 'iso3': The iso3 code for the country
# (iii) 'zone': The UTM zone corresponding to the country
#       UTM zones can be checked here:
#       http://www.dmap.co.uk/utmworld.htm

cntries_df <- read.csv(countries_df_path, stringsAsFactors = FALSE)

gadm_folder <- file.path('GAZA', 'in') # name of folder to save/retrieve the GADM admin files from
gadm_level <- 3

# folder names to save output
queries_folder <- paste0(results_folder_path,'/loc_queries') # folder to save the generated FB location queries
output_folder <- paste0(results_folder_path,'/saved_custom_locs') # folder to save all the generated output for later use
maps_folder <- paste0(results_folder_path,'/viz_maps') # folder to save the generated maps for visualization

log_file <- paste0(results_folder_path,'/logs/Processing_GADM_',gadm_level,'_regions_with_FB_custom_locations_log.txt') # save the processing log


## Run the custom location generation

# create the folders to save the results into
for (folder in c(gadm_folder, queries_folder,
                 output_folder, maps_folder)) {
  if (!dir.exists(folder)) {
    dir.create(folder, recursive=T, showWarnings=F)
  }
}



cntry_iso3 <- cntries_df$iso3[1]

cat("### Processing country:",cntry_iso3,"\n")

## read in the Gaza municipality shape file
cat("__*__ Reading in Gaza municipality boundaries:\n")

geo_adm2 <- st_read(file.path(gadm_folder, 'GazaStrip_MunicipalBoundaries_BaselinePop_Clean.gpkg')) 
geo_adm2 <- geo_adm2 |> rmapshaper::ms_simplify(keep = 0.04)


## Cover with custom locations for FB targeting
res_list <- generate_list_of_custom_locations_for_shape_files(reg_geo = as(geo_adm2, 'Spatial'),
                                                              idcol = 'ADM3_EN', 
                                                              zone = cntries_df$zone[1],
                                                              loc_area_cutoffs = c())


# # remove belarus overlap in exterior for pcode UA1806
# part_issue <- c(70, 98, 111,112)
# 
# res_list$UA1806$custom_locations_list$exterior_cover[c(paste0('part_',part_issue))] <- NULL


# Skip the extension step in case of invalid areas

invalid_list <- res_list
for (loc in names(invalid_list)) {
  invalid_list[[loc]] <- list()
}



# viz

mapviz_ext <- show_custom_location_covers_on_map(regions_geos = geo_adm2, 
                                                 geos_covers = res_list, 
                                                 invalid_locs = invalid_list, 
                                                 zone = cntries_df$zone,
                                                 covers_to_show = rep('exterior_cover',length(res_list)))

mapviz_int <- show_custom_location_covers_on_map(regions_geos = geo_adm2, 
                                                 geos_covers = res_list, 
                                                 invalid_locs = invalid_list, 
                                                 zone = cntries_df$zone,
                                                 covers_to_show = rep('interior_cover',length(res_list)))

# test facebook queries

fb <- get_fb_mau_estimates_for_custom_covers(res_list, invalid_list)

plot_fb <- function(mapviz, fb_df=fb){
  # mapviz=mapviz_ext
  fb_gis <- st_as_sf(mapviz[['custom_locs_geo']]) %>% 
    rename(coverType=cover) %>% 
    left_join(fb_df)
  
  fb_map <- tm_shape(fb_gis)+
    tm_fill(col='fb_mau', style = 'quantile')
  return(fb_map)
}

fb_map_int <- plot_fb(mapviz_int)
fb_map_ext <- plot_fb(mapviz_ext)

# save circles? ##############################
custom_circles_ext <- show_custom_circles_covers_on_map(regions_geos = geo_adm2,
                                                        geos_covers = res_list,
                                                        invalid_locs = invalid_list,
                                                        zone = cntries_df$zone,
                                                        covers_to_show = rep('exterior_cover',length(res_list)))
custom_circles_ext <- custom_circles_ext$custom_locs_geo |>
  left_join(fb |>
              filter(coverType=='exterior_cover') |>
              rename(id=geo_id))

st_write(custom_circles_ext, file.path('GAZA', 'out', 'gaza_municipality_custom_circles.gpkg'))



## 
new_custom_circles_ext <- st_read('gaza_municipality_custom_circles.gpkg')

# add lat/long of centroids (with error when calculating centroid from WGS84)
centroids <- sf::st_centroid(new_custom_circles_ext)

new_custom_circles_ext$lat <- sf::st_coordinates(centroids)[,'Y']
new_custom_circles_ext$long <- sf::st_coordinates(centroids)[,'X']
new_custom_circles_ext$radius <- 1


new_custom_circles_ext <- new_custom_circles_ext |> 
  st_drop_geometry() |> 
  mutate(geo_id=id) |> 
  select(geo_id, lat, long, ptid, coverType, radius)

geo_queries_ext <- get_mysw_geo_queries(new_custom_circles_ext, cover_type = 'exterior_cover',
                                        location_type='recent', expanded_type=expanded,
                                        country_code='PS', geo_source='HDX')


write(geo_queries_ext, paste0("PS_loc_queries_for_cover_by_custom_locations_municipalities_exterior.txt"))




