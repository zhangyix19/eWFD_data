docker build -t ewfd-data-base -f Docker/Dockerfile.base .
docker build -t ewfd-data-tor -f Docker/Dockerfile.tor .
docker build -t ewfd-data-data -f Docker/Dockerfile.data .
docker tag ewfd-data-base:latest zhangyix19/ewfd-data:base
docker tag ewfd-data-tor:latest zhangyix19/ewfd-data:tor
docker tag ewfd-data-data:latest zhangyix19/ewfd-data:data
docker tag ewfd-data-data:latest zhangyix19/ewfd-data:dev
docker push zhangyix19/ewfd-data:base
docker push zhangyix19/ewfd-data:tor
docker push zhangyix19/ewfd-data:data
docker push zhangyix19/ewfd-data:dev
