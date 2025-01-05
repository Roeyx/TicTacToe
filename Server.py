"""
This is the server-side implementation of a Tic Tac Toe game.
It manages multiple game instances, player connections, and game logic.
"""

# Imports
import json
import socket
import threading
import time

# Define constants
HOST = '127.0.0.1'  # Standard loopback IP address (localhost)
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)
FORMAT = 'utf-8'  # Define the encoding format of messages from client-server
ADDR = (HOST, PORT)  # Creating a tuple of IP+PORT

# Global variable to store games
games = {}
game_id_counter = 1  # A counter to assign unique game IDs

"""
GameThread class manages an individual game instance.
Handles game state, player connections, move validation, and win conditions.
Inherits from threading.Thread to handle multiple games concurrently.
"""
class GameThread(threading.Thread):
    def __init__(self, game_id, creator_conn, creator_addr):
        threading.Thread.__init__(self)
        self.game_id = game_id
        self.creator_conn = creator_conn
        self.creator_addr = creator_addr
        self.num_players = 1
        self.board_size = (self.num_players + 1)  # Board is (x + 1)^2
        self.board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]  # Initialize an empty 3x3 board
        self.players = {
            1: {"conn": creator_conn, "addr": creator_addr, "symbol": self.generate_symbol(0)}
        }
        self.winner=None
        self.game_over=False
        self.turn=1 #first turn is for player 1 the creator of the game
        self.status = 'waiting'  # New attribute to track the game status
        self.game_size=0

    """
    Generates a unique symbol for each player.
    Uses a combination of X, O, and Greek alphabet symbols to ensure
    each player has a distinct marker on the board.
    """
    def generate_symbol(self, player_id):
        # List of Greek symbols starting with "X", "O", "Δ", and continuing with Greek alphabet
        greek_symbols = [
            "X", "O", "Δ", "Λ", "Φ", "Ψ", "Ω", "Π", "Σ", "Θ",  # Starting with "X", "O", and Greek letters
            "Α", "Β", "Γ", "Δ", "Ε", "Ζ", "Η", "Θ", "Ι", "Κ",  # Greek alphabet symbols
            "Λ", "Μ", "Ν", "Ξ", "Ο", "Π", "Ρ", "Σ", "Τ", "Υ",
            "Φ", "Χ", "Ψ", "Ω"
        ]
        # Return the Greek symbol corresponding to the self.num_players
        return (greek_symbols[player_id % len(greek_symbols)])  # Loop over the Greek symbols list

    """
    Adds a new player to the game.
    Updates player count and assigns the new player a unique symbol.
    """
    def add_opponent(self, opponent_conn, opponent_addr):
        self.num_players += 1
        player_id = self.num_players
        #send the player its player id
        player_id=str(player_id)
        opponent_conn.send(player_id.encode(FORMAT))
        print(f"Player {player_id} joined the game.")
        player_id=int(player_id) #casting back to int
        self.players[player_id] = {
            "conn": opponent_conn,
            "addr": opponent_addr,
            "symbol": self.generate_symbol(player_id-1),
        }

    """
    Handles communication with a specific player.
    Processes moves and messages from the player.
    """
    def handle_player(self, player_id):
        conn = self.players[player_id]["conn"]
        while not self.game_over:
            try:
                data = conn.recv(1024).decode(FORMAT)  # Process player moves here
                print(f"Received data from Player {player_id}: {data}")
            except Exception as e:
                print(f"Error communicating with Player {player_id}: {e}")
                break

    """
    Main game thread execution method.
    Handles game initialization, player joining, and starts the game
    when all players have connected.
    """
    def run(self):
        conn = self.creator_conn
        game_size = conn.recv(1024).decode(FORMAT)
        game_size = int(game_size)
        self.game_size = game_size
        #modify self game as per the game size
        self.board = [[" " for _ in range((game_size+1))] for _ in range((game_size+1))]
        print("A new game has been created. Waiting for players...")
        while self.num_players < game_size:  # Inner loop to wait for players
                time.sleep(5)  # Sleep to avoid busy waiting
                print(f"Current players: {self.num_players} / {game_size}")
                num_players = str(self.num_players)
                conn.send(num_players.encode(FORMAT))

        print("All players have joined! The game is starting...")
        self.status = 'in_progress'
        self.start_game()
        print("Game finished.")
        self.notify_players("A player has left.")

    """
    Sends the current board state to all players.
    Formats the board as a string and sends it to each connected player.
    """
    def send_board(self):
        board_state = "\n".join([" | ".join(row) for row in self.board])
        board_message = f"Current Board:\n{board_state}\n"
        for player_id, player in self.players.items():
            conn = player["conn"]
            try:
                conn.send(board_message.encode(FORMAT))  # Send the board as a string
            except Exception as e:
                print(f"Error sending board to Player {player_id}: {e}")

    """
     Receives and processes messages from all players.
     Used to ensure synchronization between players.
     """
    def recv_message(self):
        for player_id, player in self.players.items():
            conn = player["conn"]
            try:
                message = conn.recv(1024).decode(FORMAT)  # Receiving from client message
                print(message)
            except Exception as e:
                print(f"Error sending board to Player {player_id}: {e}")

    """
    Manages the main game loop.
    Handles player turns, move validation, and win condition checking.
    Continues until the game is over (win, tie, or player disconnection).
    """
    def start_game(self):
        print("Game has started successfully.")
        self.send_board()
        self.recv_message()
        self.turn=0
        while(self.game_over==False):
            self.turn = (self.turn % self.game_size) + 1
            message=f"player {self.turn} turn"
            self.notify_players(message)
            player_conn = self.players[self.turn]["conn"]
            turn = player_conn.recv(1024).decode(FORMAT)
            if (turn == 'e'): #disconnect player from server and end the game
                self.notify_players(f"player {self.turn} left the game")
                self.players[self.turn]["conn"].close()
                self.players.pop(self.turn, None)
                self.num_players=self.num_players-1
                self.game_over = True
                break
            turn = turn.strip('()')
            row, col = map(int, turn.split(','))
            self.board[row][col]=self.players[self.turn]["symbol"]
            self.send_board()
            if(self.check_winner()==self.players[self.turn]["symbol"]):
                self.notify_players(f"player {self.turn} won\n")
                self.game_over=True
                break

            if (self.check_winner() == "Tie"):
                self.notify_players("Tie")
                self.game_over = True
                break

    """
    Check if there is a winner in the game.
    Returns:
        str: Symbol of the winner if there is one (e.g., 'X' or 'O'),
             'Tie' if the board is full with no winner,
             False if the game is still ongoing.
    """
    def check_winner(self):
        size = len(self.board)  # Get the size of the board

        # Check rows for a winner
        for row in self.board:
            for start in range(size - 2):
                if row[start] == row[start + 1] == row[start + 2] and row[start] != " ":
                    return row[start]  # Return the winning symbol

        # Check columns for a winner
        for col in range(size):
            for start in range(size - 2):
                if (
                        self.board[start][col] == self.board[start + 1][col] == self.board[start + 2][col]
                        and self.board[start][col] != " "
                ):
                    return self.board[start][col]  # Return the winning symbol

        # Check diagonals (top-left to bottom-right) for a winner
        for row in range(size - 2):
            for col in range(size - 2):
                if (
                        self.board[row][col] == self.board[row + 1][col + 1] == self.board[row + 2][col + 2]
                        and self.board[row][col] != " "
                ):
                    return self.board[row][col]  # Return the winning symbol

        # Check diagonals (top-right to bottom-left) for a winner
        for row in range(size - 2):
            for col in range(2, size):
                if (
                        self.board[row][col] == self.board[row + 1][col - 1] == self.board[row + 2][col - 2]
                        and self.board[row][col] != " "
                ):
                    return self.board[row][col]  # Return the winning symbol

        # Check for a tie (no empty spaces left)
        if all(cell != " " for row in self.board for cell in row):
            return "Tie"  # The board is full with no winner

        # Game is still ongoing
        return False

    """
    Sends a message to all connected players.
    Used for game updates, board states, and game end notifications.
    """
    def notify_players(self, message):
        """
        Send a message to all players.
        The message can be the game board or any other text message.
        """
        for self.num_players, player in self.players.items():
            conn = player["conn"]
            try:
                # Sending the message to the player
                conn.send(message.encode(FORMAT))  # Message must be encoded as bytes
            except Exception as e:
                print(f"Error sending message to player {self.num_players}: {e}")

