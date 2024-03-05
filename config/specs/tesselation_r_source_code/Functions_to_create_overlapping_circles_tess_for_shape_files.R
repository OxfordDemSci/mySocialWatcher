# Script with functions and modules for
# tesselating a shape file with custom circles
# for targeting


#require(rgdal)
#require(rgeos)
#require(maptools)
require(geosphere)
require(raster)
require(cleangeo)
require(sf)
require(jsonlite)
require(plyr)
require(dplyr)
library(httr)
library(jsonlite)
library(units)
require(fasterize)
library(dplyr)
library(tmap)


## ----
## Parameters
## ----
SHAPE_TESS_PARAMS <- list(
  token = NA,
  act = NA,
  version = "v8.0", 
  query_sleep_time = 0.2,
  sparse_query_size = 1000,
  num_retries_on_queries_that_are_not_estimate_ready = 5,
  wait_between_retries = 60,
  
  N_max_locs = 200, # maximum number of custome locations allowed
  min_radius = 1, # Minimum radius (km) 
  max_radius = 80, # Maximum radius (km)
  
  # The distance between the centres of any two adjacent circles in terms 
  # of multiples of the radius argument above
  # adjusts the proximity/overlap between the circles
  lat_radius_dist = 1.4, 
  long_radius_dist = 1.4,
  wgs84 = "+proj=longlat +datum=WGS84",
  
  # for expansion the parameters
  min_fb_mau = 1100,
  expand_area_max_ratio = 2
  )



## ----
## Utility functions
## ----

## 
# Sets the FB credentials in order to collect estimates
# from the marketing API
# ----- Inputs ---
# * token <- FB marketing API access token
# * act <- account number of the user
# * version <- marketing API version
# ----- Outputs ---
# sets the relevant parameters in the SHAPE_TESS_PARAMS list.
# No return value.
set_fb_credentials <- function(token, act, version = "v19.0",min_fb_mau) {
  SHAPE_TESS_PARAMS$token <<- token
  SHAPE_TESS_PARAMS$act <<- act
  SHAPE_TESS_PARAMS$version <<- version
  SHAPE_TESS_PARAMS$min_fb_mau
  SHAPE_TESS_PARAMS$Credentials <<- paste0('https://graph.facebook.com/',version,'/act_',act,'/delivery_estimate?access_token=',token,'&include_headers=false&method=get&optimization_goal=REACH&pretty=0&suppress_http_code=1')
  
  print(SHAPE_TESS_PARAMS$Credentials)
}

# query the Facebook marketing API for a given custom location.
# query for users aged 18+, living in the location.
# ----- Inputs ---
# * Credentials <- The FB credentials to be used. set this using the
#     set_fb_credentials function.
# * lat <- latitude coordinate of the location
# * long <- longitude coordinate of the location
# * radius <- radius around the point in kilometers
# ----- Outputs ---
# returns the value returned by the Facebook marketing API.
# Issues warning if the returned result is not estimate ready.
# 
get_fb_estimate_for_custom_loc <- function(Credentials, lat, long, radius) {
  query <- paste0(Credentials,'&targeting_spec={',
                  '"age_min":18,',
                  #'"age_max":',Age2,',
                  '"genders":[0],',
                  '"geo_locations":{"custom_locations":[{',
                  '"latitude":',lat,',',
                  '"longitude":',long,',', 
                  '"radius":', radius,',',
                  '"distance_unit": "kilometer"}],"location_types":["home"]},',
                  #'"facebook_positions":["feed","instant_article","instream_video","marketplace"],',
                  #'"device_platforms":["mobile","desktop"],',
                  '"publisher_platforms":["facebook"]}')#,',#'"messenger_positions":["messenger_home"]}')
  
  tries <- SHAPE_TESS_PARAMS$num_retries_on_queries_that_are_not_estimate_ready
  got_estimate_ready_result <- FALSE
  got_error <- FALSE
  while (tries > 0) {
    response <- GET(url, query = query)
    query_val<-content(response, "text",encoding = "UTF-8") %>%fromJSON()
    
    if (is.element("error",names(query_val))) { 
      got_error <- TRUE
      break 
    }
    if (is.element("data",names(query_val))) { 
      if (query_val$data$estimate_ready) {
        got_estimate_ready_result <- TRUE
        break
      }
    }
    
    Sys.sleep(SHAPE_TESS_PARAMS$wait_between_retries)
    tries <- tries - 1
  }
  
  if (!got_error & !got_estimate_ready_result) {
    warning("The FB query result is not estimate ready!")
  }
  
  return(query_val)
}

# Estimates from the Facebook marketing API for an OR of the provided 
# list of custom locations.
# ----- Inputs ---
# * Credentials <- The FB credentials to be used. set this using the
#     set_fb_credentials function.
# * locs_list <- a list containing the custom locations to do an OR of.
#     each entry is a list containing:
#       - lat <- latitude coordinate of the location
#       - long <- longitude coordinate of the location
#       - radius <- radius around the point in kilometers
# ----- Outputs ---
# returns the value returned by the Facebook marketing API.
# Issues warning if the returned result is not estimate ready.
# 
get_fb_estimate_for_list_of_custom_locs <- function(locs_list) {
  access_token <- SHAPE_TESS_PARAMS$token
  ad_set_id <- paste0("act_",SHAPE_TESS_PARAMS$act)
  # URL
  url <- paste0("https://graph.facebook.com/v19.0/", ad_set_id, "/delivery_estimate")
  
  # The targeting specification
  targeting <- list(
    age_min = 18,
    genders = list(0),
    geo_locations = list(
      custom_locations = vector("list", length(locs_list))
    ),
    publisher_platforms = list("facebook")
  )
  
  # Fill in the custom locations (as before)
  for (i in 1:length(locs_list)) {
    targeting$geo_locations$custom_locations[[i]] <- list(
      latitude = locs_list[[i]]$lat,
      longitude = locs_list[[i]]$long,
      radius = locs_list[[i]]$radius,
      distance_unit = "kilometer"
    )
  }
  
  
  # Convert the entire structure, including parameters and targeting, to JSON
  json_body <- toJSON(targeting, auto_unbox = TRUE)
  
  # Prepare the query parameters
  query <- list(
    targeting_spec = json_body,
    optimization_goal = "IMPRESSIONS",
    access_token = access_token
  )
  
  
  
  
  
  ## get FB estimate for the query
  tries <- SHAPE_TESS_PARAMS$num_retries_on_queries_that_are_not_estimate_ready
  got_estimate_ready_result <- FALSE
  got_error <- FALSE
  while (tries > 0) {
    response <- GET(url, query = query)
    query_val<-content(response, "text",encoding = "UTF-8") %>%fromJSON()
    
    if (is.element("error",names(query_val))) { 
      got_error <- TRUE
      break 
    }
    if (is.element("data",names(query_val))) { 
      if (query_val$data$estimate_ready) {
        got_estimate_ready_result <- TRUE
        break
      }
    }
    
    Sys.sleep(SHAPE_TESS_PARAMS$wait_between_retries)
    tries <- tries - 1
  }
  
  if (!got_error & !got_estimate_ready_result) {
    warning("The FB query result is not estimate ready!")
  }
  
  return(query_val)
}








# Estimates from the Facebook marketing API for the provided
# list of custom locations covering.
# ----- Inputs ---
# * geo_custom_list <- A list of custom locations coverings as output
#     by the generate_list_of_custom_locations_for_shape_files()
#     function.
# * invalid_locs <- A list of invalid locations in the 
#     geo_custom_list. This is the output of the
#     determine_invalid_custom_locations() function.
# ----- Outputs ---
# returns the value returned by the Facebook marketing API.
# Issues warning if the returned result is not estimate ready.
# 

