SELECT DISTINCT  satellite, latitude, longitude, radius_km
FROM fetched_regions
WHERE region_name = ?;