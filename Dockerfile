FROM python:3.5.3
LABEL maintainer="Dhaval Sawlani <dhaval.sawlani@contextgrid.com>"

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5006
# [START CMD]
CMD python -m bokeh serve --disable-index-redirect --num-procs=4 --port=5006 --address=0.0.0.0 dashboard.py
# [END CMD]
