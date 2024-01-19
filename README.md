# Usage

```shell
# install docker
curl -fsSL https://test.docker.com -o test-docker.sh
sudo sh test-docker.sh

# undefend
# docker run -itd -v /root/wfpdata:/work/wfpdata --name udefend zhangyix19/ewfd-data:data-undefend run.sh undefend <mode:cw/ow/cw-test/cw-notest> <batch_num>
# close world
docker run -itd -v /root/wfpdata:/work/wfpdata --name udefend zhangyix19/ewfd-data:data-undefend run.sh undefend cw 10 
# open world
docker run -itd -v /root/wfpdata:/work/wfpdata --name udefend zhangyix19/ewfd-data:data-undefend run.sh undefend ow 0.1

```
