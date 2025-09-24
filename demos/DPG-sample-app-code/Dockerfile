FROM  golang:1.17.0-buster as builder
LABEL maintener="anshul.singh@thalesgroup.com"
WORKDIR /app
COPY . .
FROM builder as build
RUN go build -o dpgupstreamserver .

FROM ubuntu:20.04
COPY --from=build /app  .

EXPOSE 8081
CMD ["./dpgupstreamserver"]
