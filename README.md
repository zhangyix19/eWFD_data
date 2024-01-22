# Usage

```shell
# install docker
curl -fsSL https://test.docker.com -o test-docker.sh
sudo sh test-docker.sh

# undefend
# docker run -itd --name undefend -m=1.2G --cpus=1.5 -v /root/wfpdata:/work/wfpdata zhangyix19/ewfd-data:data-undefend bash run.sh undefend <mode:cw/ow/cw-test/cw-notest> <batch_num>
# close world
docker run -itd --name undefend -m=1.1G --cpus=1.5 -v /root/wfpdata:/work/wfpdata zhangyix19/ewfd-data:data-undefend bash run.sh undefend cw 12 
# open world
docker run -itd --name undefend -m=1.1G --cpus=1.5 -v /root/wfpdata:/work/wfpdata zhangyix19/ewfd-data:data-undefend bash run.sh undefend ow 0.1

```
