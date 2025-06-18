SELECT *
FROM {satellite}
WHERE  haversine(latitude, longitude, ?, ?) < ?