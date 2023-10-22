-- view: facebook_clean
drop view if exists facebook_clean;

create view facebook_clean as
select
	collections.name as collection_name,
	collection_id,
	collection_date, timestamp,
	dau, mau, mau_lower, mau_upper,
	gender,
	age_min, age_max,
	country,
	geo_locations ->> 'name' as geo_level,
	trim(both '"' from (geo_locations -> 'values')[0]::text) as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	geo_locations ->> 'location_types' as location_types,
	all_fields -> 'languages' ->> 'name' as language_name,
	all_fields -> 'languages' ->> 'values' as language_key
from
 	facebook
inner join
 	collections on facebook.collection_id = collections.id
where
 	geo_locations ->> 'name' = 'countries'

union all

select
	collections.name as collection_name,
	collection_id,
	collection_date, timestamp,
	dau, mau, mau_lower, mau_upper,
	gender,
	age_min, age_max,
	country,
	geo_locations ->> 'name' as geo_level,
	(geo_locations -> 'values')[0] ->> 'key'::text as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	geo_locations ->> 'location_types' as location_types,
	all_fields -> 'languages' ->> 'name' as language_name,
	all_fields -> 'languages' ->> 'values' as language_key
from
 	facebook
inner join
 	collections on facebook.collection_id = collections.id
where
 	geo_locations ->> 'name' != 'countries';

grant select on facebook_clean to reader, writer;


-- view: facebook with geometries
drop view if exists facebook_geo;

create view
	facebook_geo as
select
	facebook_clean.*,
	gadm.geometry
from
	facebook_clean
left join
	gadm on geo_key = gadm.meta_key;

grant select on facebook_geo to reader, writer;




-- view: instagram_clean
drop view if exists instagram_clean;

create view instagram_clean as
select
	collections.name as collection_name,
	collection_id,
	collection_date, timestamp,
	dau, mau, mau_lower, mau_upper,
	gender,
	age_min, age_max,
	country,
	geo_locations ->> 'name' as geo_level,
	trim(both '"' from (geo_locations -> 'values')[0]::text) as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	geo_locations ->> 'location_types' as location_types,
	all_fields -> 'languages' ->> 'name' as language_name,
	all_fields -> 'languages' ->> 'values' as language_key
from
 	instagram
left join
 	collections on instagram.collection_id = collections.id
where
 	geo_locations ->> 'name' = 'countries'

union all

select
	collections.name as collection_name,
	collection_id,
	collection_date, timestamp,
	dau, mau, mau_lower, mau_upper,
	gender,
	age_min, age_max,
	country,
	geo_locations ->> 'name' as geo_level,
	(geo_locations -> 'values')[0] ->> 'key'::text as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	geo_locations ->> 'location_types' as location_types,
	all_fields -> 'languages' ->> 'name' as language_name,
	all_fields -> 'languages' ->> 'values' as language_key
from
 	instagram
left join
 	collections on instagram.collection_id = collections.id
where
 	geo_locations ->> 'name' != 'countries';

grant select on instagram_clean to reader, writer;


-- view: instagram with geometries
drop view if exists instagram_geo;

create view
	instagram_geo as
select
	instagram_clean.*,
	gadm.geometry
from
	instagram_clean
left join
	gadm on geo_key = gadm.meta_key;

grant select on instagram_geo to reader, writer;

