import requests
import arrow
import pandas as pd
# functions to be used by the routes

# retrieve data from the api
def query_api(lat, lng, date):
    start = arrow.get(date)
    """submit the API query using variables for latitude and longitud in the browser"""
    try:
        data = requests.get(
        'https://api.stormglass.io/v2/weather/point',
            params={
                'lat': lat,
                'lng': lng,
                'start': start.to('UTC').timestamp(),
                'end' : start.shift(days=1).to('UTC').timestamp(),
                'params': ','.join(['swellHeight','swellDirection','swellPeriod','secondarySwellHeight','secondarySwellDirection','secondarySwellPeriod','waveHeight','waveDirection', 'windSpeed', 'windDirection', 'airTemperature', 'pressure'])
        },
        headers={
            'Authorization': 'fbfdabfc-72dd-11ed-92e6-0242ac130002-fbfdac6a-72dd-11ed-92e6-0242ac130002'
        }).json()
    except Exception as exc:
        print(exc)
        data = None
    return data

def extract_values(dictionary):
    extraction = dictionary['sg']
    return extraction

def convert_degrees(degrees):
    if degrees >= 0 and degrees < 22.5:
        direction = 'N'
    elif degrees >= 22.5 and degrees < 45:
        direction = 'NNE'
    elif degrees >= 45 and degrees < 67.5:
        direction = 'NE'
    elif degrees >= 67.5 and degrees < 90:
        direction = 'ENE'
    elif degrees >= 90 and degrees < 112.5:
        direction = 'E'
    elif degrees >= 112.5 and degrees < 135:
        direction = 'ESE'
    elif degrees >= 135 and degrees < 157.5:
        direction = 'SE'
    elif degrees >= 157.5 and degrees < 180:
        direction = 'SSE'
    elif degrees >= 180 and degrees < 202.5:
        direction = 'S'
    elif degrees >= 202.5 and degrees < 225:
        direction = 'SSW'
    elif degrees >= 225 and degrees < 247.5:
        direction = 'SW'
    elif degrees >= 247.5 and degrees < 270:
        direction = 'WSW'
    elif degrees >=270 and degrees < 292.5:
        direction = 'W'
    elif degrees >= 292.5 and degrees < 315:
        direction = 'WNW'
    elif degrees >= 315 and degrees < 337.5:
        direction = 'NW'
    elif degrees >= 337.5:
        direction = 'NNW'
    return direction

def create_df(hours):
    df = pd.DataFrame.from_dict(hours)

    df['swellHeightsg'] = df['swellHeight'].apply(lambda x: pd.Series(extract_values(x)))
    df['swellDirectionsg'] = df['swellDirection'].apply(lambda x: pd.Series(extract_values(x)))
    df['swellPeriodsg'] = df['swellPeriod'].apply(lambda x: pd.Series(extract_values(x)))
    df['waveDirectionsg'] = df['waveDirection'].apply(lambda x: pd.Series(extract_values(x)))
    df['waveHeightsg'] = df['waveHeight'].apply(lambda x: pd.Series(extract_values(x)))
    df['secondarySwellHeightsg'] = df['secondarySwellHeight'].apply(lambda x: pd.Series(extract_values(x)))
    df['secondarySwellDirectionsg'] = df['secondarySwellDirection'].apply(lambda x: pd.Series(extract_values(x)))
    df['secondarySwellPeriodsg'] = df['secondarySwellPeriod'].apply(lambda x: pd.Series(extract_values(x)))
    df['windSpeedsg'] = df['windSpeed'].apply(lambda x: pd.Series(extract_values(x)))
    df['windDirectionsg'] = df['windDirection'].apply(lambda x: pd.Series(extract_values(x)))
    df['airTemperaturesg'] = df['airTemperature'].apply(lambda x: pd.Series(extract_values(x)))
    df['pressuresg'] = df['pressure'].apply(lambda x: pd.Series(extract_values(x)))
    df['swellDirectiontext'] = df['swellDirectionsg'].apply(lambda x: pd.Series(convert_degrees(x)))
    df['secondarySwellDirectiontext'] = df['secondarySwellDirectionsg'].apply(lambda x: pd.Series(convert_degrees(x)))
    df['windDirectiontext'] = df['windDirectionsg'].apply(lambda x: pd.Series(convert_degrees(x)))
    df['waveDirectiontext'] = df['waveDirectionsg'].apply(lambda x: pd.Series(convert_degrees(x)))
    df['time'] = pd.to_datetime(df['time'])
    df['date_formated'] = df['time'].dt.strftime('%Y/%m/%d %H:%M')

    #df_stormglass = df[['date_formated', 'swellHeightsg', 'swellDirectiontext', 'swellPeriodsg', 'waveDirectiontext', 'waveHeightsg']].copy()
    #df_stormglass = df_stormglass.rename(columns={'date_formated': 'date_time', 'swellHeightsg': 'swellHeight', 'swellDirectiontext': 'swellDirection', 'swellPeriodsg':'swellPeriod', 'waveDirectiontext': 'waveDirection', 'waveHeightsg': 'waveHeight'})

    df_stormglass = df[['date_formated', 'waveHeightsg', 'swellHeightsg', 'swellDirectiontext', 'swellPeriodsg', 'secondarySwellHeightsg', 'secondarySwellDirectiontext', 'secondarySwellPeriodsg', 'windSpeedsg', 'windDirectiontext', 'airTemperaturesg', 'pressuresg']].copy()
    df_stormglass = df_stormglass.rename(columns={'date_formated': 'Session Time', 'waveHeightsg': 'Wave Height', 'swellHeightsg': 'Primary Swell Height', 'swellDirectiontext': 'Primary Swell Direction', 'swellPeriodsg':'Primary Swell Period', 'secondarySwellHeightsg':'Secondary Swell Height', 'secondarySwellDirectiontext': 'Secondary Swell Direction', 'secondarySwellPeriodsg': 'Secondary Swell Period', 'windSpeedsg': 'Wind Speed', 'windDirectiontext':'Wind Direction','airTemperaturesg':'Temperature','pressuresg':'Pressure'})
    return df_stormglass


