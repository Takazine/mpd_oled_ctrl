#!/usr/bin/python
#-*- coding: utf-8 -*-
u'''
http://akizukidenshi.com/catalog/c/coled/
'''

''' for volumio2   Pi2   OLED SO1602AW  3.3V I2C 16x2
====== UNIX domain socket ======
sudo apt-get update
sudo apt-get install python-smbus kakasi
'''
import time
import commands
import smbus
import sys
import re
import socket

host = 'localhost'     # localhost
port = 6600            # mpd port
bufsize = 1024

STOP = 0
PLAY = 1
PAUSE = 2
MSTOP = 1    # Scroll motion stop time 

class i2c(object):
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.addr = 0x3c          # OLED i2s address
        self.state = STOP         # state
        self.shift = 0            # Scroll shift value
        self.retry = 20           # retry for initialize
        self.old_line1 = " "      # old str 1
        self.old_line2 = " "      # old str 2
        self.old_vol = " "        # old volume
        self.init()

# initialize OLED 
    def init(self):
        while self.retry > 0:
            try:
                self.bus.write_byte_data(self.addr, 0, 0x0c) # Display ON
                self.line1("Music           ")
                self.line2("  Player Daemon ",0)
            except IOError:
                self.retry = self.retry -1
                time.sleep(0.5)
            else:
                return 0
        else:
            sys.exit()

# mpd version 
    def ver_disp(self, ver):
        ver = ver.replace(r"Music Player Daemon ", "")
        self.line1("MPD Version    ")
        self.line2("        "+ver+"  ",0)
        
# line1 send ascii data 
    def line1(self, str):
        if str != self.old_line1:
            self.old_line1 = str
        else:
            return 0
        try:
            self.bus.write_byte_data(self.addr, 0, 0x80) 
            vv = map(ord, list(str))
            self.bus.write_i2c_block_data(self.addr, 0x40, vv)
        except IOError:
            return -1

# line2 send ascii data and Scroll 
    def line2(self, str, sp):
        try:
            self.bus.write_byte_data(self.addr, 0, 0xA0) 
            self.maxlen = len(str) +MSTOP
            if sp < MSTOP:
               sp = 0
            else:
               sp = sp -MSTOP -1
            if self.maxlen > sp + 16:
                self.maxlen = sp + 16
        
            moji = str[sp:self.maxlen]
            moji = map(ord, moji)
            self.bus.write_i2c_block_data(self.addr, 0x40, moji) 
        except IOError:
            return -1

# Get current song name 
    def song(self):
        self.soc.send('currentsong\n')
        song = self.soc.recv(bufsize)
        song_list = song.splitlines()
#        print song_list

        ar_val = ti_val = na_val = fi_val = ""
        for line in range(0,len(song_list)):
            if song_list[line].startswith(r"Artist: "):
                ar_val = song_list[line]
                ar_val = ar_val.replace(r"Artist: ", "")
                
            if song_list[line].startswith(r"Title: "):
                ti_val = song_list[line]
                ti_val = ti_val.replace(r"Title: ", "")
                
            if song_list[line].startswith(r"Name: "):
                na_val = song_list[line]
                na_val = na_val.replace(r"Name: ", "")
                
            if song_list[line].startswith(r"file: "):
                fi_val = song_list[line]
                fi_val = fi_val.replace(r"file: ", "")
                
        if (ti_val == "") and (na_val == "") and (ar_val == ""):
            song_val = fi_val
        else:
            song_val = ar_val+" : "+ti_val+" "+na_val
        
        song_val = re.escape(song_val)
#        print song_val
        song_val = commands.getoutput('echo ' +song_val+' | kakasi -Jk -Hk -Kk -Ea -s -i utf-8 -o sjis')
        #song_val = commands.getoutput('echo ' +song_val+' | kakasi -Ja -Ha -Ka -Ea -s -i utf-8 -o utf-8')

        return song_val

