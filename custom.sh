docker build -t zhangyix19/ewfd-data:base -f Docker/Dockerfile.base .
docker build -t zhangyix19/ewfd-data:tbb-13.0.10 -f Docker/custom/tbb-13.0.10.Dockerfile .

docker push zhangyix19/ewfd-data:base
docker push zhangyix19/ewfd-data:tbb-13.0.10

docker build -t zhangyix19/ewfd-data:data-undefend-13.0.10 -f Docker/custom/undefended.Dockerfile .
docker push zhangyix19/ewfd-data:data-undefend-13.0.10