get_fb_mau_estimates_for_custom_covers <- function(geo_custom_list, invalid_locs) {
  nlocs <- length(names(geo_custom_list))
  all_df <- NULL
  for (i in 1:nlocs) {
    cat("# Getting fb estimate for geo shape",i,"of",nlocs,rep(" ",10),"\r")
    locname <- names(geo_custom_list)[i]
    
    for (coverType in names(geo_custom_list[[i]]$custom_locations_list)) {
      valid_locs <- setdiff(names(geo_custom_list[[locname]]$custom_locations_list[[coverType]]),
                            names(invalid_locs[[locname]]))
      Ivalid <- as.numeric(gsub("part_([0-9]*)","\\1", valid_locs))
      
      locs_df <- data.frame(geo_id = locname,
                            coverType = coverType)
      
      if (length(Ivalid) != 0) {
        Sys.sleep(SHAPE_TESS_PARAMS$query_sleep_time)
        fbquery_val <- get_fb_estimate_for_list_of_custom_locs(locs_list = geo_custom_list[[locname]]$custom_locations_list[[coverType]][valid_locs])
        locs_df$fb_mau <- fbquery_val$data$estimate_mau_upper_bound 
        locs_df$estimate_ready <- fbquery_val$data$estimate_ready
      }
      all_df <- dplyr::bind_rows(all_df, locs_df)
    }
  }
  return(all_df)
}


# validates the provided list of custom locations.
# ----- Inputs ---
# * custom_geos_list <- a list containing the custom locations to do an OR of.
#     each entry is a list containing:
#       - lat <- latitude coordinate of the location
#       - long <- longitude coordinate of the location
#       - radius <- radius around the point in kilometers
# * verbose <- If true prints additional information.
# ----- Outputs ---
# returns a list of the locations in custom_geos_list
# that are not valid for targeting on the FB marketing API.
# 
validate_custom_locations_list <- function(custom_geos_list, verbose = FALSE) {
  
  if (verbose) {
    cat("# Validating geos list of length:",length(custom_geos_list),rep(" ",10),"\r")
  }
  
  Sys.sleep(SHAPE_TESS_PARAMS$query_sleep_time)
  
  fb_result <- get_fb_estimate_for_list_of_custom_locs(locs_list = custom_geos_list)
  #.GlobalEnv$fb_query_calls <- .GlobalEnv$fb_query_calls + 1
  
  invalid_locs <- list()
  if (is.element("error",names(fb_result))) {
    if (length(custom_geos_list) == 1) {
      loc_invalid <- list()
      loc_invalid[[names(custom_geos_list)]] <- fb_result
      
      return(loc_invalid)
    } else {
      mid <- floor(length(custom_geos_list)/2)
      invalid_locs <- c(validate_custom_locations_list(custom_geos_list[1:mid]),
                        validate_custom_locations_list(custom_geos_list[(mid+1):length(custom_geos_list)]))
    }
  }
  
  return(invalid_locs)
  
}


# validate the list of custom locations for each region.
# ----- Inputs ---
# * geo_custom_list <- A list of custom locations as returned by
#     generate_list_of_custom_locations_for_shape_files().
#
# ----- Outputs ---
# returns a list of the locations for each entry in geo_custom_list
# that are not valid for targeting on the FB marketing API.
# 
determine_invalid_custom_locations <- function(geo_custom_list) {
  invalid_locs_list <- list()
  nlocs <- length(geo_custom_list)
  for (i in 1:nlocs) {
    cat("# Determining invalid custom locations for geo shape",i,"of",nlocs,rep(" ",10),"\n")
    
    if (length(geo_custom_list[[i]]) == 0) { 
      invalid_locs_list[[names(geo_custom_list)[i]]] <- NULL
      next 
    }
    custom_geos_list <- geo_custom_list[[i]]$custom_locations_list$exterior_cover
    invalid_locs <- validate_custom_locations_list(custom_geos_list)
    
    invalid_locs_list[[names(geo_custom_list)[i]]] <- invalid_locs
  }
  return(invalid_locs_list)
}


# create pySocialWatcher geographic queries for lists of
# custom locations.
# ----- Inputs ---
# * geo_custom_list <- A list of custom locations as returned by
#     generate_list_of_custom_locations_for_shape_files().
# * invalid_locs <- A list of the locations in each entry of
#   geo_custom_list that are not valid for targeting. This
#   is the output of the determine_invalid_custom_locations()
#   function.
#   
# ----- Outputs ---
# returns a vector with the pysocialwatcher geo queries field
# for each location.
# 
get_pysw_geo_queries_from_locations_list <- function(geo_custom_list, invalid_locs) {
  geo_covers_df <- export_list_of_custom_locations(geo_custom_list, invalid_locs)
  
  all_geo_queries <- c()
  for (geoid in levels(as.factor(geo_covers_df$geo_id))) {
    Iid <- geo_covers_df$geo_id == geoid
    for (coverType in levels(as.factor(geo_covers_df$coverType[Iid]))) {
      Isub <- Iid & geo_covers_df$coverType == coverType
      expanded <- levels(as.factor(geo_covers_df$expanded[Isub]))
      # should we limite the number of significant digits in the lat/long ????????????????????????????????????????????
      custom_query <- paste('{"latitude":',geo_covers_df$lat[Isub],
                            ', "longitude":',geo_covers_df$long[Isub],
                            ',"radius":',geo_covers_df$radius[Isub],
                            ',"distance_unit": "kilometer"}',sep="", collapse = ", ")

      geo_query <- paste('{"name":"custom_locations", "values":[',custom_query,'],',
                         '"location_types": ["home"], "pySocialWatcherReference": "geo_id:',
                         geoid,'; coverType:',coverType,'; expanded:',expanded,'"}',sep="")
      all_geo_queries <- c(all_geo_queries, geo_query)
    }
  }
  return(all_geo_queries)
}

# export lists of custom locations dataframe 
# ----- Inputs ---
# * geo_custom_list <- A list of custom locations as returned by
#     generate_list_of_custom_locations_for_shape_files().
# * invalid_locs <- A list of the locations in each entry of
#   geo_custom_list that are not valid for targeting. This
#   is the output of the determine_invalid_custom_locations()
#   function.
#   
# ----- Outputs ---
# returns a dataframe with each row being the details of one
# custom location and the id of the shape file it covers.
# 
export_list_of_custom_locations <- function(geo_custom_list, invalid_locs) {
  nlocs <- length(geo_custom_list)
  all_df <- NULL
  for (i in 1:nlocs) {
    cat("# Exporting for geo shape",i,"of",nlocs,rep(" ",10),"\r")
    locname <- names(geo_custom_list)[i]
    
    for (coverType in names(geo_custom_list[[i]]$custom_locations_list)) {
      valid_locs <- setdiff(names(geo_custom_list[[locname]]$custom_locations_list[[coverType]]),
                            names(invalid_locs[[locname]]))
      
      if (length(valid_locs) != 0) {
        locs_df <- ldply(geo_custom_list[[locname]]$custom_locations_list[[coverType]][valid_locs], 
                         data.frame, stringsAsFactors = FALSE)
        locs_df$geo_id <- locname
        locs_df$coverType <- coverType
        if (is.element("expanded",names(geo_custom_list[[locname]]))) {
          locs_df$expanded <- geo_custom_list[[locname]]$expanded
        } else {
          locs_df$expanded <- FALSE
        }
        
        all_df <- rbind(all_df, locs_df)
      } 
    }
  }
  
  return(all_df)
}