"""
Creates a new game instance with the given connection and address.
Returns a dictionary containing game information including game_id, creator, and board.
Updates the global games dictionary with the new game instance.
"""
def create_new_game(conn, addr):
    global game_id_counter, games
    game = GameThread(game_id_counter, conn, addr)
    games[game_id_counter] = game
    game_id_counter += 1
    game.start()  # Start the game thread
    return {"game_id": game.game_id, "creator": addr, "board": game.board}

"""
Handles initial client connection and game setup.
Processes requests for creating new games or joining existing ones.
Manages the client's connection state throughout the game.
"""
def handle_client1(conn, addr):
    print('[CLIENT CONNECTED] on address: ', addr)  # Printing connection address
    Choose_Game = conn.recv(1024).decode(FORMAT)  # Receiving from client # of messages to expect
    Choose_Game=int(Choose_Game) #casting to int
    received = 0

    try:
    #case for joining an existing game
       if (Choose_Game==1):
            print(f"The following available game rooms are:\n{games}")
            #send the available games to the client
            time.sleep(0.5)
            available_games = {game_id: game for game_id, game in games.items() if game.status == 'waiting'}
            print(f"The following available game rooms are:\n{list(available_games.keys())}")

            # Check if there are any available games
            if not available_games:
                conn.send("No available games at the moment.".encode(FORMAT))
                return
            available_games_json = json.dumps(list(available_games.keys()))
            conn.send(available_games_json.encode(FORMAT))
            game_id = conn.recv(1024).decode(FORMAT)
            game_id = int(game_id)
            print(f"Client wants to join game {game_id}")
            if game_id in games:
                game = games[game_id]
                game.add_opponent(conn, addr)
            else:
                conn.send("Invalid game ID".encode(FORMAT))


       elif(Choose_Game==2):
           Start_Game = True
           print("Creating a new game")
           game_board = create_new_game(conn, addr) #creates a new game thread


    except:
         print("[CLIENT CONNECTION INTERRUPTED] on address: ", addr)


"""
Initializes and starts the server.
Creates a socket, binds it to the specified address and port,
and listens for incoming connections.
Spawns a new thread for each connected client.
"""
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR)
    server_socket.listen()

    print(f"[LISTENING] server is listening on {HOST}:{PORT}")

    while True:
        try:
            connection, address = server_socket.accept()
            print(f"[NEW CONNECTION] {address} connected.")

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=handle_client1, args=(connection, address))
            client_thread.start()

        except Exception as e:
            print(f"Error accepting connection: {e}")

        # on this process (opening another thread for next client to come!)


# Server initialization code
# Main
if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Opening Server socket

    print("[STARTING] server is starting...")
    start_server()

    print("THE END!")

