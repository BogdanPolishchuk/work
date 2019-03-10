from django.shortcuts import render
from django.http import HttpResponse,  JsonResponse
from django.views.generic import View
import paramiko
from multiprocessing import Process, Queue


def fttb_func(request):
    return render(request, 'searching_app/fttb.html')


class DataProcessing:
    # Class is used only to check inputted IP addresses to discard wrong IP and add correct
    def __init__(self):
        self.ip_range_str = ''  # incoming data from fttb.html
        self.bad_ip = {}  # dict for collecting wrong IP
        self.ok_ip = []  # list for collecting correct IP

    def spliter_inp_ip(self, ip_range_str):
        # function is splitting incoming data, return list of string data
        ip_range = ip_range_str.split("\n")
        return ip_range

    def checker_split_ip(self, ip_range):
        # function is checking string data for accordance to correct IP format, return correct and incorrect IP
        for i in ip_range:
            temp_ip = i.split(".")
            if len(temp_ip) == 4:
                try:
                    o1 = int(temp_ip[0])
                    o2 = int(temp_ip[1])
                    o3 = int(temp_ip[2])
                    o4 = int(temp_ip[3])
                    if 0 < o1 <= 255 and 0 <= o2 <= 255 and 0 <= o3 <= 255 and 0 <= o4 < 255:
                        self.ok_ip.append(i)
                    else:
                        print(i, "such IP does not exist")
                        self.bad_ip[i] = "such IP does not exist"

                except ValueError:
                    print(i, "this is not IP")
                    self.bad_ip[i] = "this is not IP"

            else:
                print(i, "too long/short for IP")
                self.bad_ip[i] = "too long/short for IP"

        return self.ok_ip


dp = DataProcessing()


class SessionSSH:
    # Class is used for setting tunnel to terminal server and transmit commands
    def __init__(self):
        self.host = 'X.X.X.X'
        self.user = 'Login'
        self.secret = 'Password'
        self.port = 22
        self.client = paramiko.SSHClient()
        self.stdin = None
        self.stdout = None
        self.stderr = None

    def make_tunel(self):
        # open connection with parameters(template from inet)
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host, username=self.user, password=self.secret, port=self.port)

    def do_command(self, command):
        # function receives SNMP response (string data) from devices
        self.stdin, self.stdout, self.stderr = self.client.exec_command(command)
        rez = '\n'.join(self.stdout.readlines())
        return rez

    def do_command_6250(self, command):
        # function receives SNMP response (string data) from devices, only 6250
        self.stdin, self.stdout, self.stderr = self.client.exec_command(command)
        rez = self.stdout.readlines()
        return rez

    def del_tunel(self):
        self.client.close()


obj_ssh = SessionSSH()


class Manager:
    # Class is used for creating command as variable for "SessionSSH"-function "do_command..."
    def ping_com(self, ip):
        # command: ping network element, return dict {key=IP-adr of net elem., value=ping result}
        com = {}
        com[ip] = "ping -c 2 -W 1 " + ip + " | grep '2 packet' | awk '{print $6}'"
        return com

    def vlan_com(self, ip_sw):
        # command: SNMP request for discover VLAN per port for 24-ports switch,
        # return dict {key=port of net elem., value=SNMP request to get VLAN}
        com1 = {}
        for port in range(1, 25):
            com1[port] = "snmpwalk -v 2c -c My_SNMP_community " + ip_sw + " SNMPv2-SMI::mib-2.17.7.1.4.5.1.1." + str(port) + " | awk '{ print $4 }'"
        return com1

    def vlan_com2(self, ip_sw):
        # command: SNMP request for discover VLAN per port for 48-ports switch,
        # return dict {key=port of net elem., value=SNMP request to get VLAN}
        com15 = {}
        for port in range(1, 49):
            com15[port] = "snmpwalk -v 2c -c My_SNMP_community " + ip_sw + " SNMPv2-SMI::mib-2.17.7.1.4.5.1.1." + str(port) + " | awk '{ print $4 }'"
        return com15

    def vlan_com6250(self, ip_sw):
        # command: SNMP request for discover VLAN per port for 6250,
        # return string
        com20 = "snmpwalk -v 2c -c My_SNMP_community " + ip_sw + " SNMPv2-SMI::enterprises.6486.800.1.2.1.3.1.1.2.1.1.3 | grep 'INTEGER: 1' | awk '{ print (substr($1,54,9))}'"
        return com20

    def type_com(self, ip_sw):
        # command: SNMP request for discover vendor of net. elem.,
        # return string
        com2 = "snmpwalk -v 2c -c My_SNMP_community " + ip_sw + " .1.3.6.1.2.1.1.1 | grep STRING | awk '{ print $4 }'"
        return com2

    def deck_com_all(self, ip_sw, port):
        # command: SNMP request for discover service description,
        # return string
        com_all = "snmpwalk -v 2c -c My_SNMP_community " + ip_sw + " IF-MIB::ifAlias." + port + " | awk '{ print $4 }'"
        return com_all


