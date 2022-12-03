import re
import tkinter as tk
from tkinter import messagebox
from netmiko import ConnectHandler

ip_pat = r"\d{1,4}\.\d{1,4}\.\d{1,4}\.\d{1,4}"
mac_pat = r"[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}"
mac_pat2 = r"[a-f0-9]{4}.[a-f0-9]{4}.[a-f0-9]{4}.[a-f0-9]{4}"
groups_macT=r"\s*?\d\s+[a-f0-9]{4}\.[a-f0-9]{4}\.[a-f0-9]{4}\s+\w+\s+((Fa|Gi)\d{1,2}\/\d{1,2}\/?(\d{1,2})?)"
local_int=r"Interface:\s*(.*),(.*):\s*(.*)"

sh_macaddT = "show mac address-table | in "
sh_cdpn_det = "show cdp neighbors detail"
sh_hostname = "show running-config | include hostname"



def COMPROVAR_FORMATO(var,patron):
    formato = re.compile(patron)
    revisar = formato.search(var)
    if revisar == None:
        messagebox.showinfo(message="Formato incorrecto para la Mac, Ejemplo: XX-AA-YY-00-DD-FF", title="ERROR")
        return revisar
    else:
        return revisar.group()

#####

def FIND_MAC(mac,connect):
    
    MACtable = connect.send_command(sh_macaddT + mac)
    formato=re.compile(groups_macT)
    revisar = formato.search(MACtable)
    if revisar != None:
        port = revisar.group(1)
        print("Esa mac la veo por el puerto: ",port)
        
    else:
        #print("!!! Esa mac no existe en esta red !!!")
        messagebox.showinfo(message="That mac address doesn't exist on the network", title="ERROR")
        return None
    
    CDPneighborsDet= connect.send_command(sh_cdpn_det)
    CDPneighborsDet_list = CDPneighborsDet.split('\n')

    allIPs = []  
    for element in CDPneighborsDet_list:
        if "IP address:" in element:
            allIPs.append(element)
    IPs = []
    [IPs.append(i) for i in allIPs if i not in IPs]
    print(IPs)

    allInt = []
    for element in CDPneighborsDet_list:
        if "Interface: " in element:
            allInt.append(element)

    INTs=[]
    for element in allInt:
        formato=re.compile(local_int)
        revisar = formato.search(element)
        INTs.append(revisar.group(1))

    i=0
    for element in INTs:     
        formato=re.compile(r"(Fa|Gi)[a-zA-Z]*([0-9]+\/[0-9]+\/?[0-9?]+)")
        revisar=formato.search(element)
        INTs[i]=revisar.group(1)+revisar.group(2)
        i+=1
        
    if port in INTs:
        
        connect.disconnect()
        
        p=INTs.index(port)
        ip = IPs[p]
        formato = re.compile(ip_pat)
        revisar = formato.search(ip)
        ip = revisar.group()

        Device={
            "host":ip,
            "username":"cisco",
            "device_type":"cisco_ios",
            "secret":"cisco",
            "password":"cisco",
            }
        try:
            connection = ConnectHandler(**Device)
            connection.enable() 
        except:
            #print(" !!! NO SE LOGRO LA CONECCION !!")
            messagebox.showinfo(message="Failed to connect to the host", title="ERROR")
            return None
        
        FIND_MAC(mac, connection)
    else:
        Hostname = connect.send_command(sh_hostname)
        formato=re.compile(r"hostname (.*)")
        revisar=formato.search(Hostname)
        RES.set("The host is in "+revisar.group(1)+", in the port "+port)
        return None
        


#####    
  
def MAIN_CODE():
    
    while True:
        mac = MAC.get()
        ip = IP.get()
        user = USER.get()
        passw = PASS.get()

        mac=mac.lower()
        
        mac_serch = COMPROVAR_FORMATO(mac,mac_pat)

        if  mac_serch != None:
            mac_serch = mac_serch.replace("-","")
            mac_serch = mac_serch.replace(".","")
            mac_serch = mac_serch.replace(":","")
            mac_serch = list(mac_serch)
            mac_serch.insert(4,".")
            mac_serch.insert(9,".")
            mac_serch = "".join(mac_serch)
            
            try:
                Device={
                    "host":ip,
                    "username":user,
                    "device_type":"cisco_ios",
                    "secret":passw,
                    "password":passw,
                    }
                net_connect = ConnectHandler(**Device)
                net_connect.enable()
                print("CONNECTED")
            except:
                messagebox.showinfo(message="Connection error, wrong data (ip, username, or password)", title="ERROR")
                break
            fin = FIND_MAC(mac_serch, net_connect)
            
            if fin == None:
                break

        else:
            break

###ventana principal
ventana=tk.Tk()
ventana.title("Inicio")
ventana.geometry("756x653+300+100")
ventana.resizable(width=False,height=False)
fondo=tk.PhotoImage(file="C:\\Users\\Paloma\\Documents\\fondo.png")
fondo1=tk.Label(ventana, image=fondo).place(x=0,y=0,relwidth=1,relheight=1)

###colores
color_btn="#00A1E1"
color_txt="#EBEFF1"

###variables
MAC = tk.StringVar()
IP = tk.StringVar()
USER = tk.StringVar()
PASS = tk.StringVar()
RES = tk.StringVar()

###botones y cuadros de texto de ventana principal
btn_Main=tk.Button(ventana,text="SEARCH HOST",bg=color_btn,width=40,height=2,relief="flat",command=MAIN_CODE)
btn_Main.place(x=70,y=490)

txt_MAC=tk.Entry(ventana, textvariable=MAC,width=40,bg=color_txt)
txt_MAC.place(x=400,y=222)

txt_IP=tk.Entry(ventana, textvariable=IP,width=40,bg=color_txt)
txt_IP.place(x=400,y=290)

txt_USER=tk.Entry(ventana, textvariable=USER,width=40,bg=color_txt)
txt_USER.place(x=400,y=358)

txt_PASS=tk.Entry(ventana, textvariable=PASS,width=40,bg=color_txt)
txt_PASS.place(x=400,y=415)

lbl_RES=tk.Label(ventana,textvariable=RES,width=40,height=4)
lbl_RES.place(x=400, y=490)

btnSalir=tk.Button(ventana,text="Close",bg=color_btn,width=20,height=2,relief="flat",command=ventana.destroy)
btnSalir.pack(pady=10,side=tk.BOTTOM)


ventana.mainloop()



