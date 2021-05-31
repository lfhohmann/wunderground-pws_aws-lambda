[![](https://img.shields.io/badge/MAINTAINER-%40lfhohmann-blue?style=for-the-badge)](https://github.com/lfhohmann)
[![](https://img.shields.io/github/license/lfhohmann/wunderground-pws_aws-lambda?style=for-the-badge)](LICENSE)

# Wunderground PWS API on AWS Lambda

A serverless API that scrapes Wunderground PWS pages hosted on AWS Lambda

The API handles requests with the following structure:

`https://{aws-endpoint}/{stage}/{resource}?stationId={station_id}&p0={parameter_0}&p1={parameter_1}...`

+ **stationId:** (String)(Required)
  + The station id from the Wunderground website.
+ **p0 to p9:** (String)(Optional)
  + Optional parameters to be scraped, they can must be one of the following:
    + **temp:** Temperature reading of the weather station.
    + **windSpeed:** Wind Speed reading of the weather station.
    + **windGust:** Wind Gust Speed reading of the weather station.
    + **windBearing:** Wind Bearing reading of the weather station.
    + **pressure:** Barometric Pressure reading of the weather station.
    + **humidity:** Humidity reading of the weather station.
    + **precipRate:** Precipitation Rate reading of the weather station.
    + **precipTotal:** Accumulated Precipitation reading of the weather station.
    + **uvIndex:** UV Index reading of the weather station.
    + **radiation:** Solar radiation reading of the weather station in Watts per squared meter.

## Note

You must create an API Gateway and attach it as a trigger for this Lambda Function

#

[![Buy me a coffe!](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/lfhohmann)