man = Manager()


def check_ip_adr(request):
    # function is processing AJAX request with inputted data
    if request.GET:
        ip_range_str = request.GET["ip_range"]
        ip_range_R = dp.spliter_inp_ip(ip_range_str)
        ip_range_ok = dp.checker_split_ip(ip_range_R)  # list of correct IP
        print(ip_range_ok)
        print(dp.bad_ip)

        empty_dict = {'': 'too long/short for IP'}
        if (len(ip_range_ok) == 0) and (dp.bad_ip == empty_dict):                             # empty data case
            dp.bad_ip.clear()
            return HttpResponse("empty", content_type='text/html')
        elif (len(ip_range_ok) != 0) and ((dp.bad_ip == empty_dict) or len(dp.bad_ip) == 0):  # only correct IP
            e_rez.multi_flo()
            return HttpResponse("ip", content_type='text/html')
        else:                                                                                 # correct and incorrect IP
            e_rez.multi_flo()
            return HttpResponse("ok", content_type='text/html')

    else:
        return HttpResponse("no", content_type='text/html')


def rez(request):
    # called in cases when incorrect IP addresses are exist
    context = dp.bad_ip
    print('ERROR IP ADDRESSES: ', context)

    return JsonResponse(context)


def clear_data(request):
    # AJAX request, called after process all data, clearing all transmitted and received data
    if request.GET:
        comm = request.GET["push"]
        print(comm)

        if comm == 'clear':
            dp.bad_ip.clear()
            print(dp.bad_ip)
            dp.ok_ip.clear()
            print(dp.ok_ip)
            e_rez.korp_desc.clear()
            print(e_rez.korp_desc)
            return HttpResponse("clear", content_type='text/html')
        else:
            return HttpResponse("no", content_type='text/html')
    else:
        return HttpResponse("no", content_type='text/html')


