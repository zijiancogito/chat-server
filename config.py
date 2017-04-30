config = {
    'HOST': '127.0.0.1',
    'PORT': 12345,
    'LISTEN_CLIENT': 1000,
    'KEY': '391f10fadc339e9ec5fa15af60030ac1',
    'SIZE': 2048,
    'TIME_OUT': 1000,
    'HEART_TIME': 5,
    'MAGIC_STRING': '258EAFA5-E914-47DA-95CA-C5AB0DC85B11',
    'HANDSHAKE_STRING': "HTTP/1.1 101 Switching Protocols\r\n" \
            "Upgrade:websocket\r\n" \
            "Connection: Upgrade\r\n" \
            "Sec-WebSocket-Accept: {1}\r\n" \
            "WebSocket-Location: ws://{2}/chat\r\n" \
            "WebSocket-Protocol:chat\r\n\r\n"
}
