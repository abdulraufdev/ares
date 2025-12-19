"""Sound management system for Algorithm Arena."""
import pygame
import os


class SoundManager:
    """Manages all audio playback for the game."""
    
    def __init__(self, sounds_dir: str = "Sounds"):
        """Initialize the sound manager.
        
        Args:
            sounds_dir: Directory containing sound files
        """
        self.sounds_dir = sounds_dir
        self.initialized = False
        self.muted = False
        self.bgm_volume = 0.3  # 30% for BGM
        self.sfx_volume = 0.5  # 50% for SFX
        
        # Sound file paths
        self.bgm_files = {
            'gameplay': 'Project BGM.mp3',
            'victory': 'Victory sound.mp3',
            'defeat': 'Defeat sound.mp3'
        }
        
        self.sfx_files = {
            'movement': 'Movement-sound.wav',
            'hit': 'Hit-sound.wav'
        }
        
        # Sound objects (SFX only - BGM uses pygame.mixer.music)
        self.sfx = {}
        
        # Initialize pygame mixer
        self._init_mixer()
        
        # Load sounds if initialization successful
        if self.initialized:
            self._load_sounds()
    
    def _init_mixer(self):
        """Initialize pygame mixer with error handling."""
        try:
            # Initialize mixer if not already initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512
                )
            self.initialized = True
            print("Sound system initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize sound system: {e}")
            print("Game will continue without sound")
            self.initialized = False
    
    def _load_sounds(self):
        """Load all sound files."""
        if not self.initialized:
            return
        
        # Load SFX (WAV files)
        for key, filename in self.sfx_files.items():
            filepath = os.path.join(self.sounds_dir, filename)
            try:
                if os.path.exists(filepath):
                    self.sfx[key] = pygame.mixer.Sound(filepath)
                    self.sfx[key].set_volume(self.sfx_volume)
                    print(f"Loaded SFX: {filename}")
                else:
                    print(f"Warning: Sound file not found: {filepath}")
            except Exception as e:
                print(f"Warning: Failed to load {filename}: {e}")
        
        # BGM files will be loaded on-demand using pygame.mixer.music
    
    def play_bgm(self, bgm_key: str, loop: bool = True):
        """Play background music.
        
        Args:
            bgm_key: Key for BGM file ('gameplay', 'victory', 'defeat')
            loop: Whether to loop the music (-1 for infinite, 0 for once)
        """
        if not self.initialized or self.muted:
            return
        
        if bgm_key not in self.bgm_files:
            print(f"Warning: Unknown BGM key: {bgm_key}")
            return
        
        filepath = os.path.join(self.sounds_dir, self.bgm_files[bgm_key])
        
        try:
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                print(f"Playing BGM: {self.bgm_files[bgm_key]}")
            else:
                print(f"Warning: BGM file not found: {filepath}")
        except Exception as e:
            print(f"Warning: Failed to play BGM {bgm_key}: {e}")
    
    def stop_bgm(self):
        """Stop background music."""
        if not self.initialized:
            return
        
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Warning: Failed to stop BGM: {e}")
    
    def pause_bgm(self):
        """Pause background music."""
        if not self.initialized:
            return
        
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"Warning: Failed to pause BGM: {e}")
    
    def resume_bgm(self):
        """Resume background music."""
        if not self.initialized or self.muted:
            return
        
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Warning: Failed to resume BGM: {e}")
    
    def play_sfx(self, sfx_key: str):
        """Play sound effect.
        
        Args:
            sfx_key: Key for SFX ('movement', 'hit')
        """
        if not self.initialized or self.muted:
            return
        
        if sfx_key not in self.sfx:
            print(f"Warning: Unknown SFX key: {sfx_key}")
            return
        
        try:
            self.sfx[sfx_key].play()
        except Exception as e:
            print(f"Warning: Failed to play SFX {sfx_key}: {e}")
    
    def set_bgm_volume(self, volume: float):
        """Set BGM volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if not self.initialized:
            return
        
        self.bgm_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.bgm_volume)
        except Exception as e:
            print(f"Warning: Failed to set BGM volume: {e}")
    
    def set_sfx_volume(self, volume: float):
        """Set SFX volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if not self.initialized:
            return
        
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sfx.values():
            try:
                sound.set_volume(self.sfx_volume)
            except Exception as e:
                print(f"Warning: Failed to set SFX volume: {e}")
    
    def mute(self):
        """Mute all audio."""
        self.muted = True
        if self.initialized:
            try:
                pygame.mixer.music.pause()
            except Exception as e:
                print(f"Warning: Failed to mute: {e}")
    
    def unmute(self):
        """Unmute all audio."""
        self.muted = False
        if self.initialized:
            try:
                pygame.mixer.music.unpause()
            except Exception as e:
                print(f"Warning: Failed to unmute: {e}")
    
    def is_bgm_playing(self) -> bool:
        """Check if BGM is currently playing.
        
        Returns:
            True if BGM is playing
        """
        if not self.initialized:
            return False
        
        try:
            return pygame.mixer.music.get_busy()
        except Exception as e:
            print(f"Warning: Failed to check BGM status: {e}")
            return False
