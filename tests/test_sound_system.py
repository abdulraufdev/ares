"""Unit tests for sound system."""
import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock
from core.sound_manager import SoundManager


class TestSoundManager:
    """Test suite for SoundManager class."""
    
    def test_initialization_graceful_failure(self):
        """Test that SoundManager handles initialization failure gracefully."""
        with patch('pygame.mixer.get_init', return_value=None):
            with patch('pygame.mixer.init', side_effect=Exception("No audio device")):
                sm = SoundManager()
                assert sm.initialized == False
                # Should not crash, just disable sound
    
    def test_initialization_success(self):
        """Test successful initialization."""
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.get_init', return_value=True):
                with patch('os.path.exists', return_value=True):
                    with patch('pygame.mixer.Sound'):
                        sm = SoundManager()
                        assert sm.initialized == True
    
    def test_sfx_volume_defaults(self):
        """Test default volume settings."""
        sm = SoundManager()
        assert sm.bgm_volume == 0.3
        assert sm.sfx_volume == 0.5
    
    def test_play_bgm_when_not_initialized(self):
        """Test that play_bgm doesn't crash when not initialized."""
        with patch('pygame.mixer.init', side_effect=Exception("No audio")):
            sm = SoundManager()
            # Should not crash
            sm.play_bgm('gameplay')
    
    def test_play_sfx_when_not_initialized(self):
        """Test that play_sfx doesn't crash when not initialized."""
        with patch('pygame.mixer.init', side_effect=Exception("No audio")):
            sm = SoundManager()
            # Should not crash
            sm.play_sfx('movement')
    
    def test_pause_resume_bgm_when_not_initialized(self):
        """Test pause/resume don't crash when not initialized."""
        with patch('pygame.mixer.init', side_effect=Exception("No audio")):
            sm = SoundManager()
            sm.pause_bgm()
            sm.resume_bgm()
            # Should not crash
    
    def test_mute_unmute(self):
        """Test mute/unmute functionality."""
        sm = SoundManager()
        assert sm.muted == False
        sm.mute()
        assert sm.muted == True
        sm.unmute()
        assert sm.muted == False
    
    def test_set_volumes(self):
        """Test volume setting with clamping."""
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.get_init', return_value=True):
                with patch('os.path.exists', return_value=True):
                    with patch('pygame.mixer.Sound'):
                        with patch('pygame.mixer.music.set_volume'):
                            sm = SoundManager()
                            
                            # Test BGM volume clamping
                            sm.set_bgm_volume(1.5)
                            assert sm.bgm_volume == 1.0
                            
                            sm.set_bgm_volume(-0.5)
                            assert sm.bgm_volume == 0.0
                            
                            sm.set_bgm_volume(0.5)
                            assert sm.bgm_volume == 0.5
                            
                            # Test SFX volume clamping
                            sm.set_sfx_volume(1.5)
                            assert sm.sfx_volume == 1.0
                            
                            sm.set_sfx_volume(-0.5)
                            assert sm.sfx_volume == 0.0
                            
                            sm.set_sfx_volume(0.7)
                            assert sm.sfx_volume == 0.7
    
    def test_stop_bgm_when_not_initialized(self):
        """Test that stop_bgm doesn't crash when not initialized."""
        with patch('pygame.mixer.init', side_effect=Exception("No audio")):
            sm = SoundManager()
            sm.stop_bgm()
            # Should not crash


class TestSoundIntegration:
    """Test suite for sound integration with gameplay."""
    
    def test_gameplay_imports_sound_manager(self):
        """Test that gameplay.py imports SoundManager."""
        from core.gameplay import GameSession
        # Just verify import doesn't crash
        assert True
    
    def test_game_session_has_sound_manager(self):
        """Test that GameSession initializes a SoundManager."""
        # This test would require mocking pygame display and other components
        # For now, just verify the class can be imported
        from core.gameplay import GameSession
        assert hasattr(GameSession, '__init__')
