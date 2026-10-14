Premier test sur relay.py minimal:


python3 -m http.server 8000

python3.relay.py 127.0.0.1 8000 9000

curl -v http://127.0.0.1:9000/

```
*   Trying 127.0.0.1:9000...
* Connected to 127.0.0.1 (127.0.0.1) port 9000
> GET / HTTP/1.1
> Host: 127.0.0.1:9000
> User-Agent: curl/8.5.0
> Accept: */*
>
```


