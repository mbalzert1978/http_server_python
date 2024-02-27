REQUEST = """\
POST /files/donkey_yikes_humpty_vanilla HTTP/1.1\r
Host: localhost:4221\r
User-Agent: Go-http-client/1.1\r
Content-Length: 52\r
Accept-Encoding: gzip\r
\r
yikes scooby donkey yikes yikes Monkey Horsey humpty\r
""".encode()

ECHO_REQUEST = """\
GET /echo/Horsey/Coo-Horsey HTTP/1.1\r
Host: localhost:4221\r
User-Agent: Go-http-client/1.1\r
Accept-Encoding: gzip\r
\r
\r
""".encode()
