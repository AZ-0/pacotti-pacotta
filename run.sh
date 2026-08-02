sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
screen -L -d -m python3 -m src $@
/usr/sbin/logrotate -s logrotate.status logrotate.conf
