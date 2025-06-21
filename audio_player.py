from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
import os


class AudioPlayer:
    def __init__(self):
        # Shared player for single-track playback (e.g. background music)
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
    def is_playing(self):
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def play_sfx(self, filename):
        file_url = QUrl.fromLocalFile(os.path.abspath(filename))
        self.player.setSource(file_url)
        self.player.play()

    def play_bg_track(self, filename):
        file_url = QUrl.fromLocalFile(os.path.abspath(filename))
        self.player.setSource(file_url)
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.player.play()

    def set_volume(self, volume_percent):
        # volume_percent: 0 to 100
        self.audio_output.setVolume(volume_percent / 100.0)

    