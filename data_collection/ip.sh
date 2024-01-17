myip=$(/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:")
eval sed -i 's/myip/${myip}/g' helper/utils.py
routeip=$(route -n | grep UG | cut -d" " -f10)
eval sed -i 's/routeip/${routeip}/g' helper/utils.py