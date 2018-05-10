# pacmanio

## System Requirements
This system has only been confirmed on OSX (Yosemite 10.10.5, MacOS High Sierra). Other systems may proceed at your own risk. 

Apart from that, you will need Python3 and sudo-level access in your terminal. 

## Usage and Setup (Public Server)

If you would like to join the public pacman.io game: 
- Clone this directory and cd into it.
- Run in a unix shell the command: 
```
./launch_game
```

This will connect you to our Amazon EC2 instance. 
## Usage and Setup (Private Server)

In case you don't want to play with other fun people, you can start your own private server. You will still be able to experience Pacman.io gameplay, but you will not be able to play against other people connected to our public server.

#### Server

To start a server from the main directory, run in a Unix shell the command:

```
$ python server.py <host> <port>
```

where `<host>` is your local area IP address (e.g., 10.252.215.26), and `port` is the port number you would like to use. 

Example: `python server/server.py 10.252.215.26 8090`

However, if you would like to run it locally instead, simply use `''` as your `<host>`, for example `python server/server.py '' 8090`

To find your local area IP address: 
- Go to http://www.whatsmyip.org/more-info-about-you/. On the third line it should say "Internal LAN IP: xx.xxx.xxx.xx". This is the IP address you should use.
- On Mac: Click the Apple Logo > System Preference > Network > Wifi. It should say on the right, "Wi-Fi is connected to Harvard Secure and has the IP address xx.xxx.xxx.xx." That is the IP address you should use.
- On Windows: Click on the Start menu and type cmd. When you see the cmd applications in Start menu panel, click it or just press enter. A command line window will open. Type ipconfig and press enter. You'll see a bunch of information, but the line you want to look for is "IPv4 Address." The number across from that text is your local IP address.

#### Clients

To start a client from the main directory, run in a Unix shell the command:

```
$ python client.py hostname port 
```

where `hostname` is the address of the server that you would like to connect to and `port` is the number of the port. These must match exactly with the host and port number used by the server. 

Example: `python client/client.py 10.252.215.26 8090`

If you are trying to connect locally, `python client/client.py '' 8090`