# for a list of custom locations
# computer some area and intersection statistics
# with the shape file they approximate
# ----- Inputs ---
# * geo_shape_file <- An sp object of the shape file whose
#     shape is covered by the custom locations in geo_custom_locs.
# * geo_custom_locs <- A list of custom locations as returned by
#     generate_list_of_custom_locations_for_shape_files().
#   
# ----- Outputs ---
# returns a dataframe with area coverage statistics for the 
# shape file and the custom locations.
# 
get_area_coverage_stats <- function(geo_shape_file, geo_custom_locs) {
  n_custom_locs <- nrow(geo_custom_locs)
  geo_custom_locs_sf<-st_as_sf(geo_custom_locs)
  geo_shape_file<-st_as_sf(geo_shape_file)
  
  aggregated_geom <- geo_custom_locs_sf %>%
    summarize(geometry = st_union(geometry)) %>%
    st_cast("POLYGON")
  
  res_df <- data.frame(shape_area = st_area(geo_shape_file)/1000000)
  
  geo_intr <- st_intersection(geo_shape_file, aggregated_geom, byid = TRUE)
  intr_areas <- ifelse(!is.null(geo_intr), st_area(geo_intr)/1000000, 0)
  intr_areas <-set_units(intr_areas,m^2)
  
  if (nrow(aggregated_geom)>1){
    merged_geo_custom_locs_area<-sum(st_area(aggregated_geom))/1000000
  }else{
    merged_geo_custom_locs_area <- st_area(aggregated_geom)/1000000
  }
  
  res_df$desired_area_covered <- intr_areas
  res_df$desired_area_covered_perc <- 100*res_df$desired_area_covered/res_df$shape_area
  res_df$undesired_area_covered <- merged_geo_custom_locs_area - intr_areas
  res_df$undesired_area_covered_perc <- 100*res_df$undesired_area_covered/res_df$shape_area
  
  return(res_df)
}

# Report coverage statistics for custom locations 
# covers for the shape files
# ----- Inputs ---
# * geo_shape_file <- An sp object of the shape files whose
#     shapes are covered by the custom locations in geo_custom_locs.
# * idcol <- the column in the geo_shape_files data that has the location ids.
# * geo_custom_list <- A list of custom locations as returned by
#     generate_list_of_custom_locations_for_shape_files().
# * invalid_locs <- the list of invalid locations in geo_custom_list.
# * zone <- UTM zone for the location. 
# ----- Outputs ---
# returns a dataframe with area coverage statistics for the 
# shape files and their corresponding custom locations.
# 
report_coverage_stats <- function(geo_shape_file, idcol,
                                  geo_custom_list, invalid_locs, zone) {
  planar_proj <- paste("+proj=utm +zone=",zone," ellps=WGS84",sep="")
  nlocs <- nrow(geo_shape_file)
  all_df <- NULL
  for (i in 1:nlocs) {
    cat("# Computing statistics for geo shape",i,"of",nlocs,rep(" ",10),"\r")
    locname <- geo_shape_file@data[i,idcol]
    region_geo <- spTransform(geo_shape_file[i,], CRS(planar_proj))
    
    for (coverType in names(geo_custom_list[[i]]$custom_locations_list)) {
      all_locs <- names(geo_custom_list[[locname]]$custom_locations_list[[coverType]])
      Iall <-  as.numeric(gsub("part_([0-9]*)","\\1", all_locs))
      valid_locs <- setdiff(names(geo_custom_list[[locname]]$custom_locations_list[[coverType]]),
                            names(invalid_locs[[locname]]))
      
      Ivalid <- as.numeric(gsub("part_([0-9]*)","\\1", valid_locs))
      
      locs_df <- data.frame(geo_id = locname,
                            coverType = coverType,
                            N_locs = length(all_locs),
                            N_locs_valid = length(valid_locs))
      
      if (length(Iall) != 0) {
        geo_custom_locs <- spTransform(geo_custom_list[[locname]]$Tesselated_points_with_buffers[Iall,], CRS(planar_proj))
        areas_df <- get_area_coverage_stats(region_geo,geo_custom_locs)
        names(areas_df)[-1] <- paste("All_locs",names(areas_df)[-1],sep="_")
        locs_df <- cbind(locs_df, areas_df)
      }
      
      if (length(Ivalid) != 0) {
        # firstly test the length of the union geometry 
        geo_custom_locs <- spTransform(geo_custom_list[[locname]]$Tesselated_points_with_buffers[Ivalid,], CRS(planar_proj))

        areas_df <- get_area_coverage_stats(region_geo,geo_custom_locs)
        names(areas_df)[-1] <- paste("Valid_locs",names(areas_df)[-1],sep="_")
        locs_df <- cbind(locs_df, areas_df[,-1])
        
      }
      
     
      all_df <- dplyr::bind_rows(all_df, locs_df)
    }
  }
  
  return(all_df)
}

# Create a map visualizing a given location and the
# custom locations approximating it.
# ----- Inputs ---
# * region_geo <- An sp object of the shape files whose
#     shapes are covered by the custom locations in geo_custom_list.
# * geo_custom_list <- A list of custom locations as returned by
#     generate_list_of_custom_locations_for_shape_files().
# * invalid_locs <- the list of invalid locations in geo_custom_list.
# * rownum <- row number to be visualized. 
# ----- Outputs ---
# returns a tmap object which can be visualized.
# 
get_map_viz <- function(region_geo, geo_custom_list, invalid_locs, rownum) {
  covers <- c("exterior_cover",
              setdiff(names(geo_custom_list[[rownum]]$custom_locations_list),c("exterior_cover","interior_cover")),
              "interior_cover")
  geo_custom_list[[rownum]]$Tesselated_points_with_buffers$coverType <- NA
  for(cc in covers) {
    Icc <-  as.numeric(gsub("part_([0-9]*)","\\1", names(geo_custom_list[[rownum]]$custom_locations_list[[cc]])))
    geo_custom_list[[rownum]]$Tesselated_points_with_buffers$coverType[Icc] <- cc
  }
  geo_custom_list[[rownum]]$Tesselated_points_with_buffers$coverType <- factor(geo_custom_list[[rownum]]$Tesselated_points_with_buffers$coverType,
                                                                               levels = covers)
  locs_to_exclude <- as.numeric(gsub("part_([0-9]*)","\\1",names(invalid_locs[[rownum]])))
  locs_to_show <- !is.na(geo_custom_list[[rownum]]$Tesselated_points_with_buffers$coverType) &
    !is.element(geo_custom_list[[rownum]]$Tesselated_points_with_buffers$ptid,locs_to_exclude)
  
  
  map_obj <- tm_shape(region_geo[rownum,]) + tm_fill(col = "yellow", alpha = 0.6)
  map_obj <- map_obj + tm_shape(geo_custom_list[[rownum]]$Tesselated_points) + tm_dots(col = "black")
  map_obj <- map_obj + tm_shape(geo_custom_list[[rownum]]$Tesselated_points_with_buffers[locs_to_show,]) + tm_fill(col = "coverType", alpha = 0.4)
  map_obj <- map_obj + tm_scale_bar()
  
  return(map_obj)
}


# get intersection of two shapes
#  given two shape files, finds the area of intersection between the 
#  regions in the first and the second.
# ----- Inputs ---
# * geo1 <- first geo shape file object.
# * geo1_idcol <- the column in the geo1 data that has the location ids.
# * geo2 <- second geo shape file object.
# * geo2_idcol <- the column in the geo2 data that has the location ids.
# ----- Outputs ---
# returns a dataframe with areas of intersection between the regions 
# in the first and second geographic shape files.
# 

