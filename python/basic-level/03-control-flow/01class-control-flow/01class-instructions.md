# instructions
Before we dive deep into something called an if statement, let's do a fun demo using a coin flip simulation!


Create a coin_flip.py program and type in the following:

import random

num = random.randint(0, 1)   # Roll a random number that's either 0 or 1

````
if num > 0.5:
  print('Heads')
else:
  print('Tails')
````

Note: We will learn more about random and .randint() later in the chapter.

All you need to know is that this program simulates a coin toss:

≈ 50% of the time, it's "Heads".
≈ 50% of the time, it's "Tails".