SELECT latitude, longitude, {field_name}
FROM GOSAT
WHERE ? < observationTime AND observationTime < ?
AND haversine(latitude, longitude, ?, ?) < ?
AND NOT {field_name} = -999.0
