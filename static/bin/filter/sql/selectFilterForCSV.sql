SELECT *
FROM {satellite}
WHERE ? < observationTime AND observationTime < ?
AND haversine(latitude, longitude, ?, ?) < ?