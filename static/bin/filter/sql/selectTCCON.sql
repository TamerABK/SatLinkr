SELECT latitude, longitude, AVG({field_name})
FROM TCCON
WHERE ? < observationTime AND observationTime < ?
AND haversine(latitude, longitude, ?, ?) < ?
AND NOT {field_name} = -999.0
GROUP BY latitude, longitude