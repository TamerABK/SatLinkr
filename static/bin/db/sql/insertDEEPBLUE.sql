INSERT OR IGNORE INTO MODIS_DEEP_BLUE (
  observationTime,
  latitude,
  longitude,
  Aerosol_Optical_Thickness_Land_Count_550,
  Aerosol_Optical_Thickness_Land_Maximum_550,
  Aerosol_Optical_Thickness_Land_Mean_550,
  Aerosol_Optical_Thickness_Land_Minimum_550,
  Aerosol_Optical_Thickness_Land_Standard_Deviation_550,
  Angstrom_Exponent_Land_Maximum,
  Angstrom_Exponent_Land_Mean,
  Angstrom_Exponent_Land_Minimum,
  Angstrom_Exponent_Land_Standard_Deviation,
  Spectral_Aerosol_Optical_Thickness_Land_Count_412,
  Spectral_Aerosol_Optical_Thickness_Land_Count_488,
  Spectral_Aerosol_Optical_Thickness_Land_Count_670,
  Spectral_Aerosol_Optical_Thickness_Land_Mean_412,
  Spectral_Aerosol_Optical_Thickness_Land_Mean_488,
  Spectral_Aerosol_Optical_Thickness_Land_Mean_670,
  Spectral_Aerosol_Optical_Thickness_Land_Standard_Deviation_412,
  Spectral_Aerosol_Optical_Thickness_Land_Standard_Deviation_488,
  Spectral_Aerosol_Optical_Thickness_Land_Standard_Deviation_670
) VALUES (
  ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
);
