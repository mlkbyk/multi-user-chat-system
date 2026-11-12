import socket
import threading 
import datetime
import logging 
from websocket_server import WebsocketServer
import sys
#Hocam fonksiyonları tanımlarken doc string kullanmayı genel olarak tercih ediyorum. Sonra herhangi bir şeyin içinde kullanırken daha kolay olacağını dşündüğüm için.
host="127.0.0.1"
port=38388
successfull_messeage_no=0
m_port=9753#web socket port
if len(sys.argv)>1:
    host=sys.argv[1]
if len(sys.argv)>2:
    port=int(sys.argv[2])
if len(sys.argv)>3:
    m_port=int(sys.argv[3])
relay_port=38389
if len(sys.argv)>4:
    relay_port=int(sys.argv[4])

       
ws_server=WebsocketServer(host=host,port=m_port)#web socket server created for showing logs and online users.
logging.basicConfig(#it 
 filename='chat.log',
 level=logging.INFO,format='%(asctime)s->> %(message)s',
 encoding='utf-8',
 force=True

)


online_users={}#Create a user dictinary for checking who is online or offline.
cncr_lock=threading.Lock() #If two person want to reach with same name or same data need lock control.
sc_lock=threading.Lock()#Just one things write to socket.
def validNameChecker(name):
    """User name checking function"""
    if len(name)==0 or len(name)>21:
        return False
    for c in name:
        if c in "|,/":
            return False
    return True

def nameControl(name):
    """Control name is valid or not"""
    if name in online_users:
        i=1
        s_i=str(i)
        new_name=name+s_i
        while new_name in online_users:
            i+=1
            s_i=str(i)
            new_name=name+s_i
        return new_name
    else:
        return name

         
s_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
def packet_sender(target,code,messeage):
    """Send packet to target with code and messeage."""
    time=datetime.datetime.now().strftime("%H:%M:%S")
    fomatted_packet=f"{code}|{time}|{messeage}\n"
    try:
        with sc_lock:
            target.sendall(fomatted_packet.encode("utf-8"))
    except:
        pass

def list_online_users():
    """Send onlineusers list to the target."""
    with cncr_lock:
        online_users_list=", ".join(online_users.keys())
        for x in online_users:
            packet_sender(online_users[x],"6",f"Online users: {online_users_list}")

def log_and_show(type,sender,target,ms,is_increase):
    """Creates log file and show websockets."""
    global successfull_messeage_no
    time=datetime.datetime.now().strftime("%H:%M:%S")

    with cncr_lock:
        if is_increase==True:
            successfull_messeage_no+=1
        online_user_no=len(online_users)

        try:

            logging.info(f"Time:{time} Type:{type} Sender:{sender} Target:{target} Message:{ms} Detail:{ms}")
        except Exception as err:
            print(f"Log erorr: {err}")
    ws_ms=f"{time}/{type}/{sender}/{target}/{ms}/{online_user_no}/{successfull_messeage_no}"
    try:
        ws_server.send_message_to_all(ws_ms)
    except Exception as err:
        print(f"Web socket error :{err}")
        pass
def log_show_error(e_sock,name,text):
    """Send error information to the client and log record."""
    packet_sender(e_sock,"Error",text)
    log_and_show("Error",name,"server",text,False)

