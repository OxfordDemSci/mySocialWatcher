
options(scipen=999)

# libraries
library(cleangeo)
library(raster)
library(tmap)
library(geodata)

# working directory
setwd('K:/DemSci/projects/2023_WHO_Ukraine_Population/data/tmp/gadm2_tessellation')

# define paths
credential_path <- file.path('wd', 'UKR', 'in', 'credentials.csv')
countries_df_path <- file.path('wd', 'UKR', 'in', 'countries.csv')
results_folder_path <- file.path('wd', 'UKR', 'out')

# load functions
source(paste0(dirname(rstudioapi::getActiveDocumentContext()$path),
              "/Functions_to_create_overlapping_circles_tess_for_shape_files.R"))

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

# specific params for UKR collections
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

cntries_df <- read.csv(countries_df_path,stringsAsFactors = FALSE)

gadm_folder <- file.path('wd', 'UKR', 'in') # name of folder to save/retrieve the GADM admin files from
gadm_level <- 2

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

## read in the COD-PS shape file
cat("__*__ Reading in COD-PS adm 2 shape files:\n")

geo_adm2 <- st_read(paste0(gadm_folder, '/cod-ab/UKR_AdminBoundaries_EM.gdb'), layer='ukr_admbnda_adm2_sspe_20230201_EM') 
geo_adm2 <- geo_adm2 |> rmapshaper::ms_simplify(keep = 0.04)


## Cover with custom locations for FB targeting
res_list <- generate_list_of_custom_locations_for_shape_files(reg_geo = as(geo_adm2, 'Spatial'),
                                                              idcol = 'admin2Pcode', 
                                                              zone = cntries_df$zone[1],
                                                              loc_area_cutoffs = c())


# remove belarus overlap in exterior for pcode UA1806
part_issue <- c(70, 98, 111,112)

res_list$UA1806$custom_locations_list$exterior_cover[c(paste0('part_',part_issue))] <- NULL

nlocs <- length(res_list)

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

# pysw query
res_df <- export_list_of_custom_locations(res_list, invalid_list)

res_df <- res_df |> 
  left_join(fb) |> 
  filter(!grepl('Your ad includes or excludes locations that are currently restricted', error_message))


get_pysw <- function(geo_covers_df, cover_type ,location_type='recent', expanded_type=expanded){
  geo_covers_df <- geo_covers_df %>% 
    filter(coverType==cover_type)
  
  all_geo_queries <- c()
  for (geoid in levels(as.factor(geo_covers_df$geo_id))) {
    # geoid =  "UKR.1.1_1"
    Isub <- geo_covers_df$geo_id == geoid
    # should we limite the number of significant digits in the lat/long ????????????????????????????????????????????
    custom_query <- paste('{"latitude":',geo_covers_df$lat[Isub],
                          ', "longitude":',geo_covers_df$long[Isub],
                          ',"radius":',geo_covers_df$radius[Isub],
                          ',"distance_unit": "kilometer"}',sep="", collapse = ", ")
    
    geo_query <- paste('{"name":"custom_locations", "values":[',custom_query,'],',
                       '"location_types": ["',location_type,'"], "pySocialWatcherReference": {"geo_id": "',
                       geoid,'" ,"geo_source": "COD-PS", "coverType": "',cover_type,'" , "expanded": "',expanded_type,'"},',
                       '"country_code": "UA"}',sep="")
    all_geo_queries <- c(all_geo_queries, geo_query)
    
  }
  return(all_geo_queries)
}

geo_queries_int <- get_pysw(res_df, cover_type = 'interior_cover')
geo_queries_ext <- get_pysw(res_df, cover_type = 'exterior_cover')



## save the results
write(geo_queries_int, paste(queries_folder,"/",cntry_iso3,paste0("_loc_queries_for_cover_by_custom_locations_GADM",gadm_level,"_regions_interior.txt"),sep=""))
write(geo_queries_ext, paste(queries_folder,"/",cntry_iso3,paste0("_loc_queries_for_cover_by_custom_locations_GADM",gadm_level,"_regions_exterior.txt"),sep=""))

save(res_list,  
     file = paste(output_folder,"/",cntry_iso3,"_custom_locations_coverage_data.RData",sep=""))

# save map viz
tmap_save(mapviz_ext$map_viz,paste(maps_folder,"/",cntry_iso3,"_GADM",gadm_level,"_custom_locations_coverage_map_exterior.html",sep=""),
          selfcontained = FALSE)
tmap_save(mapviz_int$map_viz,paste(maps_folder,"/",cntry_iso3,"_GADM",gadm_level,"_custom_locations_coverage_map_interior.html",sep=""),
          selfcontained = FALSE)
tmap_save(fb_map_ext,paste(maps_folder,"/",cntry_iso3,"_GADM",gadm_level,"_custom_locations_fb_map_exterior.png",sep=""))
tmap_save(fb_map_int,paste(maps_folder,"/",cntry_iso3,"_GADM",gadm_level,"_custom_locations_fb_map_interior.png",sep=""))


