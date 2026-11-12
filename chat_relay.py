import socket
import threading
import sys
import datetime
host="127.0.0.1"
relay_port=38390
server_port=38389
relay_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

if len(sys.argv)>1:
    relay_port=int(sys.argv[1])
if len(sys.argv)>2:
    server_port=int(sys.argv[2])
if len(sys.argv)>3:
    host=sys.argv[3]

def sendError(s,t):
    """Send error information."""
    now=datetime.datetime.now().strftime("%H:%M:%S")
    try:
        s.sendall(f"Error|{now}|{t}\n".encode("utf-8"))
    except:
        pass

def transmission(start,target):
    """Read data and saved."""
    while True:
        try:
            data=start.recv(1024)
            if data==b"":
                break
            target.sendall(data)
        except:
            break

    start.close()
    target.close()

def ClientController(cli):
    waterpool=b""
    try: 
        while b"\n" not in waterpool:
            data=cli.recv(1024)
            if not data:
                cli.close()
                return 
            waterpool+=data
            if len(waterpool)>480:
                sendError(cli,"So long")
                cli.close()
                return
    except:
        cli.close()
        return 

    nl_id=waterpool.find(b"\n")
    first_line=waterpool[:nl_id]
    rest=waterpool[nl_id+1:]#remaining bytes

    text=first_line.decode("utf-8")
    p_id=text.find("|")
    if p_id!=-1:
        parts=[text[:p_id],text[p_id+1:]]
    else:
        parts=[text]
    if len(parts)<2 or parts[0]!="1":
        sendError(cli,"Enter correct message format")
        cli.close()
        return
    name=parts[1]
    if name=="":
        sendError(cli,"Username canot be empty.")
        cli.close()
        return
    if name.startswith("*"):
        sendError(cli,"User name cannot start with *")
        cli.close()
        return
    
    server_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        server_sock.connect((host,server_port))
        new_name="1R|*"+name+"\n"
        new_name=new_name.encode()
        new_name=new_name+rest
        server_sock.sendall(new_name)
    except:
        sendError(cli,"Connection error with server.")
        cli.close()
        server_sock.close()
        return 
    
    th1=threading.Thread(target=transmission,args=(cli,server_sock))
    th2=threading.Thread(target=transmission,args=(server_sock,cli))
    th1.start()
    th2.start()

try:
    relay_sock.bind((host,relay_port))
    relay_sock.listen()
    print("Relay is listening.")

except:
    print("Relay Error")
    sys.exit()

while True:
    cli,adress=relay_sock.accept()
    cli_threat=threading.Thread(target=ClientController,args=(cli,))
    cli_threat.start()



    






     
            




