# ---- users ----#
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE ROLE api_reader LOGIN PASSWORD '${POSTGRES_RPASS}';
CREATE ROLE api_writer LOGIN PASSWORD '${POSTGRES_WPASS}';
"

# ---- contributors ---- #
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE contributors (
	id serial PRIMARY KEY,
	created_on DATE NOT NULL DEFAULT CURRENT_DATE,

	firstname VARCHAR (25) NOT NULL,
	lastname VARCHAR (25) NOT NULL,
	email VARCHAR(50) NOT NULL
);
GRANT SELECT ON contributors TO api_reader, api_writer;

INSERT INTO contributors (firstname, lastname, email)
VALUES ('Hoban', 'Washburne', 'hoban.washburne@serenity.io');
"

# ---- tokens ----#
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE tokens (
	id serial PRIMARY KEY,
	created_on DATE NOT NULL DEFAULT CURRENT_DATE,
	contributor_id INT NOT NULL,
	read BOOLEAN NOT NULL DEFAULT TRUE,
	write BOOLEAN NOT NULL DEFAULT FALSE,
	token VARCHAR(50) UNIQUE NOT NULL DEFAULT MD5(random()::text),
	FOREIGN KEY(contributor_id) REFERENCES contributors(id)
);
GRANT SELECT ON tokens TO api_reader, api_writer;

INSERT INTO tokens (contributor_id, write)
VALUES (1, TRUE);
"

# ---- geometries ---- #
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE geo (
	id serial PRIMARY KEY,

	contributed_on DATE NOT NULL DEFAULT CURRENT_DATE,
    contributor_id INT NOT NULL,
	FOREIGN KEY(contributor_id)
		REFERENCES contributors(id)
		ON DELETE SET NULL,

	timestamp_iso TIMESTAMPTZ NOT NULL,

	geo_name VARCHAR(25),
	geo_value VARCHAR(25),
	geom GEOMETRY
);
CREATE INDEX id_index ON geo(id);

GRANT SELECT ON geo TO api_reader, api_writer;
GRANT INSERT ON geo TO api_writer;
GRANT USAGE,SELECT ON SEQUENCE geo_id_seq TO api_reader, api_writer;
"

#---- facebook ----#
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE facebook (

	id serial PRIMARY KEY,

	geo_id INT,
	FOREIGN KEY(geo_id)
		REFERENCES geo(id)
		ON DELETE SET NULL,

	contributor_id INT,
	FOREIGN KEY(contributor_id)
		REFERENCES contributors(id)
		ON DELETE SET NULL,

	contributed_on TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),

    country CHAR(2) NOT NULL,
    geo_locations jsonb NOT NULL,

    timestamp_iso TIMESTAMPTZ(0) NOT NULL,
	timestamp INT NOT NULL,

    gender SMALLINT NOT NULL,
	age_min SMALLINT NOT NULL DEFAULT 0,
	age_max SMALLINT NOT NULL DEFAULT 999,

	dau INT,
	mau INT,
	mau_lower INT,
	mau_upper INT,

	all_fields jsonb DEFAULT '{}'::jsonb,
	targeting jsonb DEFAULT '{}'::jsonb,
	response jsonb DEFAULT '{}'::jsonb,

	UNIQUE (country, geo_locations, timestamp_iso, gender, age_min, age_max, targeting, response)
);
CREATE INDEX geo_id_fb_index ON facebook(geo_id);
CREATE INDEX country_fb_index ON facebook(country);

GRANT SELECT ON facebook TO api_reader, api_writer;
GRANT INSERT ON facebook TO api_writer;
GRANT USAGE,SELECT ON SEQUENCE facebook_id_seq TO api_reader, api_writer;
"