class EndResult:
    # Class is used for getting final result
    def __init__(self):
        self.korp_desc = {}

    def snmp_disc(self, ip_list):
        # function applies processed data
        obj_ssh.make_tunel()

        for i in ip_list:
            test_ping = obj_ssh.do_command(man.ping_com(i)[i])
            if int(test_ping[0]) == 0:
                print(i, ' - ping OK!')
                man.type_com(i)
                typ = str(obj_ssh.do_command(man.type_com(i)))

                if typ == "S2326TP-EI\n":
                    man.vlan_com(i)
                    description_list = []
                    for p in man.vlan_com(i):
                        vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                        if vlan < 1101:
                            man.deck_com_all(i, str(p+4))
                            desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p+4))))
                            print('HUAWEI(S2326TP-EI): Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                            description = 'HUAWEI(S2326TP-EI): Ethernet-' + str(p) + ' - ' + str(vlan) + ' Service description: ' + str(desc)
                            description_list.append(description)
                        else:
                            pass

                    self.korp_desc[i] = description_list

                elif typ == "D-Link\n":
                    man.vlan_com(i)
                    description_list = []
                    for p in man.vlan_com(i):
                        vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                        if vlan < 1101:
                            man.deck_com_all(i, str(p))
                            desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p))))
                            print('D-Link: Ethernet-' + str(p) + ' -', vlan , ' Service description: ', desc)
                            description = 'D-Link: Ethernet-' + str(p) + ' - ' + str(vlan) + ' Service description: ' + str(desc)
                            description_list.append(description)
                        else:
                            pass
                    self.korp_desc[i] = description_list

                elif typ == "OmniStack\n":
                    man.vlan_com(i)
                    description_list = []
                    for p in man.vlan_com(i):
                        vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                        if vlan < 1101:
                            man.deck_com_all(i, str(p))
                            desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p))))
                            print('Alcatel 6224: Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                            description = 'Alcatel 6224: Ethernet-' + str(p) + ' - ' + str(vlan) + ' Service description: ' + str(desc)
                            description_list.append(description)
                        else:
                            pass
                    self.korp_desc[i] = description_list

                elif typ == "Alcatel-Lucent\n":
                    man.vlan_com6250(i)
                    snmp_ask = obj_ssh.do_command_6250(man.vlan_com6250(i))
                    description_list = []
                    for c in snmp_ask:
                        temp = c.split('.')
                        vlan_a = temp[0]
                        port_a = temp[1][0:4]
                        if int(vlan_a) < 1101 and int(port_a) < 1025:
                            desc = str(obj_ssh.do_command(man.deck_com_all(i, port_a)))
                            print('Alcatel 6250: Ethernet-' + str(int(temp[1][0:4]) - 1000) + ' -', temp[0], ' Service description: ', desc)
                            description = 'Alcatel 6250: Ethernet-' + str(int(temp[1][0:4]) - 1000) + ' - ' + str(temp[0]) + ' Service description: ' + str(desc)
                            description_list.append(description)
                        else:
                            pass
                    self.korp_desc[i] = description_list

                elif typ == "MES3500-24\n":
                    man.vlan_com(i)
                    description_list = []
                    for p in man.vlan_com(i):
                        vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                        if vlan < 1101:
                            man.deck_com_all(i, str(p))
                            desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p))))
                            print('ZyXEL MES3500-24: Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                            description = 'ZyXEL MES3500-24: Ethernet-' + str(p) + ' - ' + str(vlan) + ' Service description: ' + str(desc)
                            description_list.append(description)
                        else:
                            pass
                    self.korp_desc[i] = description_list

                elif typ == "S2352P-EI\n":
                    man.vlan_com2(i)
                    description_list = []
                    for p in man.vlan_com2(i):
                        vlan = int(obj_ssh.do_command(man.vlan_com2(i)[p]))
                        if vlan < 1101:
                            man.deck_com_all(i, str(p + 4))
                            desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p + 4))))
                            print('HUAWEI(S2352P-EI): Ethernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                            description = 'HUAWEI(S2352P-EI): Ethernet-' + str(p) + ' - ' + str(vlan) + ' Service description: ' + str(desc)
                            description_list.append(description)
                        else:
                            pass
                    self.korp_desc[i] = description_list

                elif typ == "S5300-28P-LI-AC\n":
                    man.vlan_com(i)
                    description_list = []
                    for p in man.vlan_com(i):
                        vlan = int(obj_ssh.do_command(man.vlan_com(i)[p]))
                        if vlan < 1101:
                            man.deck_com_all(i, str(p + 4))
                            desc = str(obj_ssh.do_command(man.deck_com_all(i, str(p + 4))))
                            print('HUAWEI(S5300): GigabitEthernet-' + str(p) + ' -', vlan, ' Service description: ', desc)
                            description = 'HUAWEI(S5300): GigabitEthernet-' + str(p) + ' - ' + str(vlan) + ' Service description: ' + str(desc)
                            description_list.append(description)
                        else:
                            pass
                    self.korp_desc[i] = description_list

            else:
                print(i, '- switch has problems or unavailable')
                self.korp_desc[i] = ['Switch has problems or unavailable']

        obj_ssh.del_tunel()

        return self.korp_desc

    def shed_foo(self, ip_l, queue):
        # function takes list IP addresses and processing function and put in queue for using multiprocessing
        queue.put(e_rez.snmp_disc(ip_l))

    def multi_flo(self):
        # function creates processes for each IP address
        list_ip = dp.ok_ip
        num_q = []
        num_p = []
        for i, j in enumerate(list_ip):
            num_q.append(i)
            num_q[i] = Queue()
            num_p.append(i)
            num_p[i] = Process(target=e_rez.shed_foo, args=([j], num_q[i],))
            num_p[i].start()

        for k in range(len(num_p)):
            num_p[k].join()

        for i in range(len(num_q)):
            self.korp_desc.update(num_q[i].get())

        return self.korp_desc


e_rez = EndResult()


if __name__ == '__main__':
    e_rez.multi_flo()


def ok_daata(request):
    # called in cases when correct IP addresses are exist
    context = e_rez.korp_desc
    print("SEND DATA!", context)

    return JsonResponse(context)
