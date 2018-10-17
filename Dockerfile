FROM python:3.5.3
LABEL maintainer="Dhaval Sawlani <dhaval.sawlani@contextgrid.com>"

WORKDIR /usr/src/app

COPY . .

RUN sudo pip install --no-cache-dir -r requirements.txt

EXPOSE 5006

CMD python -m bokeh serve --disable-index-redirect --num-procs=2 --port=5006 --address=0.0.0.0 --allow-websocket-origin=$DASHBOARD_DEMO_DOMAIN dashboard.py