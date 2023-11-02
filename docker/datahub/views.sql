-- view: facebook_clean --
drop view if exists facebook_clean cascade;

create view facebook_clean as
select
	contributor_id,
    collection_id,
	collections.name as collection_name,
	collection_date, timestamp,
	dau, mau, mau_lower, mau_upper,
	gender,
	age_min, age_max,
	country,
	geo_locations ->> 'name' as geo_level,
	trim(both '"' from (geo_locations -> 'values')[0]::text) as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	case
	when geo_locations ->> 'location_types' is null then '["home", "recent"]'
	else geo_locations ->> 'location_types' 
	as location_types,
	case
        when all_fields -> 'languages' ->> 'name' is null then 'all'
        else all_fields -> 'languages' ->> 'name'
        end as language_name,
	case
	    when all_fields -> 'languages' ->> 'values' is null then '[]'
	    else all_fields -> 'languages' ->> 'values'
	    end as language_key
from
 	facebook
inner join
 	collections on facebook.collection_id = collections.id
where
 	geo_locations ->> 'name' = 'countries'

union all

select
	contributor_id,
    collection_id,
	collections.name as collection_name,
	collection_date, timestamp,
	dau, mau, mau_lower, mau_upper,
	gender,
	age_min, age_max,
	country,
	geo_locations ->> 'name' as geo_level,
	(geo_locations -> 'values')[0] ->> 'key'::text as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	case
	when geo_locations ->> 'location_types' is null then '["home", "recent"]'
	else geo_locations ->> 'location_types' 
	as location_types,
	case
        when all_fields -> 'languages' ->> 'name' is null then 'all'
        else all_fields -> 'languages' ->> 'name'
        end as language_name,
	case
	    when all_fields -> 'languages' ->> 'values' is null then '[]'
	    else all_fields -> 'languages' ->> 'values'
	    end as language_key
from
 	facebook
inner join
 	collections on facebook.collection_id = collections.id
where
 	geo_locations ->> 'name' != 'countries';

grant select on facebook_clean to reader, writer;


-- view: facebook with geometries --
drop view if exists facebook_geo cascade;

create view
	facebook_geo as
select
	facebook_clean.*,
	gadm.geometry
from
	facebook_clean
left join
	gadm on geo_key = gadm.meta_key
where
    geo_level != 'cities'
union all
select
	facebook_clean.*,
	cities.geometry
from
	facebook_clean
left join
	cities on geo_key::int = cities.meta_key
where
    geo_level = 'cities';

grant select on facebook_geo to reader, writer;




-- view: instagram_clean --
drop view if exists instagram_clean cascade;

create view instagram_clean as
select
	contributor_id,
    collection_id,
	collections.name as collection_name,
	collection_date, timestamp,
	dau, mau, mau_lower, mau_upper,
	gender,
	age_min, age_max,
	country,
	geo_locations ->> 'name' as geo_level,
	trim(both '"' from (geo_locations -> 'values')[0]::text) as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	case
	when geo_locations ->> 'location_types' is null then '["home", "recent"]'
	else geo_locations ->> 'location_types' 
	as location_types,
	case
        when all_fields -> 'languages' ->> 'name' is null then 'all'
        else all_fields -> 'languages' ->> 'name'
        end as language_name,
	case
	    when all_fields -> 'languages' ->> 'values' is null then '[]'
	    else all_fields -> 'languages' ->> 'values'
	    end as language_key
from
 	instagram
left join
 	collections on instagram.collection_id = collections.id
where
 	geo_locations ->> 'name' = 'countries'

union all

select
	contributor_id,
    collection_id,
	collections.name as collection_name,
	collection_date, timestamp,
	dau, mau, mau_lower, mau_upper,
	gender,
	age_min, age_max,
	country,
	geo_locations ->> 'name' as geo_level,
	(geo_locations -> 'values')[0] ->> 'key'::text as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	case
	when geo_locations ->> 'location_types' is null then '["home", "recent"]'
	else geo_locations ->> 'location_types' 
	as location_types,
	case
        when all_fields -> 'languages' ->> 'name' is null then 'all'
        else all_fields -> 'languages' ->> 'name'
        end as language_name,
	case
	    when all_fields -> 'languages' ->> 'values' is null then '[]'
	    else all_fields -> 'languages' ->> 'values'
	    end as language_key
from
 	instagram
left join
 	collections on instagram.collection_id = collections.id
where
 	geo_locations ->> 'name' != 'countries';

grant select on instagram_clean to reader, writer;


-- view: instagram with geometries --
drop view if exists instagram_geo cascade;

create view
	instagram_geo as
select
	instagram_clean.*,
	gadm.geometry
from
	instagram_clean
left join
	gadm on geo_key = gadm.meta_key
where
    geo_level != 'cities'
union all
select
	instagram_clean.*,
	cities.geometry
from
	instagram_clean
left join
	cities on geo_key::int = cities.meta_key
where
    geo_level = 'cities';

grant select on instagram_geo to reader, writer;


-- data overview --
drop view if exists data_overview cascade;

create view data_overview as
select
    collection_date,
    'facebook' as platform,
    country,
    location_types,
    geo_level,
    language_name,
    count(distinct(gender)) as nb_gender,
    count(distinct(concat(age_min, age_max))) as nb_agegroup,
    case
        when count(distinct(geo_name)) =0 then 1
        else count(distinct(geo_name))
      	end as nb_location,
    count(distinct(geometry)) as nb_geometry
from
    facebook_geo
group by
    collection_date, country, location_types, language_name, geo_level

union

select
    collection_date,
    'instagram' as platform,
    country,
    location_types,
    geo_level,
    language_name,
    count(distinct(gender)) as nb_gender,
    count(distinct(concat(age_min, age_max))) as nb_agegroup,
    case
        when count(distinct(geo_name)) =0 then 1
        else count(distinct(geo_name))
      end as nb_location,
      count(distinct(geometry)) as nb_geometry
from
    instagram_geo
group by
    collection_date, country, location_types, language_name, geo_level
order by
    platform, collection_date, geo_level, location_types, language_name;

grant select on data_overview to reader, writer;


-- geometries --
drop view if exists geometries;

create view geometries as
select
    meta_key as geo_key,
    'countries' as geo_level,
    gid_0 as gid,
    name_0 as name,
    geometry
from
    gadm
where
    gadm_level = 0

union all

select
    meta_key::text as geo_key,
    'regions' as geo_level,
    gid_1 as gid,
    name_1 as name,
    geometry
from
    gadm
where
    gadm_level = 1

union all

select
    meta_key::text as geo_key,
    'cities' as geo_level,
    null as gid,
    name,
    geometry
from
    cities;

grant select on geometries to reader, writer;
