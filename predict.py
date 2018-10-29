#!/bin/bash/ env python3

import datetime

def predict():
    name = str(input("What is your Name?: "))
    while True:
        try:
            age = int(input("How old are you?: "))
        except ValueError:
            print("This is not an int!")
        else:
            current_year = datetime.datetime.now().year
            break

    year_born = current_year - age

    print(name, "I predict you were born in",year_born, "!")

predict()
