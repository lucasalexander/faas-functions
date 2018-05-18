FROM python:3.6-alpine as faas-pythondev-base
WORKDIR /root/function/
RUN apk add --no-cache --virtual .build-deps build-base libffi-dev python3-dev wget
RUN wget https://github.com/openfaas/faas/releases/download/0.7.9/fwatchdog -P /usr/bin/ -q
COPY function/requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.6-alpine
COPY --from=faas-pythondev-base /root/.cache /root/.cache
COPY --from=faas-pythondev-base /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=faas-pythondev-base /usr/bin/fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

WORKDIR /root/

COPY index.py .
RUN mkdir -p function

RUN touch ./function/__init__.py

WORKDIR /root/
COPY function function

ENV fprocess="python3 index.py"

HEALTHCHECK --interval=1s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]