# original function
# detect_overlap_by_area_intersect <- function(geo1, geo1_idcol, geo2, geo2_idcol) {
#   
#   ## Get correspondence of polygon IDs to data IDs
#   geo1_ids <- list()
#   for (rowid in 1:nrow(geo1)) {
#     polyid <- paste("polyid",geo1@polygons[[rowid]]@ID,sep="_")
#     gid <- geo1@data[rowid,geo1_idcol]
#     geo1_ids[[polyid]] <- list(dataid = gid, rowid = rowid)
#   }
#   geo2_ids <- list()
#   for (rowid in 1:nrow(geo2)) {
#     polyid <- paste("polyid",geo2@polygons[[rowid]]@ID,sep="_")
#     gid <- geo2@data[rowid,geo2_idcol]
#     geo2_ids[[polyid]] <- list(dataid = gid, rowid = rowid)
#   }
#   
#   ## Calculate overlap and areas of intersection
#   geo_intr <- gIntersection(geo1, geo2, byid = TRUE)
#   intr_areas <- gArea(geo_intr,byid = TRUE)
#   
#   intr_areasdf <- data.frame(polyid = names(intr_areas), 
#                              polyid_g1 = gsub("([a-zA-Z0-9_]*) ([a-zA-Z0-9_]*)","\\1",names(intr_areas)),
#                              polyid_g2 = gsub("([a-zA-Z0-9_]*) ([a-zA-Z0-9_]*)","\\2",names(intr_areas)),
#                              intr_area = as.numeric(intr_areas)/1000000,
#                              geo1_data_id = NA, geo2_data_id = NA,
#                              geo1_area = NA, geo2_area = NA)
#   
#   for (i in 1:nrow(intr_areasdf)) {
#     g1_pid <- paste("polyid",intr_areasdf$polyid_g1[i],sep="_")
#     g1_rid <- geo1_ids[[g1_pid]]$rowid
#     g2_pid <- paste("polyid",intr_areasdf$polyid_g2[i],sep="_")
#     g2_rid <- geo2_ids[[g2_pid]]$rowid
#     
#     intr_areasdf$geo1_data_id[i] <- geo1_ids[[g1_pid]]$dataid
#     intr_areasdf$geo2_data_id[i] <- geo2_ids[[g2_pid]]$dataid
#     
#     intr_areasdf$geo1_area[i] <- gArea(geo1[g1_rid,])/1000000
#     intr_areasdf$geo2_area[i] <- gArea(geo2[g2_rid,])/1000000
#   }
#   
#   intr_areasdf$intr_area_as_perc_of_geo1_area <- 100*intr_areasdf$intr_area/intr_areasdf$geo1_area
#   intr_areasdf$intr_area_as_perc_of_geo2_area <- 100*intr_areasdf$intr_area/intr_areasdf$geo2_area
#   
#   return(intr_areasdf)
#   
# }

detect_overlap_by_area_intersect_sf <- function(geo1_sf, geo1_idcol, geo2_sf, geo2_idcol) {
  
  # Ensure input is of class sf
  if (!("sf" %in% class(geo1_sf))) {
    geo1_sf <- st_as_sf(geo1_sf)
  }
  if (!("sf" %in% class(geo2_sf))) {
    geo2_sf <- st_as_sf(geo2_sf)
  }
  
  # Calculate intersections
  geo_intr <- st_intersection(geo1_sf, geo2_sf)
  
  # Calculate areas of intersection
  geo_intr$intr_area <- st_area(geo_intr) / 1000000  # Convert to square kilometers (if necessary, depending on your CRS)
  
  # Create a dataframe for intersections
  intr_areasdf <- data.frame(
    geo1_data_id = geo_intr[[geo1_idcol]],
    geo2_data_id = geo_intr[[geo2_idcol]],
    intr_area = geo_intr$intr_area,
    geo1_area = NA,  # Placeholder, will fill next
    geo2_area = NA   # Placeholder, will fill next
  )
  
  # Calculate original areas
  geo1_sf$geo1_area <- st_area(geo1_sf) / 1000000
  geo2_sf$geo2_area <- st_area(geo2_sf) / 1000000
  
  # Loop to fill in original areas in the intersections dataframe
  for (i in 1:nrow(intr_areasdf)) {
    intr_areasdf$geo1_area[i] <- geo1_sf$geo1_area[geo1_sf[[geo1_idcol]] == intr_areasdf$geo1_data_id[i]]
    intr_areasdf$geo2_area[i] <- geo2_sf$geo2_area[geo2_sf[[geo2_idcol]] == intr_areasdf$geo2_data_id[i]]
  }
  
  # Calculate percentages
  intr_areasdf$intr_area_as_perc_of_geo1_area <- 100 * intr_areasdf$intr_area / intr_areasdf$geo1_area
  intr_areasdf$intr_area_as_perc_of_geo2_area <- 100 * intr_areasdf$intr_area / intr_areasdf$geo2_area
  
  return(intr_areasdf)
}


## ----
## Use spatial overlap to compare set of points to known
## invalid locations
## ----
# ----- Inputs ---
# * known_invalids_custom_geos <- A SpatialPolygonsDataFrame object containing the custom geolocations
#     that are already known to be invalid for targeting on FB.
# * locs_geos_to_validate <- A SpatialPolygonsDataFrame object containing custom geolocations whose
#     validity is to be determined.
# * zone <- UTM zone for the goegprahic region in geo_shape_file.
#     This is used to convert the shape to planar projection for
#     some types of geographic analysis. UTM zones can be looked up
#     here: http://www.dmap.co.uk/utmworld.htm
#
# ----- Outputs ---
# returns the invalid locations in locs_geos_to_validate.
# 
determine_invalid_custom_locs_from_known_invalids <- function(known_invalids_custom_geos, locs_geos_to_validate, zone) {
  planar_proj <- paste("+proj=utm +zone=",zone," ellps=WGS84",sep="")
  known_invalids_custom_geos_plan <- spTransform(known_invalids_custom_geos, CRS(planar_proj))
  locs_geos_to_validate_plan <- spTransform(locs_geos_to_validate, CRS(planar_proj))
  
  invalid_geos_merged <- unionSpatialPolygons(known_invalids_custom_geos,rep(1,nrow(known_invalids_custom_geos)))
  invalid_geos_merged_plan <- unionSpatialPolygons(known_invalids_custom_geos_plan,rep(1,nrow(known_invalids_custom_geos_plan)))
  invalid_geos_merged_plan <- SpatialPolygonsDataFrame(invalid_geos_merged_plan, data.frame(id = 1))
  
  # determine intersections of the locations of interest with the known invalid locations
  geo_intr <- gIntersection(invalid_geos_merged_plan, locs_geos_to_validate_plan, byid = TRUE)
  if (is.null(geo_intr)) { # no intersection with previously known invalid locations
    return(NULL)
  }
  
  geo_intr <- detect_overlap_by_area_intersect(geo1 = invalid_geos_merged_plan, geo1_idcol = "id",
                                               geo2 = locs_geos_to_validate_plan, geo2_idcol = "ptid")
  Iinvalid <- geo_intr$intr_area_as_perc_of_geo2_area >= 99.9999
  if (sum(Iinvalid) > 0) {
    invalid_locs <- paste("part",geo_intr$geo2_data_id[Iinvalid],sep="_")
  } else {
    invalid_locs <- NULL
  }
  
  return(invalid_locs)
}


## ----
## For a given geograhic region with sparse number of FB MAU users, 
## attempt to expand the custom locations covering it gradually 
## by including its periphery locations.
## ----
# ----- Inputs ---
# * reg_geo <- the geographic region for which a custom locations 
#     tesselation is desired.
# * idcol <- the name of the column in geo_shape_file containing the 
#     unique id for each region
# * zone <- UTM zone for the goegprahic region in geo_shape_file.
#     This is used to convert the shape to planar projection for
#     some types of geographic analysis. UTM zones can be looked up
#     here: http://www.dmap.co.uk/utmworld.htm
# * prev_custom_list <- a list of custom locations tesselating
#     reg_geo.
# * prev_invalid_locs <- a list of the invalid custom locations 
#     in the prev_custom_list.
# ----- Outputs ---
# Returns a list containing the updated list of custom locations
# for each iteration
# 


