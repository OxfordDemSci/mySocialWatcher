## Approximate GADM 2 locations with FB custom locations
##


library(cleangeo)
library(raster)
library(tmap)
library(geodata)

source("Functions_to_create_overlapping_circles_tess_for_shape_files.R")
args <- commandArgs(trailingOnly = TRUE)
# args <- c('/Users/valler/Dropbox/dgg_research/subnational/tessellation/files/private/credential.csv','/Users/valler/Dropbox/dgg_research/subnational/tessellation/files/tessellation/specs/to_tessellate/test.csv','/Users/valler/Dropbox/dgg_research/subnational/tessellation/files/tessellation/results')

credential_path <- args[1]
countries_df_path <- args[2]
results_folder_path <- args[3]

## ----
## Set parameters
## ----

# load csv file containing FB credentials (token and account)
# this is needed to validate the custom locations
creds_file <- read.csv(credential_path,stringsAsFactors = FALSE)
token <- creds_file$token[1]
act <- creds_file$account[1]

set_fb_credentials(token = token, act = act, version = "v19.0",min_fb_mau=1000)
SHAPE_TESS_PARAMS$query_sleep_time <- 0.1 # you can use a smaller sleep time between queries with a standard access token


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

gadm_folder <- "../../files/gadm/" # name of folder to save/retrieve the GADM admin files from
gadm_level <- 1
# folder names to save output
queries_folder <- paste0(results_folder_path,'/loc_queries') # folder to save the generated FB location queries
coverage_stats_folder <- paste0(results_folder_path,'/area_coverage_stats') # folder to save the area coverage info files
output_folder <- paste0(results_folder_path,'/saved_custom_locs') # folder to save all the generated output for later use
maps_folder <- paste0(results_folder_path,'/viz_maps') # folder to save the generated maps for visualization

log_file <- paste0(results_folder_path,'/logs/Processing_GADM_',gadm_level,'_regions_with_FB_custom_locations_log.txt') # save the processing log


## Run the custom location generation

# create the folders to save the results into
for (folder in c(queries_folder, coverage_stats_folder,
                 output_folder, maps_folder)) {
  if (!dir.exists(folder)) {
    dir.create(folder)
  }
}


capture.output(
  for (i in 1:nrow(cntries_df)) {
  cntry_iso3 <- cntries_df$iso3[i]

  cat("### Processing country:",cntry_iso3,"\n")

  ## read in the GADM 2 shape file
  cat("__*__ Reading in GADM adm 2 shape files:\n")
  
  geo_adm2 <-getData('GADM', country=cntry_iso3, level=gadm_level)
  
  ## Check if locations need clean up
  report <- clgeo_CollectionReport(geo_adm2)
  if (sum(report$valid) != nrow(geo_adm2)) {
    cat("+ Detected geo error for",sum(!report$valid),"polygons\n")
    cat("+ Attempting to clean up issue with geos:\n")

    # clean up any issues with the geo
    geo_adm2 <- clgeo_Clean(geo_adm2)

    report.clean <- clgeo_CollectionReport(geo_adm2)
    cat(clgeo_SummaryReport(report.clean))
  }

  ## Cover with custom locations for FB targeting
  res_list <- generate_list_of_custom_locations_for_shape_files(reg_geo = geo_adm2,
                                                                idcol = paste0("GID_",gadm_level), zone = cntries_df$zone[i],
                                                                loc_area_cutoffs = c())
  
  
  ## Validate locations
  cat("__*__ Validating the custom locations covering:\n")
  ptm0 <- proc.time()
  invalid_list <- determine_invalid_custom_locations(res_list)
  ptm1 <- proc.time()
  cat("Time taken to validated queries:\n")
  cat(ptm1-ptm0)
  
  ## expand coverage for sparse locations
  cat("__*__ Attempting location expansion for locations with sparse data:\n")
  expanded_coverage <- expand_coverage_for_sparse_locations(geo_shape_file = geo_adm2, idcol = paste0('GID_',gadm_level),
                                                            geo_custom_list = res_list, invalid_locs = invalid_list,
                                                            zone = cntries_df$zone[i])
  
  ## 
  cat("__*__ Selecting custom locations covering for each polygon:\n")
  chosen_custom_locs_cover <- choose_custom_locations_to_use(geo_custom_list = expanded_coverage$geo_custom_list_expanded, 
                                                             invalid_locs = expanded_coverage$expanded_list_invalid_locs,
                                                             covers_order = c("interior_cover","exterior_cover"))
  
  
  ## map visualization
  cat("__*__ Generating info. files and visualizations:\n")
  mapviz <- show_custom_location_covers_on_map(regions_geos = geo_adm2, 
                                               geos_covers = chosen_custom_locs_cover$chosen_custom_covers, 
                                               invalid_locs = expanded_coverage$expanded_list_invalid_locs, 
                                               zone = cntries_df$zone[i])
  
  ## generate statistics report on the locations areas covered
  area_coverage_stats <- report_coverage_stats(geo_shape_file = geo_adm2, idcol = paste0('GID_',gadm_level),
                                               geo_custom_list = chosen_custom_locs_cover$chosen_custom_covers, 
                                               invalid_locs = expanded_coverage$expanded_list_invalid_locs,
                                               zone = cntries_df$zone[i])
  for(j in 1:nrow(area_coverage_stats)) {
    area_coverage_stats[j,'expanded'] <- chosen_custom_locs_cover$chosen_custom_covers[[area_coverage_stats$geo_id[j]]]$expanded
    area_coverage_stats[j,'radius'] <- chosen_custom_locs_cover$chosen_custom_covers[[area_coverage_stats$geo_id[j]]]$final_radius_used
  }
  area_coverage_stats$rownum <- 1:nrow(area_coverage_stats)
  area_coverage_stats <- merge(x = area_coverage_stats, by.x = 'geo_id', all.x = TRUE,
                               y = chosen_custom_locs_cover$fb_mau[,c('locid','fb_mau')], by.y = 'locid')
  area_coverage_stats <- area_coverage_stats[order(area_coverage_stats$rownum),]
  
  ## Create queries for pySocialWatcher
  cat("__*__ Saving results:\n")
  geo_queries <- 
    get_pysw_geo_queries_from_locations_list(geo_custom_list = chosen_custom_locs_cover$chosen_custom_covers,
                                             invalid_locs = expanded_coverage$expanded_list_invalid_locs)
  geo_queries[length(geo_queries)] <- gsub(",$","",geo_queries[length(geo_queries)])
  

  ## save the results
  write(geo_queries, paste(queries_folder,"/",cntry_iso3,paste0("_loc_queries_for_cover_by_custom_locations_GADM",gadm_level,"_regions.txt"),sep=""))
  
  write.csv(area_coverage_stats, 
            paste(coverage_stats_folder,"/",cntry_iso3,"_custom_locations_area_coverage_stats.csv",sep=""),
            row.names = FALSE)
  
  save(res_list, invalid_list, expanded_coverage, chosen_custom_locs_cover, mapviz,
       file = paste(output_folder,"/",cntry_iso3,"_custom_locations_coverage_data.RData",sep=""))
  
  # save map viz
  tmap_save(mapviz$map_viz,paste(maps_folder,"/",cntry_iso3,"_GADM",gadm_level,"_custom_locations_coverage_map.html",sep=""),
            selfcontained = FALSE)
  
  cat("__*__ Done processing for location:",cntries_df$country[i]," ---------------------------- \n\n\n\n")}
  , file = log_file, append = TRUE)
