WITH count_region AS (
	SELECT 
		count(*) AS trip_count,
		region
	FROM trip
	GROUP BY region
), ranked_region AS (
	SELECT 
		ROW_NUMBER() OVER(ORDER BY cr.trip_count DESC) AS pos,
		cr.region
	FROM 
		count_region AS cr
), max_datasource AS (
	SELECT 
		max(t.datetime) AS max_date,
		t.region
	FROM trip AS t
	GROUP BY t.region 
)
SELECT datasource, t.region  
FROM 
	ranked_region rr
INNER JOIN trip t ON t.region = rr.region
INNER JOIN max_datasource md ON md.region = t.region 
WHERE 
	rr.pos <= 2
	AND md.max_date = t.datetime ;
	