expand_and_create_custom_covers_for_shape_file <- function(reg_geo, idcol, zone,
                                                           prev_custom_list, prev_invalid_locs, verbose = FALSE) {
  
  planar_proj <- paste("+proj=utm +zone=",zone," ellps=WGS84",sep="")
  reg_geo_sf <- st_as_sf(reg_geo)###
  reg_geo_plan <- st_transform(reg_geo_sf, crs = planar_proj)
  reg_area <- sum(st_area(reg_geo_plan)) / 1000000
  
  ## expand the region shape with a buffer around it
  reg_geo_buff <- st_buffer(reg_geo_plan, dist = 1000 * prev_custom_list$final_radius_used)
  reg_geo_buff <- st_transform(reg_geo_buff, crs = st_crs(4326)) 
  
  #
  reg_buf_area <- sum(st_area(reg_geo_buff)) / 1000000 
  
  expansion_iters <- list()
  iter <- 1
  while (TRUE) {
    if ((reg_buf_area/reg_area) > set_units(SHAPE_TESS_PARAMS$expand_area_max_ratio,1)) {
      # buffered region is too big
      break
    }
    if (verbose) {
      cat("Attempting to create custom locations covering expanded geo, iteration:",iter," \r")
    }
    expansion_iters[[iter]] <- list()
    expansion_iters[[iter]][["region_with_buffer"]] <- reg_geo_buff
    
    
    # create a new covering of the shape
    res_list <- generate_list_of_custom_locations_for_shape_files(reg_geo = as(reg_geo_buff,"Spatial"), idcol = idcol, zone = zone)
    
    # determine the invalid locations
    IprevInvalid <- as.numeric(gsub("part_([0-9]*)","\\1",names(prev_invalid_locs)))
    if (length(IprevInvalid) == 0) {
      locs_known_to_be_invalid <- c()
    } else {
      locs_known_to_be_invalid <- determine_invalid_custom_locs_from_known_invalids(
        known_invalids_custom_geos = prev_custom_list$Tesselated_points_with_buffers[IprevInvalid,],
        locs_geos_to_validate = res_list[[1]]$Tesselated_points_with_buffers,
        zone = zone)
    }
    remaining_locs_to_validate <- setdiff(names(res_list[[1]]$custom_locations_list$exterior_cover), locs_known_to_be_invalid)
    
    invalid_list <- validate_custom_locations_list(res_list[[1]]$custom_locations_list$exterior_cover[remaining_locs_to_validate])
    for (invloc in locs_known_to_be_invalid) {
      invalid_list[[invloc]] <- "known from previous run"
    }
    
    # get fb mau estimates for the covering
    valid_locs <- setdiff(names(res_list[[1]]$custom_locations_list$exterior_cover), names(invalid_list))
    
    if (length(valid_locs) == 0) {
      fbmau <- NA
    } else {
      Sys.sleep(SHAPE_TESS_PARAMS$query_sleep_time)
      fbmau <- get_fb_estimate_for_list_of_custom_locs(locs_list = res_list[[1]]$custom_locations_list$exterior_cover[valid_locs])
    }
    
    # record the results
    expansion_iters[[iter]][["updated_list_of_custom_locations"]] <- res_list
    expansion_iters[[iter]][["updated_list_of_invalid_locations"]] <- invalid_list
    expansion_iters[[iter]][["fb_mau"]] <- fbmau
    
    # check whether to continue or stop here
    if (!is.na(fbmau)) {
      if (fbmau$data$estimate_mau_upper_bound >= SHAPE_TESS_PARAMS$min_fb_mau) {
        break
      }
    }
    
    # prepare for the next iteration
    iter <- iter + 1
    reg_geo_buff <- st_buffer(st_transform(reg_geo_buff, crs = planar_proj), dist = 1000 * res_list[[1]]$final_radius_used)
    reg_geo_buff <- st_transform(reg_geo_buff, crs = st_crs(4326))  # Back to WGS84
    reg_buf_area <- sum(st_area(reg_geo_buff)) / 1000000 
    
    prev_custom_list <- res_list[[1]]
    prev_invalid_locs <- invalid_list
  }
  return(expansion_iters)
}


## ----
## expand the custom locations covering for geographic 
## regions where FB users are sparse
## ----
# ----- Inputs ---
# * geo_shape_file <- An sp SpatialPolygonsDataFrame object containing 
#     the polygons for the regions that are to be approximated 
#     with custom locations
# * idcol <- the name of the column in geo_shape_file containing the 
#     unique id for each region
# * geo_custom_list <- a list of custom locations covering each region
#     in geo_shape_file. This is the output of the 
#     generate_list_of_custom_locations_for_shape_files() function.
# * invalid_locs <- a list containing the custom locations that are
#     not valid for targeting on FB. This is the output of the 
#     determine_invalid_custom_locations() function.
# * zone <- UTM zone for the goegprahic region in geo_shape_file.
#     This is used to convert the shape to planar projection for
#     some types of geographic analysis. UTM zones can be looked up
#     here: http://www.dmap.co.uk/utmworld.htm
#
# ----- Outputs ---
# A list with the following data:
# * FB_maus: A dataframe with each row being one location. This 
#     reports the FB MAU for each location before and after 
#     attempts to expand the location.
# * geo_custom_list_expanded: A list containing the custom locations
#     covering for each polygon in geo_shape_file. This will be the
#     same as the one in the geo_custom_list if the location already
#     had a non-sparse number of users. Otherwise, it will be a new
#     covering for the expanded location.
# * expanded_list_invalid_locs: A list of the invalid custom locations
#     for the locations in geo_custom_list_expanded
# 

expand_coverage_for_sparse_locations <- function(geo_shape_file, idcol,
                                                 geo_custom_list, invalid_locs, zone) {
  
  nlocs <- nrow(geo_shape_file)
  
  geo_list_ext <- geo_custom_list
  for (loc in names(geo_list_ext)) {
    geo_list_ext[[loc]]$custom_locations_list <- geo_list_ext[[loc]]$custom_locations_list["exterior_cover"]
  }
  
  ## 
  fb_maus <- NULL
  geo_list_expanded <- list()
  expanded_list_invalid_locs <- list()
  
  for (i in 1:nlocs) {
    cat("# Processing geo shape",i,"of",nlocs,rep(" ",10),"\r")
    locname <- geo_shape_file@data[i,idcol]
    region_geo <- geo_shape_file[i,]
    
    ## first get FB mau estimates for all locations
    Sys.sleep(SHAPE_TESS_PARAMS$query_sleep_time)
    fm <- get_fb_mau_estimates_for_custom_covers(geo_custom_list = geo_list_ext[locname],
                                                 invalid_locs = invalid_locs[locname])
    fm$expanded <- FALSE
    fm$fb_mau_after_expansion <- NA
    fb_maus <- dplyr::bind_rows(fb_maus, fm)
    
    if (!is.na(fm$fb_mau) & fm$fb_mau >= SHAPE_TESS_PARAMS$min_fb_mau) {
      geo_list_expanded[[locname]] <- geo_custom_list[[locname]]
      geo_list_expanded[[locname]]$expanded <- FALSE
      geo_list_expanded[[locname]]$fb_mau <- fm$fb_mau
      
      expanded_list_invalid_locs[[locname]] <- invalid_locs[[locname]]
      next
    }
    
    ## try to expand the location geography gradually to reduce sparsity
    expand_attempts <- expand_and_create_custom_covers_for_shape_file(reg_geo = region_geo,idcol = idcol, zone = zone,
                                                                      prev_custom_list = geo_list_ext[[locname]],
                                                                      prev_invalid_locs = invalid_locs[[locname]])
    last_attm <- length(expand_attempts)
    
    if (last_attm == 0) { # could not expand the location coverage
      geo_list_expanded[[locname]] <- geo_custom_list[[locname]]
      geo_list_expanded[[locname]]$expanded <- FALSE
      geo_list_expanded[[locname]]$fb_mau <- fm$fb_mau
      
      expanded_list_invalid_locs[[locname]] <- invalid_locs[[locname]]
      next
    }
    
    geo_list_expanded[[locname]] <- expand_attempts[[last_attm]]$updated_list_of_custom_locations[[locname]]
    #geo_list_expanded[[locname]]$custom_locations_list <- geo_list_expanded[[locname]]$custom_locations_list["exterior_cover"]
    geo_list_expanded[[locname]]$expanded <- TRUE
    geo_list_expanded[[locname]]$results_of_expand_iterations <- expand_attempts
    if (!is.na( expand_attempts[[last_attm]]$fb_mau)) {
      geo_list_expanded[[locname]]$fb_mau <- expand_attempts[[last_attm]]$fb_mau$data$estimate_mau_upper_bound
    } else {
      geo_list_expanded[[locname]]$fb_mau <- NA
    }
    
    
    expanded_list_invalid_locs[[locname]] <- expand_attempts[[last_attm]]$updated_list_of_invalid_locations
    
    fb_maus$expanded[i] <- geo_list_expanded[[locname]]$expanded
    fb_maus$fb_mau_after_expansion[i] <- geo_list_expanded[[locname]]$fb_mau
    
  }
  return(list(FB_maus = fb_maus,
              geo_custom_list_expanded = geo_list_expanded,
              expanded_list_invalid_locs = expanded_list_invalid_locs))
}





