SELECT latitude,longitude, {field_name}
FROM MODIS_DEEP_BLUE
WHERE ? < observationTime AND observationTime < ?
AND haversine(latitude, longitude, ?, ?) < ?
AND NOT {field_name} = -999.0