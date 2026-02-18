import datetime
import random as rd

bday_messages = ["Hope you have a very Happy Birthday!🎈",
          "It's your special day – get out there and celebrate! 🎉",
          "You were born and the world got better – everybody wins! 🥳",
          "Have lots of fun on your special day! 🎂",
          "Another year of you going around the sun! 🌞"
    ]

random_choice = rd.choice(bday_messages[1])
today = datetime.date.today()
next_birthday = "2008.01.07"