# Provide the UTM projection zone number for the location
# See map here: http://www.dmap.co.uk/utmworld.htm

# For a given shape file, create a list of custom locations whose 
# union approximates each polygon in the shape file
# ----- Inputs ---
# * reg_geo <- An sp SpatialPolygonsDataFrame object containing 
#     the polygons for the regions that are to be approximated 
#     with custom locations
# * idcol <- the name of the column in reg_geo containing the 
#     unique id for each region
# * geo_custom_list <- a list of custom locations covering each region
#     in geo_shape_file. This is the output of the 
#     generate_list_of_custom_locations_for_shape_files() function.
# * zone <- UTM zone for the goegprahic region in geo_shape_file.
#     This is used to convert the shape to planar projection for
#     some types of geographic analysis. UTM zones can be looked up
#     here: http://www.dmap.co.uk/utmworld.htm
# * loc_area_cutoffs <- by default a list of custom locations 
#     completely enclosing the polygons in reg_geo (the area of intersection
#     between the polygon and the custom locations is non-zero) is returned as well
#     as a list of custom locations that are completely enclosed by the 
#     polygons in reg_geo (100% of the custom location area is within
#     the given polygon). If lists of custom locations with different
#     percentage area of intersection is desired specify this here. For example
#     if a value of 50 is specified a list is returned of the custom locations
#     where at least 50% of the area of the custom location is within the 
#     region polygon being approximated.
# ----- Outputs ---
# A list where each entry corresponds to one region from reg_geo and contains
# information on the custom locations that approximate that region: 
# * xxx: xxxx
#     xxxxxxxx
# 

generate_list_of_custom_locations_for_shape_files <-
  function(reg_geo, idcol, zone, loc_area_cutoffs = c()) {
    res_list <- list()
    planar_proj <- paste("+proj=utm +zone=",zone," ellps=WGS84",sep="")
    
    cat("# Begin creating custom locations for polygons in shape file.\n")
    cat("# Shape file has",nrow(reg_geo),"polygons.\n")
    
    for (i in 1:nrow(reg_geo)) {
      cat("# Processing row num:",i,"polygon id:",reg_geo@data[i,idcol],rep(" ",15),"\n")
      
      # prepare the geo file
      loc_geo <- reg_geo[i,]
      loc_id <- reg_geo@data[i,idcol]
      res_list[[loc_id]] <- list()
      
      # Skip if any errors in geo shape file
      report <- clgeo_CollectionReport(loc_geo)
      if (!report$valid) {
        cat("+ Skipping polygon due to geo error; see error details below:\n")
        print(clgeo_SummaryReport(report))
        next
      }
      
      # Infers the limits of the square enclosing the geographic location
      lat_min <- extent(loc_geo)@ymin
      lat_max <- extent(loc_geo)@ymax
      long_min <- extent(loc_geo)@xmin
      long_max <- extent(loc_geo)@xmax
      
      # use the distance function to get
      # the average latitude/longitude to distance conversion for
      # the square enclosing the location
      lat_to_dist <- mean(distGeo(c(long_min,lat_min),c(long_min,lat_max)),
                          distGeo(c(long_max,lat_min),c(long_max,lat_max)))/1000
      lat_to_dist <- lat_to_dist/(lat_max - lat_min)
      long_to_dist <- mean(distGeo(c(long_min,lat_min),c(long_max,lat_min)),
                           distGeo(c(long_min,lat_max),c(long_max,lat_max)))/1000
      long_to_dist <- long_to_dist/(long_max - long_min)
      
      # the latitude/longitude distance of the square enclosing the locations
      lat_dist <- lat_to_dist*(lat_max - lat_min)
      long_dist <- long_to_dist*(long_max - long_min)
      
      # appropriate start radius radius
      sf_object <- st_as_sf(spTransform(loc_geo,CRS(planar_proj)))### 
      start_radius <- ceiling(sqrt(((as.numeric(st_area(sf_object))/1000000)/SHAPE_TESS_PARAMS$N_max_locs)/pi))### 
      start_radius <- min(start_radius,SHAPE_TESS_PARAMS$max_radius)
      start_radius <- max(start_radius,SHAPE_TESS_PARAMS$min_radius)
      
      radius <- start_radius
      iters <- 1
      failed_with_max_radius <- FALSE
      while(TRUE) {
        cat("-- Attempting to create tesselation with circular buffer of radius:",radius,"\r")
        
        
        ## create a circular tiling of the locations
        # Computes number of circular tiles needed in each dimension
        n_lat <- round(lat_dist/(SHAPE_TESS_PARAMS$lat_radius_dist*radius)) # number of circles along the latitude
        n_long <- round(long_dist/(SHAPE_TESS_PARAMS$long_radius_dist*radius)) # number of circles along the longitude
        
        if (n_lat == 1) {
          lats_r1 <- (lat_min + lat_max)/2
        } else {
          lats_r1 <- seq(from = lat_min, to = lat_max, length.out = n_lat+2) # latitude coordinates of the grid of circles
        }
        if (n_long == 1) {
          longs_r1 <- (long_min + long_max)/2
        } else {
          longs_r1 <- seq(from = long_min - (radius/long_to_dist), 
                          to = long_max + (radius/long_to_dist), length.out = n_long+2) # longitude coordinates of the grid of circle
        }
                
        pts_df <- expand.grid(lat = lats_r1, long = longs_r1) # create grid
        pts_df$ptid <- 1:nrow(pts_df)
        
        if (length(lats_r1) >= 2) {
          even_rows <- seq(from = 2, to = length(lats_r1), by = 2) # shifts circles from every other row
          is_even_row <- is.element(pts_df$lat,lats_r1[even_rows])
          pts_df[is_even_row,"long"] <- pts_df[is_even_row,"long"] + (radius/long_to_dist)
        }
        
        # create a spatial points object
        coord_mat <- as.matrix(pts_df[,c("long","lat")])
        pts_spt_df <- SpatialPointsDataFrame(coords = coord_mat, 
                                             data = pts_df,
                                             proj4string = CRS(SHAPE_TESS_PARAMS$wgs84))
        
        # Convert the points to a planar projection in order to create 
        # custom circular locations
        pts_buff_all <- st_as_sf(spTransform(pts_spt_df, CRS(planar_proj))) ### 
        buff_radius <- rep(1000*radius, nrow(pts_buff_all))
        # pts_buff_all <- gBuffer(pts_buff_all, width = buff_radius, byid = TRUE, capStyle = "ROUND")### depreciated
        
        pts_buff_all <-st_buffer(pts_buff_all, dist = buff_radius, endcapStyle = "round")
        pts_buff_all<- as(pts_buff_all, "Spatial") ### 
        pts_buff_all <- spTransform(pts_buff_all, CRS(SHAPE_TESS_PARAMS$wgs84))
        
        # determine intersection with the geo shape
        geo_intr <- detect_overlap_by_area_intersect_sf(spTransform(loc_geo,CRS(planar_proj)), idcol, 
                                                     spTransform(pts_buff_all,CRS(planar_proj)),"ptid")
        
        Isubs <- list(exterior_cover = geo_intr$intr_area_as_perc_of_geo2_area >set_units(0, m^2), ###
                      interior_cover = geo_intr$intr_area_as_perc_of_geo2_area >= set_units(99.99,m^2))###
        for (cutoff in loc_area_cutoffs) {
          Isubs[[paste("cover_cutoff",cutoff,sep="_")]] <- 
            geo_intr$intr_area_as_perc_of_geo2_area >= cutoff
        }
        
        cover_geos_list <- list()
        for (cgl in names(Isubs)) {
          cover_geos_list[[cgl]] <- geo_intr$geo2_data_id[Isubs[[cgl]]]
        }
        
        Icover <- is.element(pts_buff_all$ptid, cover_geos_list$exterior_cover)
        
        if ((sum(Icover) > SHAPE_TESS_PARAMS$N_max_locs)) {
          if (radius == SHAPE_TESS_PARAMS$max_radius) {
            cat("** Shape is too big to be covered with custom locations meeting the required constrains:\n",
                "** max. radius:",SHAPE_TESS_PARAMS, "allowed max. number of locations:",SHAPE_TESS_PARAMS$N_max_locs,
                " -- Skipping this polygon!\n")
            failed_with_max_radius <- TRUE
            break
          }
          
          radius <- ifelse(radius <= 10, radius + 1,
                           ifelse(radius <= 20, radius+2, radius+3))
          radius <- min(radius,SHAPE_TESS_PARAMS$max_radius)
          
          iters <- iters + 1
        } else { break }
      }
      
      if (failed_with_max_radius) { next }
      
      res_list[[loc_id]][["start_radius"]] <- start_radius
      res_list[[loc_id]][["final_radius_used"]] <- radius
      
      ## get list of circles for the shape
      N_tess_circles <- nrow(pts_buff_all@data)
      
      # the Outside tesselation
      res_list[[loc_id]][["custom_locations_list"]] <- list()
      for (cgl in names(Isubs)) {
        res_list[[loc_id]][["custom_locations_list"]][[cgl]] <- list()
      }
      
      for (j in 1:N_tess_circles) {
        if (!Icover[j]) { next } # skip unnecessary locations
        cat("Compiling list of circles:",j,"of",N_tess_circles,rep(" ",15),"\r")
        
        loci <- list(lat = pts_buff_all@data$lat[j], 
                     long = pts_buff_all@data$long[j], 
                     radius = radius,
                     ptid = pts_buff_all@data$ptid[j])
        
        for (cgl in names(Isubs)) {
          cover_geos_list[[cgl]] #<- geo_intr$geo2_data_id[Isubs[[cgl]]]
          if (is.element(pts_buff_all$ptid[j], cover_geos_list[[cgl]])) {
            res_list[[loc_id]][["custom_locations_list"]][[cgl]][[paste("part",j,sep="_")]] <- loci
          }
        }
      }
      
      # Save some summary results for this
      res_list[[loc_id]]$N_locs_exterior_cover <- length(res_list[[loc_id]][["custom_locations_list"]]$exterior_cover)
      res_list[[loc_id]]$N_locs_interior_cover <- length(res_list[[loc_id]][["custom_locations_list"]]$interior_cover)
      
      # save results
      res_list[[loc_id]][["Tesselated_points"]] <- pts_spt_df
      res_list[[loc_id]][["Tesselated_points_with_buffers"]] <- 
        merge(x = pts_buff_all, by.x = "ptid",
              y = geo_intr[,c("geo2_data_id","intr_area","intr_area_as_perc_of_geo2_area")], by.y = "geo2_data_id")
    }
    
    return(res_list)
  }

