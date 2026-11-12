# Multi-User Chat System (Project 02)

## 1. Project Structure
- `chat_server.py`: Main TCP chat server, relay listener, and WebSocket broadcast server.
- `client.py`: Module which performs all TCP socket related tasks for the client as well as message transmission and reception.
- `chat_client.py`: Tkinter based GUI client which uses the `client.py` module.
- `chat_relay.py`: Optionally running relay server which sits between the client and the main server, adds the `*` prefix to the usernames.
- `monitor.html`: Webpage to view live server logs and counters via WebSocket.
- `chat.log`: Text file where all server activity such as connections, disconnections, messages, exceptions, and rate limiting is logged.

## 2. Installation and Dependencies
In addition to the Python 3 standard library packages (`socket`, `threading`, `tkinter`, `logging`, `datetime`, `queue`) this project uses only one third-party package, which is `websocket-server`.

To install the necessary dependency execute the following command in the terminal:
```bash
pip install -r requirements.txt
```

## 3. Sequence for Starting Up Components and Examples of Commands
In order to start up your system correctly, here is the order that you should start your components:

**Step 1: Start the Primary Chat Server**
```bash
python chat_server.py
```
(Command line arguments for IP and ports:python chat_server.py 127.0.0.1 38388 9753 38389)
**Step 2: Start the Relay Server (Optional)
Should you want to test connections using the relay, use the following command:

```bash
python chat_relay.py
```
(With custom arguments: python chat_relay.py 38390 38389 127.0.0.1)

**Step 3: Opening the Live Monitoring Page
To view the monitoring page, double-click "monitor.html" within the project directory to load it on your browser.

(Alternatively, it can be served over HTTP by running python -m http.server 8080 from the terminal and visiting http://127.0.0.1:8080/monitor.html)

**Step 4: Running the Chat Clients
Launch a new terminal window and run the following:

```bash
python chat_client.py
```

You can also use the "+ Open New Client Window" or "+ New Client" buttons available within the client GUI to run multiple clients without opening up new terminal windows.

##4. Configuring Addresses and Ports
With no command line arguments specified, the system will use the following default settings:
Default Host IP: 127.0.0.1
Primary TCP Chat Port (port): 38388 (used when connecting directly from the client)
Server Relay Listening Port (relay_port): 38389 (listening port on chat_server.py that can accept connection from chat_relay.py only)
Relay Client Port: 38390 (listening port on chat_relay.py used by incoming clients)
Monitoring Web Socket Port (m_port): 9753 (pushes live events to monitor.html using ws://127.0.0.1:9753, entirely different from chat ports)

##5. Usage: Private Messaging and Relay Connections Public Message:
Ensure that All (Public) is selected from the user list on the left, type the message, and hit Send or Enter.
Private Messages:Select any user in the Online user list on the left (the label on top of the text box changes to Private to: <nickname>), and then you can send your message.Or simply type /msg <nickname> <message> in the message window.
Connecting to IRC via Relay:On the login page, type your nickname and hit "Connect via Relay (38390)", or type 38390 in the TCP Port window and connect.



##DESİGN NOTES##
Message Application Format and FramingBecause TCP is a streaming protocol, one single call of recv(1024) can return a split message or several messages altogether. In order to cope with it correctly, I made use of the variable waterpool buffer in both server and client parts.
Each packet will be terminated with \n symbol. Input data is accumulated into waterpool until \n symbol appears and handled line by line using while "\n" in waterpool: loop.
Message fields are divided by | symbol. UTF-8 encoding will be used with max message length of 480 symbols.

**Client->Server packets:
1|<nickname>\n -> Registration packet
1R|*<nickname>\n -> Registration request through relay
2|<message>\n -> Public message
3|<recipient>|<message>\n -> Private message
4|<new_nickname>\n -> Rename nickname request
5|Disconnected\n -> Notification of normal disconnection

**Server->Client packets: Formatted as CODE|TIME|MESSAGE\n where codes are:
1 - registration confirmation,
2 - public messages & notifications about connection/disconnection,
3 - private messages,
4 - rename confirmation,
6 - online users list.

**Nickname Management and the * Prefix
Nicknames must not be blank, should not be more than 21 characters long, and must not have |, ,, or / characters such that packet processing is unaffected (validNameChecker).
In case the desired nickname is already in use, the nameControl function starts appending an incrementing number beginning at 1 (ali -> ali1, ali2) until a unique nickname is found.
The direct connection using port 38388 cannot register with * as a prefix. Only chat_relay.py, which uses port 38390, prepends * to valid registration attempts and passes them to the server relay port (38389, is_relay=True) as 1R|*<nickname>.

**Concurrency and Connection Life Cycle
A threading.Thread (clientController) is created for each individual client by the server. The relay listener and WebSocket server are also started using background daemon threads.
Two Lock objects are created to lock shared data structures:
  cncr_lock: Locks the online_users dictionary, nickname registration, and successfull_messeage_no.
  sc_lock: Locks the sendall operations performed in the packet_sender to prevent concurrency problems in outbound messages.
Once the client connection ends (Exit) or the window is closed, the user is deleted from online_users and socket closed. Other users are notified and the updated list is broadcasted in the finally: block.

**Rate-Limit Policy and Logging
Local Log File (`chat.log`):All server activity is recorded in a local text file named `chat.log` created automatically in the same directory where `chat_server.py` is executed[cite: 1]. Using Python's `logging` module, it logs timestamps, event types (`Register`, `General`, `Private`, `Change Name`, `Disconect`, `Error`, `Limation_Of_Messeage`), sender nicknames, target recipients, and message details[cite: 1].
Rate-Limit Policy: Each user thread tracks its recent message timestamps in a `messege_times` list[cite: 1]. A user can send at most **3 messages within 6 seconds** (covering both public and private messages)[cite: 1]. If a 4th message is sent before the 6-second window expires, the server rejects it, sends `"You try to send many messages!Please wait 6 second"` to the client, and records the event in `chat.log` and the WebSocket monitor[cite: 1].
Message Counter: Successful public and private messages increment `successfull_messeage_no` by `1` regardless of the number of recipients[cite: 1]. Rejected messages and system events are excluded from this counter[cite: 1].

