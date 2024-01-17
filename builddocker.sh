docker build -t ewfd-data-base -f Docker/Dockerfile.base .
docker build -t ewfd-data-tor -f Docker/Dockerfile.tor .
docker build -t ewfd-data-data -f Docker/Dockerfile.data .
