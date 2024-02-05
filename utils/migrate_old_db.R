library(dplyr)
library(future.apply)

source('mySocialWatcher/utils/migrate_old_db.env')

con_new <- DBI::dbConnect(RPostgres::Postgres(),
                      dbname = database,
                      host = host,
                      port = port,
                      user = user,
                      password = password)



combination <- tbl(con_old, 'facebook') |> 
  group_by(country, gender) |> 
  summarise(n()) |> 
  collect()

test_new_df <- tbl(con, 'facebook') |> 
  head(n=5) |> 
  collect()


# write through sql 
plan(multisession, workers=5)

writing_log <- future_lapply(1:nrow(combination), function(combination_idx){
  con_old <- DBI::dbConnect(RPostgres::Postgres(),
                            dbname = database,
                            host = host_old,
                            port = port,
                            user = user_old,
                            password = password_old)
  con_writer <- DBI::dbConnect(RPostgres::Postgres(),
                               dbname = database,
                               host = host,
                               port = port,
                               user = user_writer,
                               password = password_writer)
  
  combination_row <- unlist(combination[combination_idx,])
  country_ <- unname(combination_row['country'])
  gender_ <- unname(combination_row['gender'])

  old_df <- tbl(con_old, 'facebook') |> 
    filter(country==country_&gender==gender_)|> 
    mutate(collection_date= as.Date(timestamp_iso),
           collection_id = 37,
           contributor_id = 7) |> 
    select(colnames(test_new_df), -contributed_on) |> 
    collect()
  
  rows_insert(tbl(con_writer, 'facebook_invalid'), old_df, conflict='ignore',
              by =c('country', 'collection_date', 'geo_locations', 'gender', 'age_min', 'age_max', 'dau', 'targeting', 'response'),
              in_place = T, copy=T)
  
  DBI::dbDisconnect(con_old)
  DBI::dbDisconnect(con_writer)
  
  return(combination_row)
  
})


# check writing process

test <- tbl(con_new, 'facebook_invalid')
test_table <- test |> 
  filter(collection_id ==37) |> 
  collect() 


DBI::dbDisconnect(con_new)

