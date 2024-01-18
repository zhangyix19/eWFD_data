docker build -t ewfd-data-base -f Docker/Dockerfile.base .
docker build -t ewfd-data-tor -f Docker/Dockerfile.tor .
docker build -t ewfd-data-tbb -f Docker/Dockerfile.tbb .
docker tag ewfd-data-base:latest zhangyix19/ewfd-data:base
docker tag ewfd-data-tor:latest zhangyix19/ewfd-data:tor
docker tag ewfd-data-tbb:latest zhangyix19/ewfd-data:tbb
docker tag ewfd-data-tbb:latest zhangyix19/ewfd-data:dev
docker push zhangyix19/ewfd-data:base
docker push zhangyix19/ewfd-data:tor
docker push zhangyix19/ewfd-data:tbb
docker push zhangyix19/ewfd-data:dev

docker build -t zhangyix19/ewfd-data:data-undefend-cw -f Docker/data/undefend/Dockerfile.cw .
docker build -t zhangyix19/ewfd-data:data-undefend-ow -f Docker/data/undefend/Dockerfile.ow .
docker push zhangyix19/ewfd-data:data-undefend-cw
docker push zhangyix19/ewfd-data:data-undefend-ow