# ---- facebook (temporary storage of invalid data) ---- #
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE facebook_invalid (

	id serial PRIMARY KEY,

	geo_id INT,
	FOREIGN KEY(geo_id)
		REFERENCES geo(id)
		ON DELETE SET NULL,

	contributor_id INT,
	FOREIGN KEY(contributor_id)
		REFERENCES contributors(id)
		ON DELETE SET NULL,

	contributed_on TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),

    country CHAR(2) NOT NULL,
    geo_locations jsonb NOT NULL,

    timestamp_iso TIMESTAMPTZ(0) NOT NULL,
	timestamp INT NOT NULL,

    gender SMALLINT NOT NULL,
	age_min SMALLINT NOT NULL DEFAULT 0,
	age_max SMALLINT NOT NULL DEFAULT 999,

	dau INT,
	mau INT,
	mau_lower INT,
	mau_upper INT,

	all_fields jsonb DEFAULT '{}'::jsonb,
	targeting jsonb DEFAULT '{}'::jsonb,
	response jsonb DEFAULT '{}'::jsonb,

	UNIQUE (country, geo_locations, timestamp_iso, gender, age_min, age_max, targeting, response)
);

CREATE INDEX geo_id_fbi_index ON facebook_invalid(geo_id);
CREATE INDEX country_fbi_index ON facebook_invalid(country);

GRANT SELECT ON facebook_invalid TO api_reader, api_writer;
GRANT INSERT ON facebook_invalid TO api_writer;
GRANT USAGE,SELECT ON SEQUENCE facebook_invalid_id_seq TO api_reader, api_writer;
"

#--- instagram ----#
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE instagram (

	id serial PRIMARY KEY,

	geo_id INT,
	FOREIGN KEY(geo_id)
		REFERENCES geo(id)
		ON DELETE SET NULL,

	contributor_id INT,
	FOREIGN KEY(contributor_id)
		REFERENCES contributors(id)
		ON DELETE SET NULL,

	contributed_on TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),

    country CHAR(2) NOT NULL,
    geo_locations jsonb NOT NULL,

    timestamp_iso TIMESTAMPTZ(0) NOT NULL,
	timestamp INT NOT NULL,

    gender SMALLINT NOT NULL,
	age_min SMALLINT NOT NULL DEFAULT 0,
	age_max SMALLINT NOT NULL DEFAULT 999,

	dau INT,
	mau INT,
	mau_lower INT,
	mau_upper INT,

	all_fields jsonb DEFAULT '{}'::jsonb,
	targeting jsonb DEFAULT '{}'::jsonb,
	response jsonb DEFAULT '{}'::jsonb,

	UNIQUE (country, geo_locations, timestamp_iso, gender, age_min, age_max, targeting, response)
);

CREATE INDEX geo_id_ig_index ON instagram(geo_id);
CREATE INDEX country_ig_index ON instagram(country);

GRANT SELECT ON instagram TO api_reader, api_writer;
GRANT INSERT ON instagram TO api_writer;
GRANT USAGE,SELECT ON SEQUENCE instagram_id_seq TO api_reader, api_writer;
"

# ---- instagram (temporary storage of invalid data) ---- #
psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
"
CREATE TABLE instagram_invalid (

	id serial PRIMARY KEY,

	geo_id INT,
	FOREIGN KEY(geo_id)
		REFERENCES geo(id)
		ON DELETE SET NULL,

	contributor_id INT,
	FOREIGN KEY(contributor_id)
		REFERENCES contributors(id)
		ON DELETE SET NULL,

	contributed_on TIMESTAMPTZ(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),

    country CHAR(2) NOT NULL,
    geo_locations jsonb NOT NULL,

    timestamp_iso TIMESTAMPTZ(0) NOT NULL,
	timestamp INT NOT NULL,

    gender SMALLINT NOT NULL,
	age_min SMALLINT NOT NULL DEFAULT 0,
	age_max SMALLINT NOT NULL DEFAULT 999,

	dau INT,
	mau INT,
	mau_lower INT,
	mau_upper INT,

	all_fields jsonb DEFAULT '{}'::jsonb,
	targeting jsonb DEFAULT '{}'::jsonb,
	response jsonb DEFAULT '{}'::jsonb,

	UNIQUE (country, geo_locations, timestamp_iso, gender, age_min, age_max, targeting, response)
);

CREATE INDEX geo_id_ig2_index ON instagram_invalid(geo_id);
CREATE INDEX country_ig2_index ON instagram_invalid(country);

GRANT SELECT ON instagram_invalid TO api_reader, api_writer;
GRANT INSERT ON instagram_invalid TO api_writer;
GRANT USAGE,SELECT ON SEQUENCE instagram_invalid_id_seq TO api_reader, api_writer;
"
