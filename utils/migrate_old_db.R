library(dplyr)
library(future.apply)

source('utils/migrate_old_db.env')

con_new <- DBI::dbConnect(RPostgres::Postgres(),
                          dbname = database,
                          host = host,
                          port = port,
                          user = user,
                          password = password)

con_old <- DBI::dbConnect(RPostgres::Postgres(),
                          dbname = database,
                          host = host_old,
                          port = port,
                          user = user_old,
                          password = password_old)

combination <- tbl(con_old, 'facebook') |> 
  group_by(country, gender) |> 
  summarise(n=as.numeric(n())) |> 
  ungroup() |> 
  collect()


contributors_old <- tbl(con_old, 'contributors') |> 
  rename(contributor_id_old = id) |> 
  collect()


contributors_new <- tbl(con_new, 'contributors') |> 
  rename(contributor_id = id) |> 
  collect()

contributors <- contributors_old |> 
  distinct(contributor_id_old, firstname, lastname, email) |> 
  mutate(name=paste(firstname, lastname)) |> 
  left_join(contributors_new |> 
              select(contributor_id, name)) |> 
  filter(!is.na(contributor_id))


DBI::dbDisconnect(con_old)

test_new_df <- tbl(con_new, 'facebook') |> 
  head(n=5) |> 
  collect()


# write through sql 
plan(multisession, workers=6)

writing_log <- future_lapply(1:nrow(combination), function(combination_idx){
  #combination_idx =1
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
           collection_id = 37) |> 
    select(colnames(test_new_df), -contributed_on) |> 
    rename(contributor_id_old = contributor_id)  |> 
    collect() |> 
    left_join(
      contributors |> 
        select(contributor_id, contributor_id_old),
      by='contributor_id_old'
    ) |> 
    select(-contributor_id_old)
  
  rows_insert(tbl(con_writer, 'facebook'), old_df , conflict='ignore',
              by =c('country', 'collection_date', 'geo_locations', 'gender', 'age_min', 'age_max', 'dau', 'targeting', 'response'),
              in_place = T, copy=T)
  
  DBI::dbDisconnect(con_old)
  DBI::dbDisconnect(con_writer)
  
  print(c(combination_idx, combination_row))
  
  return(c(combination_idx, combination_row))
  
})

plan(sequential)

# check writing process

test <- tbl(con_new, 'facebook')
test_table <- test |> 
  filter(collection_id ==37) |> 
  summarise(n=n()) |> 
  collect() 
test_table #4819098

DBI::dbDisconnect(con_new)



