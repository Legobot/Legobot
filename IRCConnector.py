import socket
import ssl
import datetime
import select
import string
import time

def connect(self, isSSL=False):
    if isSSL:
        sock=socket.socket()
        self.connection = ssl.wrap_socket(sock)
    else:
        self.connection = socket.socket()

    self.connection.connect((self.host, self.port))
    if self.hostpw:
        self._send_raw_to_socket("PASS %s\r\n" % self.hostpw)

    iterate_nick = True
    orig_nick = self.nick

    i = 0
    while iterate_nick:
        #TO DO: add functionality to create separate nick, realname, etc
        if i:
            self.nick = orig_nick + "_" + str(i)


        self._send_raw_to_socket("NICK %s\r\n" % self.nick)

        self._send_raw_to_socket("USER %s %s %s :%s\r\n" % (self.nick, self.nick, self.nick, self.nick))

        #read in socket to check if we got somethign like:
        # :ircd2.abc.com 433 * test_nick :Nickname already in use

        t = datetime.datetime.now()
        iterate_nick = False
        read_line = False

        while not read_line and (datetime.datetime.now() - t).total_seconds() < 60:
            if select.select([self.connection],[],[],1.0)[0]:
                readbuffer = self.connection.recv(1024)
                #split into lines
                temp = string.split(readbuffer, "\n")

                #iterate through any lines received
                for line in temp:
                    if len(line.strip(' \t\n\r')) == 0:
                        continue
                    read_line = True

                    if "nick" in line.lower() and "already in use" in line.lower():
                        iterate_nick = True
                        i += 1
                        break
            else:
                time.sleep(.5)


    time.sleep(1)
    for room, pw in self.chans:
        if pw:
            self._send_raw_to_socket("JOIN %s %s\r\n" % room, pw)
        else:
            self._send_raw_to_socket("JOIN %s\r\n" % room)
    self.__listen()
