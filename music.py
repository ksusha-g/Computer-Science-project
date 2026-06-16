import pygame
import os

class MusicPlayer:
    def __init__(self):
        self.tracks = ["BattleMech.mp3", "Cyberia.mp3", "Rise & Strike.mp3"]
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.5
        
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        
        self.load_track(self.current_track_index)
        self.play()
    
    def load_track(self, index: int) -> None:
        try:
            if os.path.exists(self.tracks[index]):
                pygame.mixer.music.load(self.tracks[index])
                self.current_track_index = index
            else:
                print(f"Файл {self.tracks[index]} не найден")
        except Exception as e:
            print(f"Ошибка загрузки трека: {e}")
    
    def play(self) -> None:
        try:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
    
    def pause(self) -> None:
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
    
    def next_track(self) -> None:
        self.current_track_index = (self.current_track_index + 1) % len(self.tracks)
        self.load_track(self.current_track_index)
        if self.is_playing:
            self.play()
    
    def prev_track(self) -> None:
        self.current_track_index = (self.current_track_index - 1) % len(self.tracks)
        self.load_track(self.current_track_index)
        if self.is_playing:
            self.play()
    
    def toggle_play_pause(self) -> None:
        if not self.is_playing:
            self.play()
        else:
            self.pause()
    
    def update_button_states(self, pause_button) -> None:
        if self.is_playing and not self.is_paused:
            pause_button.set_idle_image("Pause_Idle.png")
        elif self.is_paused or not self.is_playing:
            pause_button.set_idle_image("Play_Idle.png")