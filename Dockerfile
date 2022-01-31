FROM python:slim-buster AS builder

WORKDIR /opt/

COPY . .

RUN apt-get update && \
    apt-get install -y binutils libc-bin git

RUN pip3 install --no-cache --upgrade -r requirements.txt

RUN pyinstaller --paths=lib scripts/schedule_resources.py --onefile


FROM opstree/python3-distroless:1.0

COPY --from=builder /opt/dist/schedule_resources .

ENTRYPOINT ["./schedule_resources"]
