#!/usr/bin/env python3
"""The dev server. `python3 -m http.server` with one thing fixed: nothing is ever cached.

    python3 tools/serve.py [port]        # default 8000

Why this exists. `python3 -m http.server` sends `Last-Modified` and no `Cache-Control` at all.
A response with no explicit freshness may be cached HEURISTICALLY — browsers commonly reuse it,
with no revalidation, for about 10% of the file's age. An hour-old page is silently good for six
minutes; a day-old one for over two hours.

That is the whole explanation for the oldest ghost in this project: you edit a song, reload its
page, hear the change — and the ALBUM still plays the old version. The album is a separate URL,
so it has its own cache entry, and it may be an old copy of the hallway with an old iframe
buster inside it. Everything looks correct and sounds wrong.

`Cache-Control: no-store` on every response ends it: the browser keeps nothing, so a reload is
always the truth and "close the tab and hard-refresh" stops being part of the job. Slower than
caching, irrelevant over localhost.
"""
import http.server, sys


class NoStore(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):        # one quiet line, no client address noise
        sys.stderr.write("  %s\n" % (fmt % args))

    def handle_one_request(self):
        # A browser abandons audio/video fetches constantly (it got enough, it seeked, the page
        # went away). That surfaces as BrokenPipe/ConnectionReset — normal here, and not worth a
        # traceback that looks like the server is broken.
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True


class Server(http.server.ThreadingHTTPServer):
    # THREADED, like `python3 -m http.server` — a song page pulls dozens of clips at once, and a
    # single-threaded server makes them queue behind each other until samples arrive late or not
    # at all. This is the whole reason to subclass rather than reuse TCPServer.
    daemon_threads = True
    allow_reuse_address = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with Server(("", port), NoStore) as httpd:
        print(f"serving . on http://localhost:{port}  (nothing cached)")
        print(f"  the album  → http://localhost:{port}/id/album/")
        print(f"  the writing→ http://localhost:{port}/id/album/essay.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")


if __name__ == "__main__":
    main()
