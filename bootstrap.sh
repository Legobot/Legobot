#!/bin/bash
host='irc.legobot.local'

apt-get update && apt-get install -y ngircd openssl
mkdir /ngircd && cd /ngircd
openssl req -newkey rsa:2048 -nodes -keyout ${host}.key  -x509 -days 365 -out ${host}.crt -subj '/CN=irc.legobot.local'
service ngircd stop