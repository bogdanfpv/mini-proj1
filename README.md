Premier test sur relay.py minimal:


python3 -m http.server 8000

python3 relay.py 127.0.0.1 8000 9000

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


Test 1 : serveur sur la VM, relai et client sur l’host


VM t1:
ssh dizzy@192.168.122.190
python3 -m http.server 8000

Host t2:
curl http://192.168.122.190:8000/

Host t2:
python3 relay.py 192.168.122.190 8000 9000

Host t3:
curl http://127.0.0.1:9000/


Test 2 : relai sur la VM, serveur et client sur l’host


Host t1:
python3 -m http.server 8000

VM t2:
ssh dizzy@192.168.122.190
python3 relay.py 192.168.122.1 8000 9000

Host t3:
curl http://192.168.122.190:9000/


Test 3 : plusieurs clients en parallèle.

VM t1:
dd if=/dev/zero of=gros bs=1M count=50
sha256sum gros
python3 -m http.server 8000

Host t2:
python3 relay.py 192.168.122.190 8000 9000

Host t3:
for i in 1 2 3 4 5; do
  curl -s --limit-rate 2M http://127.0.0.1:9000/gros | sha256sum &
done; wait

```
[1] 9580
[2] 9582
[3] 9584
[4] 9586
[5] 9588
a712abc4032ac35c6b029b15a567c71e30551f59ce05bdcf94b206d12b35bbfe  -
a712abc4032ac35c6b029b15a567c71e30551f59ce05bdcf94b206d12b35bbfe  -
[1]   Done                    curl -s --limit-rate 2M http://127.0.0.1:9000/gros | sha256sum
[5]+  Done                    curl -s --limit-rate 2M http://127.0.0.1:9000/gros | sha256sum
a712abc4032ac35c6b029b15a567c71e30551f59ce05bdcf94b206d12b35bbfe  -
[2]   Done                    curl -s --limit-rate 2M http://127.0.0.1:9000/gros | sha256sum
a712abc4032ac35c6b029b15a567c71e30551f59ce05bdcf94b206d12b35bbfe  -
[3]-  Done                    curl -s --limit-rate 2M http://127.0.0.1:9000/gros | sha256sum
a712abc4032ac35c6b029b15a567c71e30551f59ce05bdcf94b206d12b35bbfe  -
[4]+  Done                    curl -s --limit-rate 2M http://127.0.0.1:9000/gros | sha256sum
```

Tests relay_cache.py:

python3 -m http.server 8000
python3 relay_cache.py 127.0.0.1 8000 9000

curl -i http://127.0.0.1:9000/
curl -i http://127.0.0.1:9000/

Tests sniffeur:

python3 relay_sniffer.py 127.0.0.1 8000 9002
curl http://127.0.0.1:9002/test-sniffer
cat sniffer.log

Tests censeur:

curl -i http://127.0.0.1:9000/bonjour
curl -i http://127.0.0.1:9000/interdit

Tests enchaînement:

python3 -m http.server 8000
python3 relay_cache.py 127.0.0.1 8000 9001
python3 relay_censeur.py 127.0.0.1 9001 9000

curl -i http://127.0.0.1:9000/README.md
curl -i http://127.0.0.1:9000/interdit

