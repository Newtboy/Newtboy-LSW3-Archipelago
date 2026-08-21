from worlds.lsw3.LSW3Client.game import LSW3Memory


def main():
    print("Connecting to Dolphin...")

    game = LSW3Memory()

    print("Connected!")
    print()

    print(f"Studs:       {game.studs:,}")
    print(f"Gold Bricks: {game.gold_bricks}")

    while True:
        command = input("> ").strip().lower()

        if command == "status":
            print(f"Studs:       {game.studs:,}")
            print(f"Gold Bricks: {game.gold_bricks}")

        elif command == "gold":
            game.add_gold_brick()
            print(f"Gold Bricks: {game.gold_bricks}")

        elif command == "quit":
            break

        else:
            print("Commands: status, gold, quit")


if __name__ == "__main__":
    main()