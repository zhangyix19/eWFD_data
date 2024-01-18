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

docker build -t zhangyix19/ewfd-data:data-undefend -f Docker/data/Dockerfile.undefended .
docker push zhangyix19/ewfd-data:data-undefend
