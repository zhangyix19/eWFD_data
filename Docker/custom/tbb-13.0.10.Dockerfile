FROM --platform=linux/amd64 zhangyix19/ewfd-data:base

USER root
SHELL ["/bin/bash", "-c"]

WORKDIR /work
# geckodriver
RUN wget https://dist.torproject.org/torbrowser/13.0.10/geckodriver-linux-x86_64-13.0.10.tar.xz
RUN tar -xf geckodriver-linux-x86_64-13.0.10.tar.xz && rm geckodriver-linux-x86_64-13.0.10.tar.xz
RUN echo "export PATH=\$PATH:$PWD" >> /root/.bashrc
# tor-browser
RUN wget https://dist.torproject.org/torbrowser/13.0.10/tor-browser-linux-x86_64-13.0.10.tar.xz
RUN tar -xf tor-browser-linux-x86_64-13.0.10.tar.xz && rm tor-browser-linux-x86_64-13.0.10.tar.xz

CMD ["/bin/bash"]