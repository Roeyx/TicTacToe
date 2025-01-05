"""
This is the client-side implementation of a Tic Tac Toe game.
It handles player connections, game interaction, and communication with the server.
"""

import socket
import time
import json
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000  # The port used by the server
FORMAT = 'utf-8'
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

"""
Handles the game exit process by sending an exit signal to the server,
closing the client socket, and terminating the program gracefully.
"""
def exit_game():
    print("Exiting the game.")
    client_socket.send("e".encode(FORMAT))
    client_socket.close()  # Close the client socket
    sys.exit("Player has exited the game.")  # Terminate the program

"""
Converts the server's string representation of the game board into a matrix format.
Takes a message string as input and returns either a matrix representation of the board
or None if the message is not a valid board format.
"""
def parse_game_board(message):
    """Parse the game board from the message and return a matrix."""
    if message.startswith("Current Board:"):
        # Extract the board part of the message after "Current Board:"
        board_str = message.split("Current Board:")[1].strip()

        # Split the board string into rows
        rows = board_str.split('\n')

        # Initialize an empty matrix
        matrix = []

        for row in rows:
            # Split each row by ' | ' and strip spaces around each element
            row_values = [cell.strip() for cell in row.split('|')]
            matrix.append(row_values)

        return matrix
    else:
        return None

"""
Validates whether a received message contains a valid game board structure.
Checks if the message can be parsed as JSON and contains required game board components.
Returns True if message is a valid game board, False otherwise.
"""
def is_game_board(message):
    """Check if the message is a game board (based on expected structure)."""
    try:
        game = json.loads(message)
        if "game_id" in game and "creator" in game and "board" in game:
            return True
        return False
    except json.JSONDecodeError:
        return False

"""
Displays the current game board in a readable format.
Takes a game dictionary containing creator, game_id, and board information.
Prints the formatted board to the console.
"""
def print_game_board(game):
    """Print the game board in a readable format."""
    print("\nReceived game board:")
    print(f"Creator: {game['creator']}")
    print(f"Game ID: {game['game_id']}")
    print("Board:")
    for row in game['board']:
        print(" | ".join(row))  # Nicely format the rows with separators
    print("\n")

"""
Main client function that handles the entire game flow from the client side.
Manages connection to server, game creation/joining, and game interaction.
Handles player moves and processes server responses.
"""
def start_client():
    client_socket.connect((HOST, PORT))

    Choose_Game = input("Press 1 to join an existing game\nPress 2 to create a new game\n")
    client_socket.send(Choose_Game.encode(FORMAT))
    Choose_Game = int(Choose_Game)

    if Choose_Game == 1:
        # Joining an existing game
        games_json = client_socket.recv(1024).decode(FORMAT)
        print(games_json)
        if (games_json == 'No available games at the moment.'):
            return
        available_games = json.loads(games_json)
        print(f"The following game rooms are available: {available_games}")

        game_id = input("Please enter the game ID you want to join: ")
        if int(game_id) not in available_games:
            print("Invalid game ID. Exiting.")
            return

        time.sleep(0.5)
        client_socket.send(game_id.encode(FORMAT))
        player_number = client_socket.recv(1024).decode(FORMAT) #recv player number
        print(f"Waiting to all players to connect\nYou are player {player_number}")
        initial_board = client_socket.recv(1024).decode(FORMAT)
        print(initial_board)
        board=parse_game_board(initial_board)
        update="board received"
        client_socket.send(update.encode(FORMAT))
        active_game = True
        print("Starting game")
        while active_game:
            message = client_socket.recv(1024).decode(FORMAT)
            print(message)
            if (message == 'A player has left.'):
                exit_game()
                break
            message_check=parse_game_board(message)
            if (isinstance(message_check,list)):
                    if isinstance(message_check[0],list):
                        board=message_check
            if (message == f'player {player_number} turn'):
                while True:  # Keep asking for input until valid input is provided
                    move = input("Enter your move in the format (row,col):\nPress e to exit game\n")
                    if (move == 'e'):
                        exit_game()
                        break
                    move = move.strip('()')
                    # Check if input can be split into exactly two integers
                    try:
                        row, col = map(int, move.split(','))

                        # Check if the row and col are within the valid range (0 to 2)
                        if 0 <= row <= (len(board)-1) and 0 <= col <= (len(board)-1):
                            if (board[row][col]==""):
                                client_socket.send(move.encode(FORMAT))
                                break  # Valid input, exit the loop
                            else:
                                print("Invalid move! The spot is already taken.")
                        else:
                            print("Invalid move! Row and column must be between 0 and 2.")
                    except ValueError:
                        print("Invalid input format! Please enter the move as (row,col) with integers.")

    elif Choose_Game == 2:
        # Creating a new game
        game_size=input("Enter number of players for the game\n")
        client_socket.send(game_size.encode(FORMAT))
        print("Waiting for other players to join...")
        game_size = int(game_size)
        wait_mode=True
        while wait_mode:
            message = client_socket.recv(1024).decode(FORMAT)
            time.sleep(2.5) #sleep to avoid busy wait
            print(f"number of connected players: {message}/{game_size}")
            message=int(message)
            if(message>(game_size-1)):
                wait_mode=False
                print("Waiting to all players to connect\nYou are player 1")
        initial_board = client_socket.recv(1024).decode(FORMAT)
        print(initial_board)
        board=parse_game_board(initial_board)
        update="board received"
        client_socket.send(update.encode(FORMAT))
        active_game = True
        print("Starting game")
        while active_game:
            message = client_socket.recv(1024).decode(FORMAT)
            print(message)
            if (message == 'A player has left.'):
                exit_game()
                break
            message_check=parse_game_board(message)
            if (isinstance(message_check,list)):
                    if isinstance(message_check[0],list):
                        board=message_check
            if(message == "player 1 turn"):
                while True:  # Keep asking for input until valid input is provided
                    move = input("Enter your move in the format (row,col):\nPress e to exit game\n")
                    if (move == 'e'):
                        exit_game()
                        break
                    move = move.strip('()')
                    # Check if input can be split into exactly two integers
                    try:
                        row, col = map(int, move.split(','))

                        # Check if the row and col are within the valid range (0 to 2)
                        if 0 <= row <= (len(board)-1) and 0 <= col <= (len(board)-1):
                            if (board[row][col]==""):
                                client_socket.send(move.encode(FORMAT))
                                break  # Valid input, exit the loop
                            else:
                                print("Invalid move! The spot is already taken.")
                        else:
                            print("Invalid move! Row and column must be between 0 and 2.")
                    except ValueError:
                        print("Invalid input format! Please enter the move as (row,col) with integers.")

    client_socket.close()
    print("\n[CLOSING CONNECTION] Client closed socket!")

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("[CLIENT] Started running")
    start_client()
    print("\nGoodbye client :)")
