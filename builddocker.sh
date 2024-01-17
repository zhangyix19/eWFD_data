pushd .devcontainer
docker build -t ewfd-data-env -f Dockerfile.dev .
popd
docker build -t ewfd-data-tor -f Docker/Dockerfile.tor .
