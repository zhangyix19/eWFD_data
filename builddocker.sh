docker build -t zhangyix19/ewfd-data:base -f Docker/Dockerfile.base .
docker build -t zhangyix19/ewfd-data:tor -f Docker/Dockerfile.tor .
docker build -t zhangyix19/ewfd-data:tbb -f Docker/Dockerfile.tbb .

docker push zhangyix19/ewfd-data:base
docker push zhangyix19/ewfd-data:tor
docker push zhangyix19/ewfd-data:tbb

docker build -t zhangyix19/ewfd-data:data-undefend -f Docker/data/Dockerfile.undefended .
docker push zhangyix19/ewfd-data:data-undefend
