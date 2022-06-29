import time
import os
import requests
from datetime import datetime
import smtplib
from tkinter import Tk

MY_LAT = -47#-33.932106
MY_LNG = 89#18.860151


def getUTC():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LNG,
        "username": "al3gor",
    }

    response = requests.get("http://api.geonames.org/timezoneJSON?", params=parameters)
    response.raise_for_status()
    data = response.json()["rawOffset"]

    return data


def check_iss():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    iss_position = {
        "iss_latitude": float(data["iss_position"]["latitude"]),
        "iss_longitude": float(data["iss_position"]["longitude"]),
    }
    return iss_position


def check_sun():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LNG,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sun_data = {
        "sunrise": int(data["results"]["sunrise"].split("T")[1].split(":")[0]) + int(getUTC()),
        "sunset": int(data["results"]["sunset"].split("T")[1].split(":")[0]) + int(getUTC())
    }
    return sun_data


time_now = datetime.now()


def send_mail():
    my_email = os.environ["env_email"]
    password = os.environ["env_password"]

    connection = smtplib.SMTP("smtp.mail.yahoo.com")
    connection.starttls()
    connection.login(my_email, password)

    message = "ISS is above look up"
    subject = "ISS ABOVE!"

    connection.sendmail(from_addr=my_email, to_addrs="andrewknoesen@gmail.com",
                        msg=f"Subject: {subject}\n\n{message}")
    connection.close()
    print("Mail Sent")


# Your position is within +5 or -5 degrees of the ISS position.
def check_if_above():
    print("Checking")
    iss_location = check_iss()
    sun_location = check_sun()
    if abs(iss_location["iss_latitude"] - MY_LAT) <= 5 and abs(iss_location["iss_longitude"] - MY_LNG) <= 5:
        # check if currently dark
        if time_now.hour < sun_location["sunrise"] or time_now.hour > sun_location["sunset"]:
            print("It's above and dark. Sending mail\n")
            send_mail()
        else:
            print("It's above but sadly dark. Not sending mail\n")
    else:
        print(f"Alas it's not above:\n"
              f"ISS Location: Latitude:{iss_location['iss_latitude']}, Longitude: {iss_location['iss_longitude']}\n"
              f"Your location: Latitude:{MY_LAT}, Longitude: {MY_LNG}\n")


# Tk().after(60000, check_if_above())   Using TkInter to run the loop

check_if_above()

while (1):
    print("Waiting 60 seconds\n")
    time.sleep(60)
    print("Running code...\n")
    check_if_above()
