SELECT latitude,longitude,xco2
FROM OCO2
WHERE ? < observationTime AND observationTime < ?
AND haversine(latitude,longitude,?,?) < ?

