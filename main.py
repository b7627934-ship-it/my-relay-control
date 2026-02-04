import socket
import time

HOST = "0.0.0.0"
PORT = 6722

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    print("🟢 ממתין לריליי...")

    conn, addr = server.accept()
    conn.settimeout(5)
    print(f"🟢 ריליי מחובר מ־{addr}")
    return conn

conn = start_server()
last_ok = time.time()

try:
    while True:
        try:
            # keep alive – לא משנה איזה, העיקר תעבורה
            conn.sendall(b"11")   # או פקודה ניטרלית אם יש
            last_ok = time.time()
            print(f"✅ חיבור חי – {time.strftime('%H:%M:%S')}")
            time.sleep(10)

        except socket.timeout:
            print("⏳ אין תגובה, אבל החיבור עדיין קיים")

        except Exception as e:
            print("❌ החיבור נפל:", e)
            conn.close()
            conn = start_server()

except KeyboardInterrupt:
    print("סגירה ידנית")
    conn.close()
