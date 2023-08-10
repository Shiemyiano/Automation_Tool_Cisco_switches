import telnetlib
import pandas as pd

def percentages(num1):
    percent = (num1 / 255) * 100
    return percent
def get_info():
    global host, user, password, en_pass, tn , excel_name
    host = input("Enter Switch IP ")
    user = input("Enter your remote_account: ")
    password = input("Enter your Password: ")
    en_pass = input("Enter your enable_Password: ")
    excel_name = input("Enter Excel-Sheet name: ")
def telnet_connect(tn):
    y = tn.read_until(b" : \n", timeout=2).decode('ascii')
    if "login as: " in y:
        tn.write(user.encode('ascii') + b"\n")
        y = tn.read_until(b" : \n", timeout=2).decode('ascii')
        if 'Password:' in y:
            tn.write(password.encode('ascii') + b"\n")
            tn.write("enable".encode('ascii') + b"\n")
            z = tn.read_until(b" Password: \n", timeout=4).decode('ascii')
            if "Password: " in z:
                print('4')
                tn.write(en_pass.encode('ascii') + b"\n")
    elif 'Password:' in y:
        tn.write(password.encode('ascii') + b"\n")
        tn.write("enable".encode('ascii') + b"\n")
        z = tn.read_until(b" Password: \n", timeout=4).decode('ascii')
        if "Password: " in z:
            tn.write(en_pass.encode('ascii') + b"\n")
def get_Basic_Configuration(tn):
    tn.read_until(b"#\n", timeout=2).decode('ascii')
    tn.write(b"terminal length 0\n")
    tn.write(b"sh mac address-table\n")
    #tn.write(b"show running-conf\n")
    return tn.read_until(b"end\n", timeout=2).decode('ascii')
def RxTxLoad(rx_tx_data):
    rx_tx_list = []
    var1 = rx_tx_data.find("rxload")
    var2 = rx_tx_data.find("/" , var1)
    var_rx = rx_tx_data[var1+7: var2]
    #rx_tx_list.append(percentages(var_rx))
    var1 = rx_tx_data.find("txload")
    var2 = rx_tx_data.find("/", var1)
    var_tx = rx_tx_data[var1 + 7: var2]
    rx_tx_list = [percentages(int(var_rx)),percentages(int(var_tx))]
    return rx_tx_list
def get_RX_TX(tn, intPort ):
    tn.read_until(b"#\n", timeout=2).decode('ascii')
    tn.write(b"terminal length 0\n")
    var = "show interface" + intPort + "\n"
    tn.write(b"show interface " + intPort.encode('ascii') + b"\n")
    # tn.write(b"show running-conf\n")
    return tn.read_until(b"end\n", timeout=2).decode('ascii')
def wrang_basic_config(data):
    start = data.find("Vlan")
    end = data.find("Total")
    data = data[start:end]
    return data
def str_to_df(BasicConf):
    confList = BasicConf.splitlines()
    del confList[0:1]
    df = pd.DataFrame(columns=['Vlan' , 'Mac Address' , 'Type' , 'INT'],
                 data=[row.split() for row in confList[1:]])
    df = df[df["INT"].str.contains("CPU") == False]
    del df["Type"]
    #Output = list(map(lambda x: x.split(';'), confList))
    #df = pd.DataFrame(Output)
    df = df.reset_index()
    del df["index"]
    return df


if __name__ == "__main__":
    #The function below for interaction with user to get basic data to collect data
    get_info()

    #start connection with switch using telnet protcol using Telnet packages
    #Note that i made host global from pervious function
    tn = telnetlib.Telnet(host)
    telnet_connect(tn)
    #we collect basic data from switch like INT, MAC, Vlan
    basic_conf = get_Basic_Configuration(tn)
    # clean data to be ready for required data
    #BasicConf after remove all unnecessary data from basic_conf
    BasicConf = wrang_basic_config(basic_conf)
    #convert string into dataframe using pandas
    df = str_to_df(BasicConf)
    RxTx = []
    #get Rx and Tx load and assign to df that we created
    for i in df['INT']:
        RxTx.append(RxTxLoad(get_RX_TX(tn, i)))

    df = df.assign(Rx_Load=[i[0] for i in RxTx])
    df = df.assign(Tx_Load=[i[1] for i in RxTx])

    #finally store data in excel 
    df.to_csv(excel_name  + '.csv')
    print(df)