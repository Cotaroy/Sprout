from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
from PySide6.QtCore import QUrl, QTimer
import os


class AudioPlayer:
    def __init__(self, output_device=None):
        if output_device is None:
            output_device = QMediaDevices.defaultAudioOutput()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput(output_device)
        self.player.setAudioOutput(self.audio_output)

    def is_playing(self):
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def play_sfx(self, filename, duration_ms=-1):
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

    def stop(self):
        self.player.stop()