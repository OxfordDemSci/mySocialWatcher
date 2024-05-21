library(rio)
library(R.utils)
library(future.apply)

drive_path <- '/run/user/1002/gvfs/smb-share:server=ndph.ox.ac.uk,share=k/DemSci/' 

collection <- 'global_migration'

old_path <- file.path(drive_path,'data/QCRI/scdev5.qcri.org/mfatehkia/collections', collection, '/')

new_path <- file.path(drive_path,'projects/2023_WHO_Ukraine_Population/data/meta_collections/', 
                      paste0(collection, '_qcri'), paste0(collection, '_qcri'), 'finished/')



# making temp to store the unzipped csvs
dir.create(file.path(old_path, 'temp'))

# function to convert the unzipped files into gz
csvconvert <- function(csvname, dir_name=temp_dir_name){
  convert(file.path(old_path,'temp', dir_name, "tmp_finished_collections", csvname), 
          paste0(new_path, csvname, ".gz"),
          in_opts = list(fill=T)) # to deal with unfinished lines in csv when using fread for import. probably due to blank lines
}

# function to unzip the tars and transform the csv into gz
tartransform <- function(filename){
  # create in temp directory a temp dir with the filename
  # it will be deleted only if the entire process is successful
  temp_dir_name <- gsub('.tar.gz', '',filename)
  
  if(!file.exists(paste0(new_path, '/log/', temp_dir_name, '.txt'))){
    dir.create(file.path(old_path, 'temp', temp_dir_name))
    
    tryCatch(
      {
        n_files_tar <- length(untar(paste0(old_path, filename),list = T))
        
        # unzip the archives in temp directory
        suppressWarnings(untar(paste0(old_path, filename),
                               exdir = file.path(old_path,'temp', temp_dir_name)))

        # convert csvs one by one
        csvnames <- list.files(file.path(old_path,'temp', temp_dir_name, "tmp_finished_collections"))
        if(length(csvnames)==n_files_tar){
          convert_to_gz <- lapply(csvnames, function(x) csvconvert(x, temp_dir_name))
          
          # empty the temp folder only if all csv have been written to new directory
          if(all(csvnames %in% gsub('.gz', '',list.files(paste0(new_path))))==T){
            unlink(file.path(old_path,'temp', temp_dir_name), recursive = TRUE)
            fileConn<-file(paste0(new_path, '/log/', temp_dir_name, '.txt'))
            writeLines('success', fileConn)
            close(fileConn)
          }
          
        }
      },
      error = function(cond){
        message(paste("filename failed:", filename))
        message("Here's the original error message:")
        message(conditionMessage(cond))
      }
    )
  }
}

# list of file names to feed into loop
filename_list <- list.files(old_path, pattern = '.tar.gz')

plan(multisession(workers=4))

t1 <- Sys.time()
future_lapply(filename_list, tartransform)
t2 <- Sys.time()
print(t2 - t1)

# 