# union approximates each polygon in the shape file
# ----- Inputs ---
# * reg_geo <- An sp SpatialPolygonsDataFrame object containing 
#     the polygons for the regions that are to be approximated 
#     with custom locations
# * idcol <- the name of the column in reg_geo containing the 
#     unique id for each region
# * geo_custom_list <- a list of custom locations covering each region
#     in geo_shape_file. This is the output of the 
#     generate_list_of_custom_locations_for_shape_files() function.
# * zone <- UTM zone for the goegprahic region in geo_shape_file.
#     This is used to convert the shape to planar projection for
#     some types of geographic analysis. UTM zones can be looked up
#     here: http://www.dmap.co.uk/utmworld.htm
# * loc_area_cutoffs <- by default a list of custom locations 
#     completely enclosing the polygons in reg_geo (the area of intersection
#     between the polygon and the custom locations is non-zero) is returned as well
#     as a list of custom locations that are completely enclosed by the 
#     polygons in reg_geo (100% of the custom location area is within
#     the given polygon). If lists of custom locations with different
#     percentage area of intersection is desired specify this here. For example
#     if a value of 50 is specified a list is returned of the custom locations
#     where at least 50% of the area of the custom location is within the 
#     region polygon being approximated.
# ----- Outputs ---
# A list where each entry corresponds to one region from reg_geo and contains
# information on the custom locations that approximate that region.
# 
get_custom_locations_list_for_different_cutoffs <- function(reg_geo, idcol, zone, geo_custom_list, loc_area_cutoffs = c()) {
  
  planar_proj <- paste("+proj=utm +zone=",zone," ellps=WGS84",sep="")
  
  for (locname in names(geo_custom_list)) { 
    Iloc <- reg_geo@data[,idcol] == locname
    pts_buff_all <- geo_custom_list[[locname]]$Tesselated_points_with_buffers
    radius <- geo_custom_list[[locname]]$final_radius_used
    
    geo_intr <- detect_overlap_by_area_intersect(spTransform(reg_geo[Iloc,],CRS(planar_proj)), idcol, 
                                                 spTransform(pts_buff_all,CRS(planar_proj)),"ptid")
    
    Isubs <- list(exterior_cover = geo_intr$intr_area_as_perc_of_geo2_area > 0,
                  interior_cover = geo_intr$intr_area_as_perc_of_geo2_area >= 99.99)
    for (cutoff in loc_area_cutoffs) {
      Isubs[[paste("cover_cutoff",cutoff,sep="_")]] <- 
        geo_intr$intr_area_as_perc_of_geo2_area >= cutoff
    }
    
    cover_geos_list <- list()
    for (cgl in names(Isubs)) {
      cover_geos_list[[cgl]] <- geo_intr$geo2_data_id[Isubs[[cgl]]]
    }
    
    Icover <- is.element(pts_buff_all$ptid, cover_geos_list$exterior_cover)
      
    ## get list of circles for the shape
    N_tess_circles <- nrow(pts_buff_all@data)
    
    # the Outside tesselation
    for (cgl in names(Isubs)) {
      geo_custom_list[[locname]]$custom_locations_list[[cgl]] <- list()
    }
    
    for (j in 1:N_tess_circles) {
      if (!Icover[j]) { next } # skip unnecessary locations
      cat("Compiling list of circles:",j,"of",N_tess_circles,rep(" ",15),"\r")
      
      loci <- list(lat = pts_buff_all@data$lat[j], 
                   long = pts_buff_all@data$long[j], 
                   radius = radius,
                   ptid = pts_buff_all@data$ptid[j])
      
      for (cgl in names(Isubs)) {
        if (is.element(pts_buff_all$ptid[j], cover_geos_list[[cgl]])) {
          geo_custom_list[[locname]]$custom_locations_list[[cgl]][[paste("part",j,sep="_")]] <- loci
        }
      }
    }
  }
  return(geo_custom_list)
}



