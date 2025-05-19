select DISTINCT observationTime
FROM {satellite}
WHERE haversine(latitude,longitude,?,?) < ?;