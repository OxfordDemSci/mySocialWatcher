countries=("AD" "AE" "AF" "AG" "AI" "AL" "AM" "AN" "AO" "AQ" "AR" "AS" "AT" "AU" "AW" "AZ" "BA" "BB" "BD" "BE" "BF" "BG" "BH" "BI" "BJ" "BL" "BM" "BN" "BO" "BQ" "BR" "BS" "BT" "BW" "BY" "BZ" "CA" "CD" "CF" "CG" "CH" "CI" "CK" "CL" "CM" "CN" "CO" "CR" "CU" "CV" "CW" "CX" "CY" "CZ" "DE" "DJ" "DK" "DM" "DO" "DZ" "EC" "EE" "EG" "EH" "ER" "ES" "ET" "FI" "FJ" "FK" "FM" "FO" "FR" "GA" "GB" "GD" "GE" "GF" "GG" "GH" "GI" "GL" "GM" "GN" "GP" "GQ" "GR" "GS" "GT" "GU" "GW" "GY" "HK" "HN" "HR" "HT" "HU" "ID" "IE" "IL" "IM" "IN" "IO" "IQ" "IR" "IS" "IT" "JE" "JM" "JO" "JP" "KE" "KG" "KH" "KI" "KM" "KN" "KR" "KW" "KY" "KZ" "LA" "LB" "LC" "LI" "LK" "LR" "LS" "LT" "LU" "LV" "LY" "MA" "MC" "MD" "ME" "MF" "MG" "MH" "MK" "ML" "MM" "MN" "MO" "MP" "MQ" "MR" "MS" "MT" "MU" "MV" "MW" "MX" "MY" "MZ" "NA" "NC" "NE" "NF" "NG" "NI" "NL" "NO" "NP" "NR" "NU" "NZ" "OM" "PA" "PE" "PF" "PG" "PH" "PK" "PL" "PM" "PN" "PR" "PS" "PT" "PW" "PY" "QA" "RE" "RO" "RS" "RU" "RW" "SA" "SB" "SC" "SD" "SE" "SG" "SH" "SI" "SJ" "SK" "SL" "SM" "SN" "SO" "SR" "SS" "ST" "SV" "SX" "SY" "SZ" "TC" "TD" "TG" "TH" "TJ" "TK" "TL" "TM" "TN" "TO" "TR" "TT" "TV" "TW" "TZ" "UA" "UG" "UM" "US" "UY" "UZ" "VA" "VC" "VE" "VG" "VI" "VN" "VU" "WF" "WS" "XK" "YE" "YT" "ZA" "ZM" "ZW")

# users
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE ROLE writer LOGIN PASSWORD '${POSTGRES_WPASS}';
CREATE ROLE reader LOGIN PASSWORD '${POSTGRES_RPASS}';
"

# collections
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE collections (
	id serial PRIMARY KEY,
	created_on DATE NOT NULL DEFAULT CURRENT_DATE,
	name VARCHAR (25) NOT NULL,
	UNIQUE(name)
);
GRANT SELECT ON collections TO writer, reader;
GRANT INSERT ON collections TO writer;
GRANT USAGE,SELECT ON SEQUENCE collections_id_seq TO writer, reader;
"

# contributors
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE contributors (
	id serial PRIMARY KEY,
	created_on DATE NOT NULL DEFAULT CURRENT_DATE,
	name VARCHAR(50) NOT NULL,
	email VARCHAR(50) NOT NULL,
	collaborators INTEGER[] NOT NULL DEFAULT '{}',
	collections INTEGER[] NOT NULL DEFAULT '{}',
	UNIQUE(name)
);
GRANT SELECT ON contributors TO writer, reader;
GRANT USAGE,SELECT ON SEQUENCE contributors_id_seq TO writer, reader;

INSERT INTO contributors (id, name, email)
VALUES
(1,'Doug Leasure','douglas.leasure@demography.ox.ac.uk')
"

# tokens
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE tokens (
	id serial PRIMARY KEY,
	contributor_id INT NOT NULL
    REFERENCES contributors(id)
    ON DELETE SET NULL,
	created_on DATE NOT NULL DEFAULT CURRENT_DATE,
	write BOOLEAN NOT NULL DEFAULT FALSE,
	token VARCHAR(50) UNIQUE NOT NULL DEFAULT MD5(random()::text),
	UNIQUE(contributor_id, write)
);
GRANT SELECT ON tokens TO writer;
GRANT USAGE,SELECT ON SEQUENCE tokens_id_seq TO writer, reader;

INSERT INTO tokens (contributor_id, write) VALUES (1, True)
"

#---------- data ----------#

# facebook
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE facebook (
	collection_id INT REFERENCES collections(id) ON DELETE SET NULL,
	contributor_id INT REFERENCES contributors(id) ON DELETE SET NULL,
  contributed_on TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  collection_date DATE NOT NULL,
  country CHAR(2) NOT NULL,
  gender SMALLINT NOT NULL,
	age_min SMALLINT NOT NULL DEFAULT 0,
	age_max SMALLINT NOT NULL DEFAULT 999,
	dau INT NOT NULL,
	mau INT,
	mau_lower INT,
	mau_upper INT,
	timestamp BIGINT NOT NULL,
  geo_locations jsonb NOT NULL,
	all_fields jsonb DEFAULT '{}'::jsonb,
	targeting jsonb DEFAULT '{}'::jsonb,
	response jsonb DEFAULT '{}'::jsonb,
  UNIQUE(country, collection_date, geo_locations, gender, age_min, age_max, dau, targeting, response)
) PARTITION BY LIST (country);

