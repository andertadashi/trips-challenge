DROP TABLE IF EXISTS trip;

CREATE EXTENSION IF NOT EXISTS h3;

CREATE TABLE IF NOT EXISTS trip (
	id SERIAL PRIMARY KEY,
    region VARCHAR(255) NOT NULL,
--    origin_coord geography(POINT(4326),
--    destination_coord geography(POINT(4326),
    origin_coord_h3 h3index,
    destination_coord_h3 h3index,
    hour_day smallint,
    datetime timestamp with time zone,
    datasource VARCHAR(255) NOT NULL
);

--SELECT AddGeometryColumn ('public', 'trip', 'origin_coord', 4326, 'POINT', 2); -- 4326 WGS84
--SELECT AddGeometryColumn ('public', 'trip', 'destination_coord', 4326, 'POINT', 2); -- 4326 WGS84

ALTER TABLE trip ADD COLUMN IF NOT EXISTS origin_coord geometry(Point,4326);
ALTER TABLE trip ADD COLUMN IF NOT EXISTS destination_coord geometry(Point,4326);

--COPY trip(region,origin_coord,destination_coord,datetime,datasource) FROM '/files/trips.csv' WITH CSV HEADER;

--SELECT h3_geo_to_h3(POINT('37.3615593,-122.0553238'), 7);

CREATE OR REPLACE FUNCTION trips_update_h3_trigger_fnc()
	RETURNS trigger AS
$$
BEGIN

	UPDATE trip
	SET origin_coord_h3      = subquery.origin_coord_h3,
	    destination_coord_h3 = subquery.destination_coord_h3,
	    hour_day             = subquery.hour_day
	FROM (
		SELECT 
			t.id, 
			h3_geo_to_h3(t.origin_coord, 7) AS origin_coord_h3, 
			h3_geo_to_h3(t.destination_coord, 7) AS destination_coord_h3, 
			date_part('hour', t.datetime) AS hour_day
	    FROM  
	    	trip AS t
	    WHERE
	    	t.origin_coord IS NULL OR t.destination_coord IS NULL OR t.hour_day IS NULL 
	) AS subquery
	WHERE trip.id = subquery.id;

RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';


DROP TRIGGER IF EXISTS trips_update_h3_trigger ON trip;
CREATE TRIGGER trips_update_h3_trigger
	AFTER INSERT
		ON "trip"
	FOR EACH ROW
EXECUTE PROCEDURE trips_update_h3_trigger_fnc();


