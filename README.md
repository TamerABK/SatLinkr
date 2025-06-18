# satelliteImageryApp

 This webapp tool was developped with Flask, and relying on Folium for the Satellite Imagery and visualisation. 
 It offers visualisation for data from OCO2, GOSAT, and MODIS, products: 

- OCO2_L2_Lite_FP : https://disc.gsfc.nasa.gov/datasets/OCO2_L2_Lite_FP_11.2r/summary?keywords=oco2

- GOSAT-2 TANSO-FTS-2 SWIR L2 Chlorophyll Fluorescence and Proxy-method Product : https://prdct.gosat-2.nies.go.jp/documents/documents.html.en

- AERDB_D3_VIIRS_NOAA20 : https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/AERDB_D3_VIIRS_NOAA20


## Setup 

 - ### Step one: Download and extract the zip from the releases
 
 - ### Step two: Configuring config.env

   There should be a **config.env** file in the same directory as the exe, this is the file where the necessary autentification credentials for the data fetching is located.
   Each of these fields need to be filled to be able to download files for the fetching function, and they need to be updated once they expire.
   

        [OCO2]
        username = 
        password = 
        cookies = 
        [SFTP]
        host = 
        port = 22 
        username = 
        password = 
        [MODIS]
        token = 


     ### OCO2
      username and password are your Nasa Earthdata account details.  
      And cookies is the path to the cookies file you will have to create using the instructions in this page : https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20Access%20GES%20DISC%20Data%20Using%20wget%20and%20curl

     ### SFTP
      host, and port are the links to GOSAT sftp server which you can find here : https://prdct.gosat-2.nies.go.jp/aboutdata/directsftpaccess.html.en  
      username and password in this section are your GOSAT account details.

     ### MODIS
      token is generated using these instructions: https://ladsweb.modaps.eosdis.nasa.gov/learn/download-files-using-edl-tokens/  
      You will need your  Nasa Earthdata account details to be able to generate it.

- ### Step three: Link files
  
     While GOSAT doesn't need anymore setup than this, OCO2 and MODIS require files with the links to files.

    ### OCO2
     The links for OCO2 expire 2 days after they're generated : https://disc.gsfc.nasa.gov/datasets/OCO2_L2_Lite_FP_11.2r/summary?keywords=oco2  
     They have to be in a file named **OCO2.txt** in the same folder as the exe

   ### MODIS
     The links for AERDB_D3_VIIRS_NOAA20 don't expire, but you have a limit about 2000 when getting them on the site, with them being quite slow.
      The resulting links have to be in a file named **DEEP.json**

  - ### Step four: Updating Amazon CA certificates

    In case the Amazon CA certificates expire, you can find them here : https://www.amazontrust.com/repository/
    You just have to copy them to the **amazon.pem** file.
     

## Fetching data

After being setup, the webapp allows you to download and filter out data for a region of your choosing in the   **Fetch Data**  tab:

  - **Choose file Source allows** you to specify wether you want to attempt to download files for the missing dates or only look in the * /data * folders, 

  - **Choose Region Option** gives you the option to choose wether you want to fetch data for a region you already created with the same parameters (satellite, center latitude, center longitude, radius) or create a new one:

      -  If you choose **Select Existing Region**, you only have to choose one of the options in **Select Region**
      -  If you choose **Create New region**, you then have input for what name, satellite, center latitude, center longitude, radius you want the region to have

  - **Starting date** and **Ending date** are for the period you want to fetch for, those dates included, they take it in the dd/mm/yyyy format

  - **Keep files** when checked keeps all the downloaded files, as by default they're deleted to save space, this is useful to use when you're fetching for multiple regions with the satellite for the same period 


The way to track how far along the fetching operation is in the open terminal.

## MAP Params

This is were the fun stuff are. With a display on top for regions, and what dates we have data for, you can set the parameters and display the data you have on the interactive satellite map,
you can download the map you have on screen as a png, or exctract the data you have within these parameters as a csv.

Delta is the interval of time around your date-time input where points are looked for, this is for OCO2 and GOSAT, as the MODIS data and 1' zones for a whole day of measurments. 

    

