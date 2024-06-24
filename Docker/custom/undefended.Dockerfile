FROM --platform=linux/amd64 zhangyix19/ewfd-data:tbb-13.0.10

USER root
SHELL ["/bin/bash", "-c"]

WORKDIR /work
COPY torrc/torrc.default torrcs/torrc
COPY data_collection data_collection

WORKDIR /work/data_collection
CMD ["/bin/bash","run.sh","undefend","cw","10"]