FROM python:slim-buster AS builder

WORKDIR /opt/
COPY . .
RUN apt-get update
RUN apt-get install -y binutils libc-bin
RUN pip3 install --no-cache --upgrade -r requirements.txt
RUN pyinstaller scripts/schedule_resources.py --onefile

FROM python:slim-buster AS deployer
WORKDIR /opt/
RUN mkdir -p config
COPY --from=builder /opt/dist/schedule_resources .
ENTRYPOINT ["./schedule_resources"]


