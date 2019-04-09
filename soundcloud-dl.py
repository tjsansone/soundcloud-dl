from __future__ import unicode_literals
import json
import os
import subprocess
from queue import Queue
from bottle import route, run, Bottle, request, static_file
from threading import Thread
from pathlib import Path
from collections import ChainMap

app = Bottle()


app_defaults = {
    'YDL_FORMAT': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
    'YDL_EXTRACT_AUDIO_FORMAT': None,
    'YDL_EXTRACT_AUDIO_QUALITY': '192',
    'YDL_RECODE_VIDEO_FORMAT': None,
    'YDL_OUTPUT_TEMPLATE': '/soundcloud-dl/%(title)s [%(id)s].%(ext)s',
    'YDL_ARCHIVE_FILE': None,
    'YDL_SERVER_HOST': '0.0.0.0',
    'YDL_SERVER_PORT': 9090,
}

@app.route('/soundcloud-dl')
def dl_queue_list():
    return static_file('index.html', root='./')


@app.route('/soundcloud-dl/static/:filename#.*#')
def server_static(filename):
    return static_file(filename, root='./static')


@app.route('/soundcloud-dl/q', method='GET')
def q_size():
    return {"success": True, "size": json.dumps(list(dl_q.queue))}


@app.route('/soundcloud-dl/q', method='POST')
def q_put():
    url = request.forms.get("url")

    if not url:
        return {"success": False, "error": "/q called without a 'url' query param"}

    dl_q.put((url))
    print("Added url " + url + " to the download queue")
    return {"success": True, "url": url}


def dl_worker():
    while not done:
        url = dl_q.get()
        download(url)
        dl_q.task_done()

def download(url):
    subprocess.run("scdl","-l",[url],"--addtofile","--download-archive","/config/archive.txt","--extract-artist","--hide-progress","--onlymp3","--path /downloads")

dl_q = Queue()
done = False
dl_thread = Thread(target=dl_worker)
dl_thread.start()

print("Started download thread")

app_vars = ChainMap(os.environ, app_defaults)

app.run(host=app_vars['YDL_SERVER_HOST'], port=app_vars['YDL_SERVER_PORT'], debug=True)
done = True
dl_thread.join()