CREATE INDEX contributor_fb_idx ON facebook(contributor_id);
CREATE INDEX collection_fb_idx ON facebook(collection_id);
CREATE INDEX date_fb_idx ON facebook(collection_date);
CREATE INDEX gender_fb_idx ON facebook(gender);
CREATE INDEX age_fb_idx ON facebook(age_min, age_max);

GRANT SELECT ON facebook TO reader;
GRANT SELECT,INSERT ON facebook TO writer;
"

# create facebook partitions by country
for idx in "${!countries[@]}"
do
  psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
  "CREATE TABLE facebook_${countries[idx]} PARTITION OF facebook FOR VALUES IN ('${countries[idx]}')"
done

# facebook (temporary storage of invalid data)
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE facebook_invalid (
	collection_id INT REFERENCES collections(id) ON DELETE SET NULL,
	contributor_id INT REFERENCES contributors(id) ON DELETE SET NULL,
  contributed_on TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  collection_date DATE NOT NULL,
  country CHAR(2) NOT NULL,
  gender SMALLINT NOT NULL,
	age_min SMALLINT NOT NULL DEFAULT 0,
	age_max SMALLINT NOT NULL DEFAULT 999,
	dau INT NOT NULL,
	mau INT,
	mau_lower INT,
	mau_upper INT,
	timestamp BIGINT NOT NULL,
  geo_locations jsonb NOT NULL,
	all_fields jsonb DEFAULT '{}'::jsonb,
	targeting jsonb DEFAULT '{}'::jsonb,
	response jsonb DEFAULT '{}'::jsonb,
  UNIQUE(country, collection_date, geo_locations, gender, age_min, age_max, dau, targeting, response)
);
GRANT SELECT ON facebook_invalid TO reader;
GRANT SELECT,INSERT ON facebook_invalid TO writer;
"

# instagram
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE instagram (
	collection_id INT REFERENCES collections(id) ON DELETE SET NULL,
	contributor_id INT REFERENCES contributors(id) ON DELETE SET NULL,
  contributed_on TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  collection_date DATE NOT NULL,
  country CHAR(2) NOT NULL,
  gender SMALLINT NOT NULL,
	age_min SMALLINT NOT NULL DEFAULT 0,
	age_max SMALLINT NOT NULL DEFAULT 999,
	dau INT NOT NULL,
	mau INT,
	mau_lower INT,
	mau_upper INT,
	timestamp BIGINT NOT NULL,
  geo_locations jsonb NOT NULL,
	all_fields jsonb DEFAULT '{}'::jsonb,
	targeting jsonb DEFAULT '{}'::jsonb,
	response jsonb DEFAULT '{}'::jsonb,
  UNIQUE(country, collection_date, geo_locations, gender, age_min, age_max, dau, targeting, response)
) PARTITION BY LIST (country);
CREATE INDEX contributor_ig_idx ON instagram(contributor_id);
CREATE INDEX collection_ig_idx ON instagram(collection_id);
CREATE INDEX date_ig_idx ON instagram(collection_date);
CREATE INDEX gender_ig_idx ON instagram(gender);
CREATE INDEX age_ig_idx ON instagram(age_min, age_max);

GRANT SELECT ON instagram TO reader;
GRANT SELECT,INSERT ON instagram TO writer;
"

# create instagram partitions by country
for idx in "${!countries[@]}"
do
  psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
  "CREATE TABLE instagram_${countries[idx]} PARTITION OF instagram FOR VALUES IN ('${countries[idx]}')"
done


# instagram (temporary storage of invalid data)
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE instagram_invalid (
	collection_id INT REFERENCES collections(id) ON DELETE SET NULL,
	contributor_id INT REFERENCES contributors(id) ON DELETE SET NULL,
  contributed_on TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  collection_date DATE NOT NULL,
  country CHAR(2) NOT NULL,
  gender SMALLINT NOT NULL,
	age_min SMALLINT NOT NULL DEFAULT 0,
	age_max SMALLINT NOT NULL DEFAULT 999,
	dau INT NOT NULL,
	mau INT,
	mau_lower INT,
	mau_upper INT,
	timestamp BIGINT NOT NULL,
  geo_locations jsonb NOT NULL,
	all_fields jsonb DEFAULT '{}'::jsonb,
	targeting jsonb DEFAULT '{}'::jsonb,
	response jsonb DEFAULT '{}'::jsonb,
  UNIQUE(country, collection_date, geo_locations, gender, age_min, age_max, dau, targeting, response)
);
GRANT SELECT ON instagram_invalid TO reader;
GRANT SELECT,INSERT ON instagram_invalid TO writer;
"

# view: facebook_clean
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
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
	(geo_locations -> 'values')[0] ->> 'key' as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	geo_locations ->> 'location_types' as location_types,
	all_fields -> 'languages' ->> 'name' as language_name,
	all_fields -> 'languages' ->> 'values' as language_key
from facebook
inner join collections on facebook.collection_id = collections.id;

grant select on facebook_clean to reader, writer;
"

# view: instagram_clean
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
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
	(geo_locations -> 'values')[0] ->> 'key' as geo_key,
	(geo_locations -> 'values')[0] ->> 'name' as geo_name,
	geo_locations ->> 'location_types' as location_types,
	all_fields -> 'languages' ->> 'name' as language_name,
	all_fields -> 'languages' ->> 'values' as language_key
from instagram
inner join collections on instagram.collection_id = collections.id;

grant select on instagram_clean to reader, writer;
"

unset countries