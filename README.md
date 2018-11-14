# Splash LED RPI

## To use the web

```
pip install -r web-requirements.txt
python3 web.py
======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)
```

### To query the web

```
$ http --form POST localhost:8080/bot  text=Hello
HTTP/1.1 200 OK
Content-Length: 7
Content-Type: text/plain; charset=utf-8
Date: Wed, 14 Nov 2018 11:46:47 GMT
Server: Python/3.6 aiohttp/3.4.4

Copy that

$ http GET localhost:8080/bot
HTTP/1.1 200 OK
Content-Length: 20
Content-Type: application/json; charset=utf-8
Date: Wed, 14 Nov 2018 11:46:57 GMT
Server: Python/3.6 aiohttp/3.4.4

{
    "message": "Hello"
}

$ http GET localhost:8080/bot
HTTP/1.1 404 Not Found
Content-Length: 20
Content-Type: application/json; charset=utf-8
Date: Wed, 14 Nov 2018 11:46:58 GMT
Server: Python/3.6 aiohttp/3.4.4

{
    "error": "Nothing"
}

```

### To run the raspberry pi worker

```
pip install worker-requirements.txt
sudo python3 rpi.py
```
