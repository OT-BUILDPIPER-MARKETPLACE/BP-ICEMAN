FROM python:slim-buster AS builder

WORKDIR /opt/

COPY . .

RUN apt-get update && \
    apt-get install -y binutils libc-bin

RUN mkdir -p /ot/logs /ot/config && \
    pip3 install --no-cache --upgrade -r requirements.txt

RUN pyinstaller --paths=lib scripts/schedule_resources.py --onefile


FROM gcr.io/distroless/python3-debian11 AS deployer

COPY --from=builder /ot /ot

WORKDIR /ot

COPY --from=builder /opt/dist/schedule_resources .

ENTRYPOINT ["./schedule_resources"]
