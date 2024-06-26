FROM --platform=linux/amd64 ewfd-data-tbb:latest

USER root
SHELL ["/bin/bash", "-c"]

WORKDIR /work
COPY torrc/torrc.default torrcs/torrc
COPY data_collection data_collection

WORKDIR /work/data_collection
CMD ["/bin/bash","run.sh","tor","cw","10"]