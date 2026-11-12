import socket
import threading 
import datetime
import sys
host="127.0.0.1"
port=38388
cli_sock=None
gui_sender=None
if len(sys.argv)>1:
    host=sys.argv[1]
if len(sys.argv)>2:
    port=int(sys.argv[2])

def gui_notifaction(code, message):
    """Send information about error and closed server to the GUİ"""
    if gui_sender:
        now=datetime.datetime.now().strftime("%H:%M:%S")
        gui_sender(code,now,message)


def sendPacket(code,messeage,target=""):
    """Send packet function for client. Returns True if packet sends otherwise return False."""
    if cli_sock==None:
        gui_notifaction("Error","No connection to the Server")
        return False

    if target=="":
        packet=f"{code}|{messeage}\n"
    else:
        packet=f"{code}|{target}|{messeage}\n"
    try:
        cli_sock.sendall(packet.encode("utf-8"))
        return True
    except:
        gui_notifaction("Eror","Message wasnot send.")
        return False
    

def connectServer(name,server_ip=host,server_port=port):
    """Connect server with given port number."""
    global cli_sock
    try:
        cli_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        cli_sock.connect((server_ip, int(server_port)))
        sendPacket("1",name)
        sr_Threat=threading.Thread(target=listenMessage,args=(cli_sock,),daemon=True)
        sr_Threat.start()
        return True
    except Exception:
        cli_sock=None
        gui_notifaction("Closed","No connect to the server.")
        return False

def listenMessage(sock):
    """Listen messages from server."""
    waterpool=""
    while True:
        try:
            comming_message=sock.recv(1024)
            if not comming_message:
                if cli_sock!=None:
                    gui_notifaction("Closed","Server is closed already.")
                return

            waterpool+=comming_message.decode("utf-8")

            while "\n" in waterpool:
                nl_id=waterpool.find("\n")
                part_messeage=waterpool[:nl_id]
                waterpool=waterpool[nl_id+1:]

                p1=part_messeage.find("|")
                if p1==-1:
                    continue
                code=part_messeage[:p1]
                rem=part_messeage[p1+1:]

                p2=rem.find("|")
                if p2==-1:
                    continue
                time=rem[:p2]
                messeage=rem[p2+1:]
                print(f"{time}, {code}, {messeage}\n")
                if gui_sender:
                    gui_sender(code,time,messeage)

        except:
            if gui_sender:
                gui_sender("Error","...","Connection Error WİTH server and client.")
            break


def sendGenMessage(message):
    """Send messages to everyone"""
    sendPacket("2",message)

def sendprivateMessage(target,messeage):
    """Send spesific message to spesific target."""
    sendPacket("3",messeage,target)

def changeUsername(new_user_name):
    """For changing the user name."""
    sendPacket("4",new_user_name)

def dissconnect():
    """Tell server we are leaved and close to the socket"""
    global cli_sock
    if cli_sock!=None:
        try:

            sendPacket("5","Disconnected")
            cli_sock.close()
        except:
            pass
        cli_sock=None

   









