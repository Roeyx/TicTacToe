# Tic Tac Toe Game

This project is a server-client implementation of a Tic Tac Toe game. It supports multiple game instances and player connections, enabling concurrent gameplay.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Gameplay](#gameplay)
- [Networking Details](#networking-details)
- [Contributing](#contributing)

## Features

- Multi-player support
- Concurrent game instances
- Reliable game state synchronization
- Player disconnection handling
- Flexible game board size

## Requirements

- Python 3.x

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/tic-tac-toe.git
    cd tic-tac-toe
    ```
2. No additional packages are required as the implementation uses Python's standard libraries.

## Usage

### Server

1. Start the server:
    ```bash
    python server.py
    ```

### Client

1. Start the client:
    ```bash
    python client.py
    ```
2. Follow the prompts to either join an existing game or create a new one.

## Gameplay

1. **Create a New Game**:
    - When prompted, press `2` to create a new game.
    - Enter the number of players for the game.
    - Wait for other players to join.
    - Once all players are connected, the game will start.

2. **Join an Existing Game**:
    - When prompted, press `1` to join an existing game.
    - If there are available games, enter the game ID you want to join.
    - Wait for other players to connect if the game is not full.
    - Once all players are connected, the game will start.

3. **Playing the Game**:
    - Players take turns to make their moves.
    - Enter your move in the format `(row,col)`.
    - The game continues until a player wins or the game ends in a tie.
    - Players can exit the game by pressing `e`.

## Networking Details

### Client-Server Architecture

- **Host**: `127.0.0.1` (loopback address for local testing)
- **Port**: `5000`
- **Protocol**: TCP (Transmission Control Protocol)

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create your feature branch:
    ```bash
    git checkout -b feature/YourFeature
    ```
3. Commit your changes:
    ```bash
    git commit -m 'Add some feature'
    ```
4. Push to the branch:
    ```bash
    git push origin feature/YourFeature
    ```
5. Open a pull request.
