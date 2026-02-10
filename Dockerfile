FROM ubuntu:latest
LABEL authors="krsti"

ENTRYPOINT ["top", "-b"]