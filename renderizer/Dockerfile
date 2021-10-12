# Image used to generate the Dockerfiles from a Go text template.
#
# Build:
#   docker build --rm --pull -t gcr.io/kaggle-images/go-renderizer -f Dockerfile .
#
# Push:
#   docker push gcr.io/kaggle-images/go-renderizer
FROM golang:1.17

RUN go install github.com/gomatic/renderizer/v2/cmd/renderizer@v2.0.13

ENTRYPOINT ["renderizer"]