# import requests
# import os
# import numpy as np

# API_KEY = os.getenv("OPENWEATHER_API_KEY")

# # =========================
# # SAFE API CALL
# # =========================
# def safe_request(url):
#     try:
#         response = requests.get(url, timeout=5)
#         data = response.json()

#         if response.status_code != 200:
#             print("❌ API Error:", data)
#             return None

#         return data
#     except Exception as e:
#         print("❌ Request Failed:", e)
#         return None


# # =========================
# # CURRENT WEATHER (FALLBACK)
# # =========================
# def get_current_weather(city):
#     url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

#     data = safe_request(url)

#     if data is None:
#         return 25, 1000  # fallback

#     try:
#         temp = data['main']['temp']
#         rainfall = data.get('rain', {}).get('1h', 0) * 1000  # convert to mm approx
#     except:
#         return 25, 1000

#     return temp, rainfall


# # =========================
# # FORECAST WEATHER (MAIN)
# # =========================
# def get_forecast_weather(city):
#     url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

#     data = safe_request(url)

#     if data is None:
#         return get_current_weather(city)

#     try:
#         temps = []
#         rainfall = 0

#         for entry in data['list']:
#             temps.append(entry['main']['temp'])
#             rainfall += entry.get('rain', {}).get('3h', 0)

#         avg_temp = np.mean(temps)

#         # 🔥 yearly approximation (controlled, not crazy)
#         yearly_rainfall = rainfall * 73  # (365/5 ≈ 73)

#         # sanity limits
#         if yearly_rainfall < 100:
#             yearly_rainfall = 500
#         if yearly_rainfall > 4000:
#             yearly_rainfall = 2000

#     except Exception as e:
#         print("❌ Forecast parsing error:", e)
#         return get_current_weather(city)

#     return avg_temp, yearly_rainfall


# # =========================
# # FINAL FUNCTION (USE THIS)
# # =========================
# # def get_weather_features(city):

# #     # 🔥 FIX: invalid location handling
# #     if not city or len(city) < 3:
# #         return 25, 1000

# #     city = city.strip()

# #     temp, rain = get_forecast_weather(city)

# #     return temp, rain
# def get_weather_features(city):

#     if not city or len(city.strip()) < 3:
#         return None, None   # ❗ default नहीं, None

#     city = city.strip()

#     try:
#         temp, rain = get_forecast_weather(city)
#         return temp, rain
#     except:
#         return None, None
# # def get_weather_features(city):
# #     try:
# #         temp, rain = get_forecast_weather(city)
# #         return temp, rain
# #     except Exception as e:
# #         return None, None
# # =========================
# # TEST
# # =========================
# if __name__ == "__main__":
#     city = "Agra"

#     temp, rain = get_weather_features(city)

#     print(f"🌡 Temp: {temp}")
#     print(f"🌧 Rainfall (year approx): {rain}")
import requests
import os
import numpy as np

API_KEY = os.getenv("OPENWEATHER_API_KEY")

# =========================
# SAFE API CALL (NO PRINT)
# =========================
def safe_request(url):
    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        # ❌ Silent fail (NO PRINT)
        if response.status_code != 200:
            return None

        return data

    except:
        return None


# =========================
# CURRENT WEATHER (FALLBACK)
# =========================
def get_current_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    data = safe_request(url)

    if data is None:
        return None, None

    try:
        temp = data['main']['temp']
        rainfall = data.get('rain', {}).get('1h', 0) * 1000
    except:
        return None, None

    return temp, rainfall


# =========================
# FORECAST WEATHER (MAIN)
# =========================
def get_forecast_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

    data = safe_request(url)

    if data is None:
        return get_current_weather(city)

    try:
        temps = []
        rainfall = 0

        for entry in data['list']:
            temps.append(entry['main']['temp'])
            rainfall += entry.get('rain', {}).get('3h', 0)

        avg_temp = np.mean(temps)

        # yearly approx
        yearly_rainfall = rainfall * 73

        # sanity limits
        yearly_rainfall = max(300, min(yearly_rainfall, 3000))

    except:
        return get_current_weather(city)

    return avg_temp, yearly_rainfall


# =========================
# FINAL FUNCTION
# =========================
def get_weather_features(city):

    if not city or len(city.strip()) < 3:
        return None, None

    city = city.strip()

    temp, rain = get_forecast_weather(city)

    return temp, rain


# =========================
# TEST
# =========================
if __name__ == "__main__":
    city = "Agra,IN"

    temp, rain = get_weather_features(city)

    print(f"🌡 Temp: {temp}")
    print(f"🌧 Rainfall: {rain}")