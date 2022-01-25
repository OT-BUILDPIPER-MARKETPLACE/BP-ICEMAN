FROM python:slim-buster AS builder

WORKDIR /opt/
COPY . .
RUN apt-get update && apt-get install -y binutils libc-bin
RUN mkdir -p config /var/log/ot && pip3 install --no-cache --upgrade -r requirements.txt
RUN pyinstaller scripts/schedule_resources.py --onefile

FROM gcr.io/distroless/python3-debian11 AS deployer
WORKDIR /opt/
COPY --from=builder /opt/dist/schedule_resources .
COPY --from=builder /opt/config .
COPY --from=builder /var/log/ot /var/log/ot
ENTRYPOINT ["./schedule_resources"]
