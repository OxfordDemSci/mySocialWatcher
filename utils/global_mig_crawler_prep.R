

library(rio)
library(R.utils)

# making temp to store the unzipped csvs
dir.create("DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration/temp")

# function to convert the unzipped files into gz
csvconvert <- function(csvnames){
  convert(paste0("DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration//temp/tmp_finished_collections/", csvnames), 
          paste0("DemSci/projects/2023_WHO_Ukraine_Population/data/meta_collections/global_migration_qcri/global_migration_qcri/finished/", csvnames, ".gz")) 
}

# function to unzip the tars and transform the csv into gz
tartransform <- function(filename){
  
  # sometimes it cannot extract a list that's why I added a timeout of 3 min
  list <- withTimeout(untar(paste0("DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration/data/", filename), list = TRUE), timeout = 180)
  
  # unzip the archives in temp directory
  if (length(grep("dataframe_collected_finished", list)) > 0){
    untar(paste0("DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration/data/", filename), 
          exdir = "DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration/temp")
  } else {
    stop("erroneous tar archive")
  }
  rm(list)
  
  if (file.exists("DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration/temp/tmp_finished_collections/") == TRUE){
    # convert csv to gz
    csvnames <- list.files("DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration/temp/tmp_finished_collections")
    lapply(csvnames, csvconvert)
  } else {
    stop("file does not exist")
  }
  rm(csvnames)
  # empty the temp folder
  unlink("DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration/temp/*", recursive = TRUE)
}

# list of file names to feed into loop
filename <- list.files("DemSci/data/QCRI/scdev5.qcri.org/mfatehkia/collections/global_migration/data")

lapply(filename, tartransform)
# takes 1.5 min for one tar.gz archive


