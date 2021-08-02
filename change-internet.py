from multiprocessing import Pool
from subprocess import getstatusoutput
import datetime
import time
import os

sentPkg = 10
maxPkgLoss = 2
avgLatencyExpected = 300
sleep = 20

faixaIPVivo = '15.1'
faixaIPViaTelecom = '51.1'

command = []
command.append(f'/usr/bin/ping -c{sentPkg} 200.147.35.149')
command.append(f'/usr/bin/ping -c{sentPkg} 186.192.90.12')

rt_tables = '''
255     local
254     main
253     default
0       unspec
200     vivo
199     viatelecom
'''

def defineRoutes():
    while True:
        print('while')
        st = getstatusoutput('/sbin/ip route del default')[0] 
        if st != 0:
            break

    getstatusoutput('/sbin/ip route add default via 192.168.15.1')

    getstatusoutput(f'echo "{rt_tables}" > /etc/iproute2/rt_tables')

    getstatusoutput('/sbin/ip route flush table vivo')
    getstatusoutput('/sbin/ip route add default via 192.168.15.1 dev bond0.3 table vivo')
    getstatusoutput('/sbin/ip route add 192.168.48.0/22 dev bond0.5 table vivo')
    getstatusoutput('/sbin/ip route add 192.168.20.0/22 dev bond0.6 table vivo')
    getstatusoutput('/sbin/ip route add 192.168.15.0/24 dev bond0.3 table vivo')
    getstatusoutput('/sbin/ip route add 192.168.51.0/24 dev bond0.4 table vivo')

    getstatusoutput('/sbin/ip rule del fwmark 1 lookup vivo')
    getstatusoutput('/sbin/ip rule del to 192.168.15.0/24 lookup vivo')
    getstatusoutput('/sbin/ip rule del from 192.168.15.0/24 lookup vivo')

    getstatusoutput('/sbin/ip rule add fwmark 1 lookup vivo')
    getstatusoutput('/sbin/ip rule add to 192.168.15.0/24 lookup vivo')
    getstatusoutput('/sbin/ip rule add from 192.168.15.0/24 lookup vivo')


    getstatusoutput('/sbin/ip route flush table viatelecom')
    getstatusoutput('/sbin/ip route add default via 192.168.51.1 dev bond0.4 table viatelecom')
    getstatusoutput('/sbin/ip route add 192.168.48.0/22 dev bond0.5 table viatelecom')
    getstatusoutput('/sbin/ip route add 192.168.20.0/22 dev bond0.6 table viatelecom')
    getstatusoutput('/sbin/ip route add 192.168.15.0/24 dev bond0.3 table viatelecom')
    getstatusoutput('/sbin/ip route add 192.168.51.0/24 dev bond0.4 table viatelecom')

    getstatusoutput('/sbin/ip rule del fwmark 2 lookup viatelecom')
    getstatusoutput('/sbin/ip rule del to 192.168.51.0/24 lookup viatelecom')
    getstatusoutput('/sbin/ip rule del from 192.168.51.0/24 lookup viatelecom')

    getstatusoutput('/sbin/ip rule add fwmark 2 lookup viatelecom')
    getstatusoutput('/sbin/ip rule add to 192.168.51.0/24 lookup viatelecom')
    getstatusoutput('/sbin/ip rule add from 192.168.51.0/24 lookup viatelecom')
    
def getCurrentInternet():
    wc = getstatusoutput('/sbin/ip route list | grep "default" | wc -l')
    if wc == 1:
        st, out = getstatusoutput('/sbin/ip route list | grep "default" | tr -s " " | cut -d" " -f3 | cut -d"." -f3')
        if out != '':
            if out == '15':
                return 'VIVO'
            elif out == '51':
                return 'VIA'
    
    defineRoutes()
    return ''

def changeInternet():
    ret = getCurrentInternet()
    if ret == 'VIA':
        getstatusoutput('/sbin/ip route del default')
        getstatusoutput('/sbin/ip route add default via 192.168.15.1')
    elif ret == 'VIVO':
        getstatusoutput('/sbin/ip route del default')
        getstatusoutput('/sbin/ip route add default via 192.168.51.1')
    else:
        log('As rotas foram redefinidas', [('', '')])

def getStatistic(cmd):
    lines = cmd[1].split('\n')
    
    for i in lines:
        if 'rtt min/avg/max/mdev' in i:
            avgLatency = i.split('=')[1].split('/')[1]
            
        if 'received' in i:
            pkgReceived = i.split(',')[1].strip().split(' ')[0]
    
    return float(avgLatency), int(pkgReceived)

def pathLogsExists():
    path = f'{os.getcwd()}/logs'
    if os.path.exists(path) == False:
        getstatusoutput(f'mkdir {path}')


def log(strr, cmd):
    pathLogsExists()
    datanow = datetime.datetime.now().strftime(r"%d-%m-%Y--%H-%M-%S")
    with open(f'logs/Log-{datanow}.txt', 'w') as f:
        f.write('===== Commands =====\n')
        for y in command:
            f.write(f'{y}\n')
        f.write(f'\n===== Config  =====\n')
        f.write(f'sentPkg: {sentPkg}\nmaxPkgLoss: {maxPkgLoss}\navgLatencyExpected: {avgLatencyExpected}\nsleep: {sleep}\n\n')
        f.write(f'===== Message =====\n{strr}\n')
        for i in cmd:
            f.write(f'\n\n===== Status {i[0]} =====\n')
            f.write(f'=====  Output  =====\n')
            for x in i[1].split('\n'):
                f.write(f'{x}\n')
    

def multiprocess():
    p = Pool()
    commands = p.map(getstatusoutput, 'command')

    statisticAVG = []
    statisticReceived = []

    for cmd in commands:
        if cmd[0] == 0:
            avg, received = getStatistic(cmd)
            statisticAVG.append(avg)
            statisticReceived.append(received)

    return statisticAVG, statisticReceived, commands

def validations(statisticAVG, statisticReceived, cmd):

    qtd = len(statisticAVG)

    str1 = f'Todos os processos retornaram com erro'
    if qtd == 0:
        print(str1)
        log(str1, cmd)
        changeInternet()
        return
    
    else:
        avg = sum(x for x in statisticAVG) / qtd
        str2 = f'A media da latencia foi de {avg}, acima dos {avgLatencyExpected}ms esperados'
        if avg > avgLatencyExpected:
            print(str2)
            log(str2, cmd)
            changeInternet()
            return
    
    pkgReceivedExpected = (sentPkg - maxPkgLoss) * qtd
    received = sum(x for x in statisticReceived)
    str3 = f'Foram perdidos mais do que {maxPkgLoss} pacotes'
    if received < pkgReceivedExpected:
        print(str3)
        log(str3, cmd)
        changeInternet()
        return

def main():
    #print(f'Start: {datetime.datetime.now().strftime(r"%d-%m-%Y--%H-%M-%S")}')
    while True:
        st1, st2, cmd = multiprocess()
        validations(st1, st2, cmd)
        time.sleep(sleep)

main()
