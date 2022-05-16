CREATE TABLE trip (
	id SERIAL PRIMARY KEY,
    region VARCHAR(255) NOT NULL,
--    origin_coord geography(POINT(4326),
--    destination_coord geography(POINT(4326),
    origin_coord_h3 int,
    destination_coord_h3 int,
    hour_day smallint,
    datetime timestamp with time zone,
    datasource VARCHAR(255) NOT NULL
);

SELECT AddGeometryColumn ('public', 'trip', 'origin_coord', 4326, 'POINT', 2); -- 4326 WGS84
SELECT AddGeometryColumn ('public', 'trip', 'destination_coord', 4326, 'POINT', 2); -- 4326 WGS84

--COPY trip(region,origin_coord,destination_coord,datetime,datasource) FROM '/files/trips.csv' WITH CSV HEADER;

CREATE EXTENSION h3;