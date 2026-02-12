for bottles in range(99, 0, -1):
    if bottles > 1:
        next_bottles = bottles - 1

        if next_bottles == 1:
            bottle_word = "bottle"
        else:
            bottle_word = "bottles"

        print(f"{bottles} bottles of beer on the wall")
        print(f"{bottles} bottles of beer")
        print("Take one down, pass it around")
        print(f"{next_bottles} {bottle_word} of beer on the wall\n")

    else:
        # último verso
        print("1 bottle of beer on the wall")
        print("1 bottle of beer")
        print("Take one down, pass it around")
        print("No more bottles of beer on the wall")