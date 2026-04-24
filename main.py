from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import smtplib
import time

load_dotenv()

def get_sunset():
    params = {
        "lat": os.getenv("LAT"),
        "lng": os.getenv("LONG"),
        "formatted": 0,
        "tzid": "EST"
    }

    url = "https://api.sunrise-sunset.org/json"

    sunset_res = requests.get(url=url, params=params)
    sunset_res.raise_for_status()
    data = sunset_res.json()
    return [int(data["results"]["sunrise"].split("T")[1].split(":")[0]), int(data["results"]["sunset"].split("T")[1].split(":")[0])]

def get_iss_position(sunset):
    url = "http://api.open-notify.org/iss-now.json"
    iss_res = requests.get(url=url)
    iss_res.raise_for_status()

    iss_position = iss_res.json()["iss_position"]
    return [float(iss_position["latitude"]), float(iss_position["longitude"])]

def within_five_degrees_of_iss(iss_lat, iss_long):
    return abs(iss_lat - float(os.getenv("LAT")) < 5 and abs(iss_long - float(os.getenv("LONG"))))

def is_nighttime(sunrise, sunset):
    current_hour = datetime.now().hour
    return sunset < current_hour < sunrise


def send_email():
    with smtplib.SMTP(os.getenv("SMTP_HOST"), port=587) as connection:
        connection.starttls()
        connection.login(
            user=os.getenv("GMAIL_ADDRESS"),
            password=os.getenv("GMAIL_APP_PASSWORD")
        )
        connection.sendmail(
            from_addr=os.getenv("GMAIL_ADDRESS"),
            to_addrs=os.getenv("GMAIL_ADDRESS"),
            msg="Subject: ISS Overhead!\n\nLook up!"
        )

def main():
    sunrise, sunset = get_sunset()
    lat, long = get_iss_position(sunset)

    if within_five_degrees_of_iss(lat, long) and is_nighttime(sunrise, sunset):
        send_email()


if __name__ == "__main__":
    while True:
        time.sleep(60)
        main()