def clientController(cli_s_sock,is_relay=False):
    """Function that works with all client.Purpose:Controll all client."""
    messege_times=[]#users message times stored in this list.
    reserved_username=""
    waterpool=""#It used for accumulate messseages

    try:
        while not "\n" in waterpool:
            messeages=cli_s_sock.recv(1024)
            if not messeages:
                return 
            waterpool+=messeages.decode("utf-8")

        nl_index=waterpool.find("\n")
        register_messeage=waterpool[:nl_index]
        waterpool=waterpool[nl_index+1:]
        parts_of_reg=register_messeage.split("|")
        if len(parts_of_reg)<2 or len(register_messeage)>480:
            log_show_error(cli_s_sock,"UK","You are message is so long enter message max 480 chacter.")
            return
        choice=parts_of_reg[0]
        register_name=parts_of_reg[1]
        if not register_name:
            log_show_error(cli_s_sock,"UK","User name is empty.User name cannot be empty.")
            return

        if  choice=="1"and not is_relay:
            if register_name.startswith("*"):
                log_show_error(cli_s_sock,"UK","user name cannot start with *.")
                return 
            
        elif choice=="1R" and is_relay:
            if not register_name.startswith("*"):
                register_name="*"+register_name
        else:
            log_show_error(cli_s_sock,"UK","Enter correct choice.Choice must be 1 or 1R.")
            return

        if not validNameChecker(register_name):
            log_show_error(cli_s_sock,"UK","Enter valid name(lenght:0-21) and connot start with |")
            return
        
        with cncr_lock:
            reserved_username=nameControl(register_name)
            online_users[reserved_username]=cli_s_sock
            packet_sender(cli_s_sock,"1",f"Username {reserved_username} register.")
            for x in online_users:
                packet_sender(online_users[x],"2",f"{reserved_username} joined to the chat.")
        log_and_show("Register",reserved_username,"Server","User registed.",False)
        list_online_users()
                
        while True:
            if "\n" not in waterpool:
                rem_messeages=cli_s_sock.recv(1024)
                if not rem_messeages:
                    print("No messeages here.")
                    break
                waterpool=waterpool+rem_messeages.decode("utf-8")

            while "\n" in waterpool:
                id_w=waterpool.find("\n")
                messeage=waterpool[:id_w]
                waterpool=waterpool[id_w+1:]

                p_id=messeage.find("|")
                if p_id!=-1:
                    choice=messeage[:p_id]
                    msg_body=messeage[p_id+1:]
                    parts_of_messeage=[choice,msg_body]
                else:
                    choice=messeage
                    parts_of_messeage=[choice]

                if len(messeage)>480:
                    log_show_error(cli_s_sock,reserved_username,"Message is so long.Max:480 ch.")
                    continue

                if choice not in["2","3","4","5"]:
                    log_show_error(cli_s_sock,reserved_username,"You enrted unvalid number.Choose valid number.")
                    continue
                if choice in ["2","3","4"] and (len(parts_of_messeage)<2 or parts_of_messeage[1].strip()==""):
                    log_show_error(cli_s_sock,reserved_username,"You enterrect uncorrect message.Enter corret message")
                    continue

                if choice=="2" or choice=="3":
                    now=datetime.datetime.now()
                    new_times=[]
                    for tim in messege_times:
                        if ((now - tim).total_seconds() <6):
                            new_times.append(tim)

                    messege_times=new_times
                    if len(messege_times)>=3:
                        packet_sender(cli_s_sock,"Error","You try to send  many messages!Please wait 6 second")
                        log_and_show("Limation_Of_Messeage",reserved_username,"Server","User try to send many messages.",False)
                        continue
                    messege_times.append(now)    

                if choice=="2":#general messeage
                    gen_messeage=parts_of_messeage[1]
                    
                    print(f"{reserved_username}: {gen_messeage}")
                    with cncr_lock:
                        for x in online_users:
                            packet_sender(online_users[x],"2",f"General messeage from {reserved_username}: {gen_messeage}")
                    log_and_show("General",reserved_username,"All users",gen_messeage,True)
                
                if choice=="3":#private messeage
                    private_message=parts_of_messeage[1]
                    p_id2=private_message.find("|")
                    if p_id2!=-1:
                        private_parts=[private_message[:p_id2],private_message[p_id2+1:]]
                    else:
                        private_parts=[private_message]


                    if len(private_parts)<2 or not  private_parts[0] or private_parts[1].strip()=="":
                        log_show_error(cli_s_sock,reserved_username,"You entered uncorrect message style.Enter correct message style.")
                        continue


                    target_username=private_parts[0]
                    private_messeage=private_parts[1]
                    found_a_user=False
                    with cncr_lock:
                        if target_username in online_users:
                            found_a_user=True
                            packet_sender(online_users[target_username],"3",f"Private messeage from {reserved_username}: {private_messeage}")
                            if target_username!=reserved_username:
                                packet_sender(cli_s_sock,"3",f"Private messeage to {target_username}: {private_messeage}")
                    
                    if found_a_user:
                        log_and_show("Private",reserved_username,target_username,private_messeage,True)
                    else:
                        log_show_error(cli_s_sock,reserved_username,f"User {target_username} not here.")
                    

                if choice=="4":#change name
                    new_username=parts_of_messeage[1]
                    if new_username.startswith("*") or not validNameChecker(new_username):
                        log_show_error(cli_s_sock,reserved_username,"Username cannot be empty or starts with *.")
                    else:
                        if is_relay:
                            new_username="*"+new_username
                        with cncr_lock:
                            if reserved_username in online_users:
                                del online_users[reserved_username]
                            reserved_username=nameControl(new_username)
                            online_users[reserved_username]=cli_s_sock
                        packet_sender(cli_s_sock,"4",f"Username changed to {reserved_username}.")
                        log_and_show("Change Name",reserved_username,"Server",f"Username changed to {reserved_username}.",False)
                        list_online_users()
                if choice=="5":
                    return#disconect

    except Exception as Error:
        print(f"Error happen:{Error}")
    finally:
        if reserved_username !="": 
            with cncr_lock:
                if reserved_username in online_users:
                    del online_users[reserved_username]
                for y in online_users:
                    packet_sender(online_users[y],"2",f"{reserved_username} left chat.")
            log_and_show("Disconect",reserved_username,"Server","User disconected.",False)
            list_online_users()   
        cli_s_sock.close()

r_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
def relayListener():
    """Connections controller for relay posts"""
    while True:
        r_cli_sock,r_adrees=r_sock.accept()
        r_Threat=threading.Thread(target=clientController,args=(r_cli_sock,True))
        r_Threat.start()



try:#socket control
    s_sock.bind((host,port))
    s_sock.listen()
    r_sock.bind((host,relay_port))
    r_sock.listen()
    rr_threat=threading.Thread(target=relayListener,daemon=True)
    rr_threat.start()
    ws_Threat=threading.Thread(target=ws_server.run_forever,daemon=True)
    ws_Threat.start()
    while True :
        cli_s_sock,conn_s_adress=s_sock.accept()
        threading.Thread(target=clientController, args=(cli_s_sock,)).start()
    
except Exception as Error:#socket creation error
    print("Socket cannot created succesfully.")                        





                    

                
            









     
                
                


        






