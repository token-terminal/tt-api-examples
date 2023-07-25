# Token Terminal API Example using Python

## Getting started

You can either run this locally or using docker.

### Locally

Install package requirements

```sh
pip install -U pip
pip install -r requirements.txt
```

Go to https://tokenterminal.com/terminal/account/api and copy your API Key. Then start the script to fetch all fees for projects that belong to the Blockchains L1 market sector.

NOTE: Substitute the `API_KEY` w/ your own.

```sh
API_KEY='8aaf76f7-b3cb-4c08-b6e7-8550a1e0541b' python main.py
```

### Docker

Build the image and tag it.

```sh
docker build -t my-tt-api-example .
```

Run the example.

```sh
docker run --rm -it -v /tmp:/tmp -e API_KEY='replace-this-with-your-api-key' my-tt-api-example python main.py
```
