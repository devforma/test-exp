from huangzherui/open-engine:latest

RUN pip3 install osm2gmns requests

ENV cityname=nanchang north=30.2601 south=30.2415 east=120.1828 west=120.1536

CMD ["./main.sh"]