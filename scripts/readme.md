Tetris and OCR related scripts will be found in this folder and documented in this file

# Restream

`scripts/restream.py` is a script to allow a restreamer to quickly get started to OCR from a CTM Stencil-ready twitch stream.

This can allow a restreamer to compute stats and redraw a stream, or even render a 1v1 competition while computing score differential between players.

To run this script, you are expected to have downloaded and installed the following CLI tools:
* [streamlink](https://streamlink.github.io/install.html)
* [vlc](https://www.videolan.org/index.html)
* [ffmpeg](https://ffmpeg.org/download.html)


The script can be invoked from NESTrisOCR's root folder as:
```bash
python -m scripts.restream PLAYER_1_TWITCH_USER_NAME 1

# and for player 2
python -m scripts.restream PLAYER_1_TWITCH_USER_NAME 2
```

To test this, visit https://www.twitch.tv/directory/game/Tetris to see who is streaming with CTM Stencil. Select the twitch user name of a player and use it in the command for player 1 above.


The script does the following:

* Locate suitable stream quality for the twitch user (720p30 preferred)
* Create local VLC server from it
* Extract information such as FPS and resolution
* Create player config file based of a template
* Invoke NESTrisOCR's calibrator for manual fine tuning and verification (Should be very close and quick, thanks to using the Stencil)
* Starts NESTrisOCR with that config


The VLC servers will be accessible locally from the following 2 URLs (for player 1 and 2 respectively):

* http://localhost:8081 for player 1
* http://localhost:8082 for player 2


NESTrisOCR will push the game data to ports 4001 and 4002 for player 1 and player 2 respectively, where a suitable renderer may be listening (like [NESTrisStatsUI](https://github.com/timotheeg/NESTrisStatsUI)).


Note: running the local VLC server on windows doesn't seem to work very well (for some reason???). You can forgo VLC and have NESTrisOCR read straight from the twitch stream. This can be done by adding the CLI arg `--novlc` like this:

```bash
python -m scripts.restream --novlc PLAYER_1_TWITCH_USER_NAME 1
```



# Compute Color Palette

TODO: Document!