import RPi.GPIO as GPIO
import time
import datetime
import json

# GPIO pins of raspberry
power_relays = 16
relays_one = 5
relays_two = 6


def setup_gpios():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(power_relays, GPIO.OUT)
    GPIO.setup(relays_one, GPIO.OUT)
    GPIO.setup(relays_two, GPIO.OUT)


def write_time_to_json(hour, minute):
    """
    Writes time to json file, which is located next to this python script.
    :param hour: hour to write
    :param minute: minute to write
    """
    json_data = open("LastTimeState.json", "r")
    json_object = json.load(json_data)
    json_data.close()
    json_object["hour"] = hour
    json_object["minute"] = minute

    json_data = open("LastTimeState.json", "w")
    json.dump(json_object, json_data)
    json_data.close()


def clock_hand_step(minute, init):
    """
    Moves the clock hands by changing polarity with the relays. This method checks what polarisation to use, depending
    on even and uneven minute position of the clock. The clock movement speed is pretty slow, so every minute step is
    defined to take 4 seconds.
    :param minute: minute number to check if it is even or uneven
    :param init: On clock initialization the polarity steps have to be inversed
    """
    power_delay = 4
    switch_delay = 0.2
    if init:
        polarisation = (minute % 2) == 0
    else:
        polarisation = not ((minute % 2) == 0)

    if polarisation:
        GPIO.output(relays_one, GPIO.LOW)
        GPIO.output(relays_two, GPIO.LOW)
        time.sleep(switch_delay)
        GPIO.output(power_relays, GPIO.HIGH)
        time.sleep(power_delay)
        GPIO.output(power_relays, GPIO.LOW)
    else:
        GPIO.output(relays_one, GPIO.HIGH)
        GPIO.output(relays_two, GPIO.HIGH)
        time.sleep(switch_delay)
        GPIO.output(power_relays, GPIO.HIGH)
        time.sleep(power_delay)
        GPIO.output(power_relays, GPIO.LOW)


def converted_hour_now():
    """
    Converts the hour to american standard (e.g. 6AM or 6PM). This is necessary because the clock has 12 hours on the
    clock face.
    """
    if datetime.datetime.now().time().hour > 12:
        return datetime.datetime.now().time().hour - 12
    elif datetime.datetime.now().time().hour == 0:
        return 12
    else:
        return datetime.datetime.now().time().hour


def initialize_clock_hands():
    """
    On reboot of the Pi the clock gets set to the right time. After powerloss it checks the last saved time in the .json
    file and moves the clock hands until the hands reach the actual time.
    """
    json_data = open("LastTimeState.json", "r")
    last_known_time = json.load(json_data)
    json_data.close()
    last_known_hour = last_known_time["hour"]
    last_known_minute = last_known_time["minute"]

    if (last_known_hour != converted_hour_now()) or (last_known_minute != datetime.datetime.now().time().minute):
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


def clock_state():
    """
    Lets the clock work like a normal clock should.
    """
    last_minute = datetime.datetime.now().time().minute
    while (True):
        if last_minute != datetime.datetime.now().time().minute:
            last_minute = datetime.datetime.now().time().minute
            write_time_to_json(converted_hour_now(), datetime.datetime.now().time().minute)
            clock_hand_step(datetime.datetime.now().time().minute, False)


if __name__ == '__main__':
    setup_gpios()
    initialize_clock_hands()
    clock_state()
