import random
symbols = ['🍒', '🍇', '🍉', '7️⃣']
def play():
    results = random.choices(symbols, k=3)
    print(f"{results[0]} | {results[1]} | {results[2]}")

    if results[0] == '7️⃣' and results[1] == '7️⃣' and results[2] == '7️⃣':
        print("Jackpot! 💰")
    else:
        print("Thanks for playing!")


while True:
    input("\nPress Enter to play...")
    play()

    again = input("Play again? (y/n): ").lower()
    if again != 'y':
        print("Goodbye!")
        break
