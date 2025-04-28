INSERT OR REPLACE INTO OCO2 (
    observationTime,
    latitude,
    longitude,
    solar_zenith_angle,
    sensor_zenith_angle,
    xco2_quality_flag,
    xco2_qf_bitflag,
    xco2_qf_simple_bitflag,
    xco2,
    xco2_x2019,
    xco2_uncertainty,
    xco2_apriori,
    pressure_levels,
    co2_profile_apriori,
    xco2_averaging_kernel,
    pressure_weight
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);