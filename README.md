# pacman.io

## System Requirements
This system has only been confirmed on OSX (Yosemite 10.10.5, MacOS High Sierra). Other systems may proceed at your own risk. 

Apart from that, you will need Python3 and sudo-level access in your terminal. 

## Usage and Setup (Public Server)

If you would like to join the public pacman.io game: 
- Clone this directory and cd into it.
- Zoom out of your terminal. You can do this with by pressing CMD- (command and -) on OSX.
- Run in a unix shell the command: 
```
./launch_game
```

A prompt will pop up asking for a password. This is your administrative, sudo-level password. Hit enter, and then this will connect you to our Amazon EC2 instance. We don't have that much AWS credit so it might not be up all the time, in which case you can use the private server below.
## Usage and Setup (Private Server)

In case you don't want to play with other fun people, you can start your own private server by following the instructions below. You will still be able to experience Pacman.io gameplay, but you will not be able to play against other people connected to our public server.

#### Server

To start a server from the main directory, run in a Unix shell the command:

```
$ python server.py <host> <port>
```

where `<host>` is your local area IP address (e.g., 10.252.215.26), and `port` is the port number you would like to use. 

Example: `python server.py 10.252.215.26 8090`

However, if you would like to run it locally instead, simply use `''` as your `<host>`, for example `python server.py '' 8090`

To find your local area IP address: 
- Go to http://www.whatsmyip.org/more-info-about-you/. On the third line it should say "Internal LAN IP: xx.xxx.xxx.xx". This is the IP address you should use.
- On Mac: Click the Apple Logo > System Preference > Network > Wifi. It should say on the right, "Wi-Fi is connected to Harvard Secure and has the IP address xx.xxx.xxx.xx." That is the IP address you should use.
- On Windows: Click on the Start menu and type cmd. When you see the cmd applications in Start menu panel, click it or just press enter. A command line window will open. Type ipconfig and press enter. You'll see a bunch of information, but the line you want to look for is "IPv4 Address." The number across from that text is your local IP address.

#### Clients

To start a client from the main directory, run in a Unix shell the command:

```
$ sudo python client.py hostname port 
```

where `hostname` is the address of the server that you would like to connect to and `port` is the number of the port. These must match exactly with the host and port number used by the server. 

Example: `python client.py 10.252.215.26 8090`

If you are trying to connect locally, you can use `python client.py '' 8090`.

## Protocol Details

The following section is completely unnecessary for enjoying our game. However, if you are interested in learning about the protocol used and/or extending the game for your own use, it may be useful.

Messages sent with our game protocol are constructed as follows: 

- Header, consisting of:
    + (byte) protocol version number
    + (unsigned int) message body length, not including this header. 
    + (byte) operation code
- Additional body of message, as specified for each opcode below. May be empty for some opcodes.

We always send the protocol version number in order to verify that the messages sent / received are compatible. If the version number does not match up, the client will be disconnected, because no communication can be guaranteed to be understood. The body length is necessary to guarantee that the message has been fully received.

### Server-Received Opcodes: 
- '\x01': create_request
    + Payload: Data packet contains UTF-8 encoding of account name to log in to (max 5 chars, padded with ' ' if necessary) to log into.
- '\x02': restart_request
    + Payload: None
- '\x03': move_request
    + Payload: UTF-8 encoding of the player's move, should be a single char.

### Client-Received Opcodes:
- '\x00': general_failure
    + Payload: Failure message (UTF-8 encoded), can be any length.
- '\x01': create_success
    + Payload: The UTF-8 encoding of the account id of the user whose account was just made.
- '\x02': receive_game_state`
    + Payload: Python pickled version of game state sent from server.

