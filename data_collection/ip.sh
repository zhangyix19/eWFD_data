myip=$(ifconfig eth0 | awk NR==2 | awk '{print $2}')
eval sed -i 's/myip/${myip}/g' helper/utils.py
