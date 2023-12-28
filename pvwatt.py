import requests
import json

def get_pvwatts_data(system_capacity, module_type, losses, array_type, tilt, azimuth, lat, lon):
    url = "https://developer.nrel.gov/api/pvwatts/v8.json"  # Changed to v8
    params = {
        'api_key': 'ef43dSIdvg397HVWEE9zfaoWd7UdesbxudgETPTn',
        'system_capacity': system_capacity,
        'module_type': module_type,
        'losses': losses,
        'array_type': array_type,
        'tilt': tilt,
        'azimuth': azimuth,
        'lat': lat,
        'lon': lon,
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data