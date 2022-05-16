SELECT 
	* 
FROM 
	trip AS t 
WHERE 
	ST_Contains(ST_MakeEnvelope(10, 10, 11, 11, 4326), t.origin_coord)
	AND ST_Contains(ST_MakeEnvelope(10, 10, 11, 11, 4326), t.destination_coord);

-- ST_MakeEnvelope(float xmin, float ymin, float xmax, float ymax, integer srid=unknown);

 
	 
	