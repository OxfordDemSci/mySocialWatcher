-- unique constraint on facebook using hashed jsons
create unique index unique_facebook_idx
    on facebook (country, collection_date, gender, age_min, age_max, dau,
    md5(geo_locations::text),
	md5(targeting::text),
	md5(response::text));

alter table facebook drop constraint facebook_country_collection_date_geo_locations_gender_age_m_key;

-- unique constraint on facebook_invalid using hashed jsons
create unique index unique_facebook_invalid_idx
    on facebook_invalid (country, collection_date, gender, age_min, age_max, dau,
    md5(geo_locations::text),
	md5(targeting::text),
	md5(response::text));

alter table facebook_invalid drop constraint facebook_invalid_country_collection_date_geo_locations_gend_key;


-- unique constraint on instagram using hashed jsons
create unique index unique_instagram_idx
    on instagram (country, collection_date, gender, age_min, age_max, dau,
    md5(geo_locations::text),
	md5(targeting::text),
	md5(response::text));

alter table instagram drop constraint instagram_country_collection_date_geo_locations_gender_age__key;


-- unique constraint on instagram_invalid using hashed jsons
create unique index unique_instagram_invalid_idx
    on instagram_invalid (country, collection_date, gender, age_min, age_max, dau,
    md5(geo_locations::text),
	md5(targeting::text),
	md5(response::text));

alter table instagram_invalid drop constraint instagram_invalid_country_collection_date_geo_locations_gen_key;


-- unique constraint on vkontakte using hashed jsons
create unique index unique_vkontakte_idx
    on vkontakte (country, collection_date, gender, age_min, age_max, dau,
    md5(geo_locations::text));

alter table vkontakte drop constraint vkontakte_country_collection_date_geo_locations_gender_age__key;


-- unique constraint on vkontakte_invalid using hashed jsons
create unique index unique_vkontakte_invalid_idx
    on vkontakte_invalid (country, collection_date, gender, age_min, age_max, dau,
    md5(geo_locations::text));

alter table vkontakte_invalid drop constraint vkontakte_invalid_country_collection_date_geo_locations_gen_key;