# Display Control 
    def disp(self):
        self.soc.send('status\n')
        st = self.soc.recv(bufsize)
        st_list = st.splitlines()

        bitr_val = audio_val = time_val = vol_val = state_val = samp_val = bit_val = ""
        
        for line in range(0,len(st_list)):
            
            # Volume
            if st_list[line].startswith(r"volume: "):
                vol_val = st_list[line]
                vol_val = vol_val.replace("volume: ", "")
                vol_val = "%2d" %int(vol_val)
                vol_val = str(vol_val)+' '
            
            # Play status
            if st_list[line].startswith(r"state: "): # stop play pause
                state_val = st_list[line]
                state_val = state_val.replace("state: ", "")
                
            # Plaing time
            if st_list[line].startswith(r"time: "):
                time_val = st_list[line]
                time_val = time_val.replace("time: ", "")
                time_val = re.split(':',time_val)
                time_val = int(time_val[0])
                time_min = time_val/60
                time_sec = time_val%60
                time_min = "%2d" %time_min
                time_sec = "%02d" %time_sec
                time_val = str(time_min)+":"+str(time_sec)
            
            # Bitrate
            if st_list[line].startswith(r"bitrate: "):
                bitr_val = st_list[line]
                bitr_val = bitr_val.replace("bitrate: ", "")
                bitr_val = bitr_val +'k'
            
            # Sampling rate / bit 
            if st_list[line].startswith(r"audio: "):
                audio_val = st_list[line]
                audio_val = audio_val.replace("audio: ", "")
                audio_val = re.split(':',audio_val)
                
                if audio_val[0] == '44100':
                    samp_val = '44.1k'
                elif audio_val[0] == '48000':
                    samp_val = '48k'
                elif audio_val[0] == '88200':
                    samp_val = '88.2k'
                elif audio_val[0] == '96000':
                    samp_val = '96k'
                elif audio_val[0] == '176400':
                    samp_val = '176.4k'
                elif audio_val[0] == '192000':
                    samp_val = '192k'
                elif audio_val[0] == '352800':
                    samp_val = '352.8k'
                elif audio_val[0] == '384000':
                    samp_val = '384k'
                else:
                    samp_val = ''
                    
                if audio_val[1] == 'dsd':
                    samp_val = bitr_val

                bit_val = audio_val[1]+'bit '
                if audio_val[1] == 'dsd':
                    bit_val = '1 bit '

        # stop
        if state_val == 'stop':
            # get IP address
            ad = commands.getoutput('ip route')
            ad_list = ad.splitlines()
            #addr_line = re.search('\d+\.\d+\.\d+\.\d+.$', ad_list[1])
            addr_line = re.search('\d+\.\d+\.\d+\.\d+\s', ad_list[1])
            addr_str = addr_line.group()

        # Volume string
        if self.old_vol != vol_val:
            self.old_vol = vol_val
            self.vol_disp = 5
        else:
            if self.vol_disp != 0:
                self.vol_disp = self.vol_disp -1

        
        # Volume and status for Line1 
        if state_val == 'stop':
            if self.vol_disp != 0:
                self.line1("STOP     Vol:"+vol_val)
            else:
                self.line1("STOP             ")
            self.line2(addr_str+"        ",0)
            self.old_line2 = " "
        elif state_val == 'play':
            if self.vol_disp != 0:
                self.line1("PLAY     Vol:"+vol_val)
            else:
                self.line1("PLAY      "+time_val+"  ")
        elif state_val == 'pause':
            if self.vol_disp != 0:
                self.line1("PAUSE    Vol:"+vol_val)
            else:
                self.line1("PAUSE     "+time_val+"  ")
        
        # music name for Line2 
        if state_val != 'stop':
            song_txt = self.song()
            song_txt = song_txt+' - '+ samp_val+'/'+bit_val+' '
            if song_txt != self.old_line2:
                self.old_line2 = song_txt
                self.shift = 0
                self.line2("                ", 0)
            self.line2(self.old_line2+bitr_val+'bps  ', self.shift)
        
        self.shift = self.shift + 1
        if self.shift > (len(self.old_line2)+8 +MSTOP):
            self.shift = 0


# Soket Communication
    def soket(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((host, port))
        aaa = self.soc.recv(bufsize)

def main():
    oled = i2c()
    netlink = False
    time.sleep(1)
    ver = commands.getoutput('mpd -V')
    ver_list = ver.splitlines()
    oled.ver_disp(ver_list[0])
    time.sleep(2)
    
    while netlink is False:
        ip = commands.getoutput('ip route')
        ip_list = ip.splitlines()
        if len(ip_list) >= 1:
            netlink = True
        else:
            time.sleep(1)

    oled.soket()
    
    while True:
        time.sleep(0.25)
        try:
            oled.disp()
        except socket.error:
            print "socket.error"
            oled.soket()
            time.sleep(1)
        pass

if __name__ == '__main__':
        main()
