import RPi.GPIO as GPIO
import time
import datetime
import json

# GPIO pins of raspberry
power_relais = 16
relais_one = 5
relais_two = 6


def setup_gpios():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(power_relais, GPIO.OUT)
    GPIO.setup(relais_one, GPIO.OUT)
    GPIO.setup(relais_two, GPIO.OUT)


def write_time_to_json(hour, minute):
    json_data = open("LastTimeState.json", "r")
    json_object = json.load(json_data)
    json_data.close()

    json_object["hour"] = hour
    json_object["minute"] = minute

    json_data = open("LastTimeState.json", "w")
    json.dump(json_object, json_data)
    json_data.close()


def clock_hand_step(minute, init):
    power_delay = 4
    switch_delay = 0.2
    if init:
        polarisation = (minute % 2) == 0
    else:
        polarisation = not ((minute % 2) == 0)

    if polarisation:
        GPIO.output(relais_one, GPIO.LOW)
        GPIO.output(relais_two, GPIO.LOW)
        time.sleep(switch_delay)
        GPIO.output(power_relais, GPIO.HIGH)
        time.sleep(power_delay)
        GPIO.output(power_relais, GPIO.LOW)
    else:
        GPIO.output(relais_one, GPIO.HIGH)
        GPIO.output(relais_two, GPIO.HIGH)
        time.sleep(switch_delay)
        GPIO.output(power_relais, GPIO.HIGH)
        time.sleep(power_delay)
        GPIO.output(power_relais, GPIO.LOW)


def converted_hour_now():
    if datetime.datetime.now().time().hour > 12:
        return datetime.datetime.now().time().hour - 12
    elif datetime.datetime.now().time().hour == 0:
        return 12
    else:
        return datetime.datetime.now().time().hour


def initialize_clock_hands():
    json_data = open("LastTimeState.json", "r")
    last_known_time = json.load(json_data)
    json_data.close()
    last_known_hour = last_known_time["hour"]
    last_known_minute = last_known_time["minute"]

    if (last_known_hour != converted_hour_now()) or (last_known_minute != datetime.datetime.now().time().minute):
        print("Time before: " + str(last_known_hour) + ":" + str(last_known_minute))
        print("Time now: " + str(converted_hour_now()) + ":" + str(datetime.datetime.now().time().minute))

        while (not ((last_known_hour == converted_hour_now()) and (
                last_known_minute == datetime.datetime.now().time().minute))):
            if last_known_minute > 59:
                last_known_minute = 0
                last_known_hour += 1
            if last_known_hour > 12:
                last_known_hour = 1
            clock_hand_step(last_known_minute, True)
            last_known_minute += 1
            write_time_to_json(last_known_hour, last_known_minute)


def main():
    last_minute = datetime.datetime.now().time().minute
    while (True):
        if last_minute != datetime.datetime.now().time().minute:
            last_minute = datetime.datetime.now().time().minute
            write_time_to_json(converted_hour_now(), datetime.datetime.now().time().minute)
            clock_hand_step(datetime.datetime.now().time().minute, False)


if __name__ == '__main__':
    setup_gpios()
    initialize_clock_hands()
    main()
