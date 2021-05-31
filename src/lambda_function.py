from bs4 import BeautifulSoup as bs
import requests
import json


def scrape(
    station, units={"temp": "c", "pressure": "hpa", "speed": "kph", "precip": "mm"}
):
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    URL = "https://www.wunderground.com/dashboard/pws/"

    try:
        session = requests.Session()
        session.headers["User-Agent"] = USER_AGENT
        session.headers["Accept-Language"] = LANGUAGE
        session.headers["Content-Language"] = LANGUAGE
        html = session.get(URL + station["id"])

        soup = bs(html.text, "html.parser")
    except:
        return None

    if (
        soup.findAll("span", attrs={"_ngcontent-app-root-c173": ""})[21].text
        == "Online"
    ):
        data = {}

        # Last updated value
        data["LAST_UPDATED"] = soup.findAll(
            "span", attrs={"class": "ng-star-inserted"}
        )[0].text

        strings = data["LAST_UPDATED"].split()
        if (strings[0] == "(updated") and (strings[3] == "ago)"):
            value = int(strings[1])

            if (value >= 0) and (value <= 60):
                if strings[2][0:6] == "second":
                    data["LAST_UPDATED"] = value

                elif strings[2][0:6] == "minute":
                    data["LAST_UPDATED"] = value * 60

                elif strings[2][0:4] == "hour":
                    if (value >= 0) and (value <= 24):
                        data["LAST_UPDATED"] = value * 3600

                    else:
                        return None

                else:
                    return None

            else:
                return None

        # Get Temperature
        if "temp" in station["parameters"]:
            data["temp"] = soup.find("span", attrs={"class": "wu-value"})
            data["temp"] = round(float(data["temp"].text))

            if units["temp"] == "c":
                data["temp"] = round((data["temp"] - 32) * (5 / 9), 1)

        # Get Wind Speed
        if "windSpeed" in station["parameters"]:
            data["wind_speed"] = soup.findAll("span", attrs={"class": "wu-value"})
            data["wind_speed"] = round(float(data["wind_speed"][2].text), 1)

            if units["speed"] == "kmph":
                data["wind_speed"] = round(data["wind_speed"] * 1.6, 1)

            elif units["speed"] == "mps":
                data["wind_speed"] = round(data["wind_speed"] * (4 / 9), 1)

        # Get Wind Gust
        if "windGust" in station["parameters"]:
            data["wind_gust"] = soup.findAll("span", attrs={"class": "wu-value"})
            data["wind_gust"] = round(float(data["wind_gust"][3].text), 1)

            if units["speed"] == "kmph":
                data["wind_gust"] = round(data["wind_gust"] * 1.6, 1)

            elif units["speed"] == "mps":
                data["wind_gust"] = round(data["wind_gust"] * (4 / 9), 1)

        # Get Wind Bearing
        if "windBearing" in station["parameters"]:
            data["wind_bearing"] = soup.find("div", attrs={"class": "arrow-wrapper"})

            string_full = ((data["wind_bearing"]["style"]).split())[1]
            string_start = string_full[0:7]
            string_end = string_full[-5:-1]

            if (string_start == "rotate(") and (string_end == "deg)"):
                data["wind_bearing"] = int(string_full[7:-5]) - 180
            else:
                data["wind_bearing"] = None

        # Get Precipitation Rate
        if "precipRate" in station["parameters"]:
            data["precip_rate"] = soup.findAll("span", attrs={"class": "wu-value"})
            data["precip_rate"] = round(float(data["precip_rate"][5].text), 2)

            if units["precip"] == "mm":
                data["precip_rate"] = round(data["precip_rate"] * 25.4, 2)

        # Get Precipitation Total
        if "precipTotal" in station["parameters"]:
            data["precip_total"] = soup.findAll("span", attrs={"class": "wu-value"})
            data["precip_total"] = round(float(data["precip_total"][8].text), 2)

            if units["precip"] == "mm":
                data["precip_total"] = round(data["precip_total"] * 25.4, 2)

        # Get Pressure
        if "pressure" in station["parameters"]:
            data["pressure"] = soup.findAll("span", attrs={"class": "wu-value"})
            data["pressure"] = round(float(data["pressure"][6].text), 2)

            if units["pressure"] == "hpa":
                data["pressure"] = round(data["pressure"] * 33.86, 2)

        # Get Humidity
        if "humidity" in station["parameters"]:
            data["humidity"] = soup.findAll("span", attrs={"class": "wu-value"})
            data["humidity"] = round(float(data["humidity"][7].text))

        # Get UV Index
        if "uvIndex" in station["parameters"]:
            data["uv_index"] = soup.findAll("span", attrs={"class": "wu-value"})
            data["uv_index"] = round(float(data["uv_index"][9].text))

        # Get Solar Radiation
        if "radiation" in station["parameters"]:
            data["radiation"] = soup.findAll("div", attrs={"class": "weather__text"})
            strings = data["radiation"][-1].text.split()

            if strings[1][-8:-3] == "watts":
                data["radiation"] = round(float(strings[0]), 1)
            else:
                data["radiation"] = None

    return data


def lambda_handler(event, context):
    # 1. Try to extract the parameters passed
    try:
        station_id = event["queryStringParameters"]["stationId"]
        del event["queryStringParameters"]["stationId"]
    except:
        raise Exception("Invalid queryStringParameters")

    parameters = []
    for value in event["queryStringParameters"].values():
        parameters.append(value)

    station = {}
    station["id"] = station_id
    station["parameters"] = parameters

    # 2. Scrape Wunderground website
    response_body = scrape(station)

    # 3. Construct http response object
    response_obj = {}
    response_obj["statusCode"] = 200
    response_obj["headers"] = {}
    response_obj["headers"]["Content-Type"] = "application/json"
    response_obj["body"] = json.dumps(response_body)

    # 4. Return the response object
    return response_obj


# def debug():
#     event = {
#         "queryStringParameters": {
#             "stationId": "ICURITIB24",
#             "p0": "temp",
#             "p1": "windSpeed",
#             "p2": "windGust",
#             "p3": "windBearing",
#             "p4": "pressure",
#             "p5": "humidity",
#             "p6": "precipRate",
#             "p7": "precipTotal",
#             "p8": "uvIndex",
#             "p9": "radiation",
#         }
#     }

#     print(json.dumps(lambda_handler(event, None), indent=4))


# debug()
