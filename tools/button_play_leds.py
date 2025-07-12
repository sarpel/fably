#!/usr/bin/env python3
"""Test that bottoms, playing sounds and LEDs work together properly and concurrently."""

import threading

try:
    from apa102_pi.colorschemes import colorschemes
except ImportError:
    colorschemes = None

try:
    from gpiozero import Button
except ImportError:
    Button = None

if colorschemes is None:
    print("Bu script bir LED şeridi gerektirir. IQAudio HAT'te LED yok, çıkılıyor.")
    exit(1)
if Button is None:
    print("Bu script bir GPIO buton gerektirir. IQAudio HAT'te buton yok, çıkılıyor.")
    exit(1)

from fably import utils

NUM_LED = 3
GPIO_PIN = 17
CYCLES = 4
BRIGHTNESS = 15

def play_sound():
    utils.play_sound("hi")

def flash_leds():
    my_cycle = colorschemes.TheaterChase(
        num_led=NUM_LED,
        pause_value=0.03,
        num_steps_per_cycle=35,
        num_cycles=CYCLES,
        order="rgb",
        global_brightness=BRIGHTNESS,
    )
    my_cycle.start()

def button_pressed():
    sound_thread = threading.Thread(target=play_sound)
    sound_thread.start()
    led_thread = threading.Thread(target=flash_leds)
    led_thread.start()

def main():
    try:
        button = Button(GPIO_PIN)
        button.when_pressed = button_pressed
    except Exception:
        print("GPIO pin bulunamadı. Test çalıştırılamıyor.")
        return
    try:
        print("Butona basınca ses çalacak ve LED yanacak.")
        input("Çıkmak için Enter'a basın...\n")
    except KeyboardInterrupt:
        print("Program sonlandırıldı.")

if __name__ == "__main__":
    main()
