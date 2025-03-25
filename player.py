from util.dndnetwork import PlayerClient

if __name__ == "__main__":
    player = PlayerClient(
        name="Player 1",
        host="172.0.0.1",
        port=5555
    )
    player.connect()
    while True:
        buffer = player.receive_message()
        if buffer:
            print(f"Received: {buffer}")
        message = input("Enter your message: ")
        player.send_message(message)