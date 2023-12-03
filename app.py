from flask import Flask, render_template, request
from werkzeug.datastructures import ImmutableMultiDict
import pytubDef
import logging

if pytubDef.log():
    logging.basicConfig(filename="data/flaskDebug.log", encoding="utf-8", level=logging.DEBUG)
app = Flask(__name__)


@app.route('/')
def index():
    monitored_playlist = pytubDef.return_monitored_playlist()
    monitored_playlist_titles = [pytubDef.get_playlist_name(playlist) for playlist in monitored_playlist]

    zipped = zip([], [])
    zipped1 = zip(monitored_playlist_titles, monitored_playlist)
    return render_template("index.html", channels=zipped, playlist=zipped1)


@app.route("/settings.html")
def settings():
    return render_template("settings.html", channelDir=pytubDef.return_channel_dir(), interval=pytubDef.return_interval(),
                           ytagent=pytubDef.return_yt_agent())


@app.route("/index.html", methods=["GET", "POST"])
def back():
    return index()


@app.route('/', methods=["GET", "POST"])
def add_channel():
    monitored_playlist = pytubDef.return_monitored_playlist()
    monitored_playlist_titles = [pytubDef.get_playlist_name(playlist) for playlist in monitored_playlist]

    if request.method == "POST":

        for n in range(len(monitored_playlist)):
            if request.form == ImmutableMultiDict([(str(monitored_playlist_titles[n]), 'Remove')]):
                pytubDef.remove_monitored_playlist(str(monitored_playlist[n]))
                monitored_playlist = pytubDef.return_monitored_playlist()
                monitored_playlist_titles = []

                for playlist in monitored_playlist:
                    monitored_playlist_titles.append(pytubDef.get_playlist_name(playlist))

                zipped = zip([], [])
                zipped1 = zip(monitored_playlist_titles, monitored_playlist)
                return render_template("index.html", channels=zipped, playlist=zipped1)

        if request.form["inputSubmit"]:
            newURL = request.form["inputField"]
            if pytubDef.new_monitored_playlist(newURL):
                print("Success")
            else:
                print("URL Invalid")

    monitored_playlist = pytubDef.return_monitored_playlist()
    monitored_playlist_titles = [pytubDef.get_playlist_name(playlist) for playlist in monitored_playlist]

    zipped = zip([], [])
    zipped1 = zip(monitored_playlist_titles, monitored_playlist)
    return render_template("index.html", channels=zipped, playlist=zipped1)


@app.route("/settings.html", methods=["POST"])
def update_settings():
    if request.method == "POST":
        if request.form.get("IntervalSubmit"):
            pytubDef.update_interval(int(request.form['Interval']))
        if request.form.get("toggleChannelDir"):
            pytubDef.toggle_channel_dir()
        if request.form.get("toggleytagent"):
            pytubDef.toggle_yt_agent()

    return settings()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