# For a given list of custom locations covering various shape files
# chooses the level of covers to be used to approximate that location.
# ----- Inputs ---
# * geo_custom_list <- a list of custom locations covering each region
#     in geo_shape_file. This is the output of the 
#     generate_list_of_custom_locations_for_shape_files() function.
# * invalid_locs <- a list of the invalid locations in geo_custom_list
# * covers_order <- indicates the level of approximations of the
#     location with custom locations to be used. Indicate this in 
#     order from smallest to largest. By default the interior cover 
#     is returned (if the value of FB users is not sparse); otherwise
#     the next largest cover is attempted successively until 
#     a the union of custom locations is non-sparse or no larger
#     covering exists that is non-sparse.
# ----- Outputs ---
# A list with the following information:
# * chosen_custom_covers: each entry corresponds to one region and contains
#     information on the custom locations that approximate that region. 
# * fb_mau: a dataframe of the FB monthly active users for
#     the custom locations covering each region.
choose_custom_locations_to_use <- function(geo_custom_list, 
                                           invalid_locs, covers_order = c("interior_cover","exterior_cover")) {
  geos_covers <- geo_custom_list
  fb_mau_df <- NULL
  ngeos <- length(geo_custom_list)
  for (ni in 1:ngeos) {
    locname <- names(geo_custom_list)[ni]
    cat("Processing for location:",locname,";",ni,"of",ngeos,"   \r")
    
    for (j in 1:length(covers_order)) {
      coverType <- covers_order[j]
      valid_locs <- setdiff(names(geo_custom_list[[locname]]$custom_locations_list[[coverType]]),
                            names(invalid_locs[[locname]]))
      if (length(valid_locs) > 0) {
        Sys.sleep(SHAPE_TESS_PARAMS$query_sleep_time)
        fbmau <- get_fb_estimate_for_list_of_custom_locs(locs_list = geo_custom_list[[locname]]$custom_locations_list[[coverType]][valid_locs])
      } else {
        fbmau <- list(data = data.frame(estimate_mau_upper_bound = 0))
      }
      
      if (fbmau$data$estimate_mau_upper_bound > SHAPE_TESS_PARAMS$sparse_query_size) {
        geos_covers[[locname]]$custom_locations_list <- geos_covers[[locname]]$custom_locations_list[coverType]
        fb_mau_df <- rbind(fb_mau_df, data.frame(locid = locname, coverType = coverType, fb_mau = fbmau$data$estimate_mau_upper_bound, nlocs = length(valid_locs)))
        break
      } else if (j == length(covers_order)) {
        geos_covers[[locname]]$custom_locations_list <- geos_covers[[locname]]$custom_locations_list[coverType]
        fb_mau_df <- rbind(fb_mau_df, data.frame(locid = locname, coverType = coverType, fb_mau = fbmau$data$estimate_mau_upper_bound, nlocs = length(valid_locs)))
      }
    }
  }
  
  return(list(chosen_custom_covers = geos_covers,
              fb_mau = fb_mau_df))
}



# Extracts the approximate correspondence from lat/long degrees 
# to distance (in km) for a given location.
# ----- Inputs ---
# * shape_geo <- shape file object whose extent is used to return the degree
#     to distance conversion.
# ----- Outputs ---
# A list with the following information:
# * lat_to_dist: approximate correspondence between each degree of
#     latitude and distance.
# * long_to_dist: approximate correspondence between each degree of
#     longitude and distance.

get_lat_long_degree_to_dist_from_object_extent <- function(shape_geo) {
  # get the lat/long of the extent
  lat_min <- extent(shape_geo)@ymin
  lat_max <- extent(shape_geo)@ymax
  long_min <- extent(shape_geo)@xmin
  long_max <- extent(shape_geo)@xmax

  # use the distance function to get
  # the average latitude/longitude to distance conversion for
  # the square enclosing the location
  lat_to_dist <- mean(distGeo(c(long_min,lat_min),c(long_min,lat_max)),
                      distGeo(c(long_max,lat_min),c(long_max,lat_max)))/1000
  lat_to_dist <- lat_to_dist/(lat_max - lat_min)
  long_to_dist <- mean(distGeo(c(long_min,lat_min),c(long_max,lat_min)),
                       distGeo(c(long_min,lat_max),c(long_max,lat_max)))/1000
  long_to_dist <- long_to_dist/(long_max - long_min)
  
  return(list(lat_to_dist = lat_to_dist,
              long_to_dist = long_to_dist))
}


# creates a Visualization of the regions and the custom locations covering the
# regions. 
# ----- Inputs ---
# * regions_geos <- shape file of the regions.
# * geos_covers <- the list of custom locations covering the regions.
# * invalid_locs <- the locations in geos_covers that are not valid.
# * zone <- the UTM zone for the location.
# * covers_to_show <- a vector indicating the covering of custom locations to
#     display for each locations. If not specified the first available list of
#     custom locations in geos_covers is used for each location.
# ----- Outputs ---
# A list with the following information:
# * custom_locs_geo: An sp object with polygons representing the areas that are
#     covered by the custom locations.
# * raster_map_coverage: a raster map showing how many times each individual area
#     of the map is included in different custom locations for the different regions.
# * map_viz: A map visualization.

show_custom_location_covers_on_map <- function(regions_geos, geos_covers, invalid_locs, zone, covers_to_show = NA) {
  planar_proj <- paste("+proj=utm +zone=",zone," ellps=WGS84",sep="")
  
  # Aggregate the individual custom locations covers to polygons
  custom_polys <- NULL # Initialize an empty sfc to store polygons
  
  ngeos <- length(geos_covers)
  for (j in 1:ngeos) {
    locname <- names(geos_covers)[j]
    cat("* Processing location:",locname,";",j,"of",ngeos,"\r")
    
    coverType <- ifelse(!is.na(covers_to_show[j]), covers_to_show[j], 1)
    valid_locs <- setdiff(names(geos_covers[[locname]]$custom_locations_list[[coverType]]),
                          names(invalid_locs[[locname]]))
    Ivalid <- as.numeric(gsub("part_([0-9]*)","\\1",valid_locs))
    
    all_locs <- names(geos_covers[[locname]]$custom_locations_list[[coverType]])
    Iall_locs <-as.numeric(gsub("part_([0-9]*)","\\1",all_locs))
    if (length(Ivalid) == 0) { next }
    # loc_geos <- spTransform(geos_covers[[locname]]$Tesselated_points_with_buffers[Ivalid,], CRS(planar_proj))
    # loc_geos <-(loc_geos)
    
    
    loc_geos_sf <- st_transform(st_as_sf(geos_covers[[locname]]$Tesselated_points_with_buffers[Ivalid,]), crs = planar_proj)
    aggregated_geom <- loc_geos_sf %>%
      summarize(geometry = st_union(geometry)) %>%
      st_cast("POLYGON")
    
    loc_geos <- as(aggregated_geom,'Spatial')
    
    if (length(loc_geos)>1){
      ids = unlist(lapply(1:length(loc_geos), function(i) paste(locname, i, sep = "")))
      cover =  unlist(replicate(length(loc_geos),names(geos_covers[[locname]]$custom_locations_list[coverType]),simplify = FALSE))
      
    }
    else{
      ids = locname
      cover = names(geos_covers[[locname]]$custom_locations_list[coverType])
    }
    

      
    loc_geos <- SpatialPolygonsDataFrame(loc_geos, data.frame(id = ids, cover = cover))
    loc_geos <- spTransform(loc_geos, SHAPE_TESS_PARAMS$wgs84)
    # loc_geos <- st_as_sf(loc_geos)
    
    
    
    
    if (is.null(custom_polys) || length(custom_polys) == 0) {
      custom_polys <- loc_geos
    } else {
     
      custom_polys <- rbind(custom_polys, loc_geos)
    }
    
  }
  
  

  
  # create a raster map indicating how often a given location is covered
  lat_long_to_dist <- get_lat_long_degree_to_dist_from_object_extent(custom_polys)
  raster_res <- min(1/lat_long_to_dist$lat_to_dist,
                    1/lat_long_to_dist$long_to_dist)
  raster_temp = raster(extent(custom_polys), resolution = raster_res,
                       crs = st_crs(custom_polys)$proj4string)
  raster_map_coverage <- fasterize(st_as_sf(custom_polys), raster_temp, fun = "sum")
  
  # create a map object
  map_viz <- tm_shape(regions_geos, name = "Regions") + 
    tm_fill(col = "grey",alpha = 0.2) + 
    tm_borders(col = "red", lwd = 2) + 
    tm_shape(custom_polys, name = "custom locations covering") + 
    tm_fill(col = "MAP_COLORS", alpha = 0.9) + 
    
    tm_shape(raster_map_coverage, name = "number of locations covering the area") + 
    tm_raster(style = "cat") + tm_scale_bar()
  
  
  
  return(list(custom_locs_geo = custom_polys, 
              raster_map_coverage = raster_map_coverage,
              map_viz = map_viz))
}

