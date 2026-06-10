import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSoundManager(unittest.TestCase):
    def test_creates_exactly_four_sounds(self):
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', return_value=MagicMock()) as mock_sound:
            from systems.sound_manager import SoundManager
            SoundManager()
            self.assertEqual(mock_sound.call_count, 4)

    def test_play_gunshot_calls_play(self):
        mock_gunshot = MagicMock()
        sounds_cycle = [mock_gunshot, MagicMock(), MagicMock(), MagicMock()]
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', side_effect=sounds_cycle):
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            sm.play_gunshot()
            mock_gunshot.play.assert_called_once()

    def test_play_reload_calls_play(self):
        mock_reload = MagicMock()
        sounds_cycle = [MagicMock(), mock_reload, MagicMock(), MagicMock()]
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', side_effect=sounds_cycle):
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            sm.play_reload()
            mock_reload.play.assert_called_once()

    def test_play_hit_calls_play(self):
        mock_hit = MagicMock()
        sounds_cycle = [MagicMock(), MagicMock(), mock_hit, MagicMock()]
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', side_effect=sounds_cycle):
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            sm.play_hit()
            mock_hit.play.assert_called_once()

    def test_play_death_calls_play(self):
        mock_death = MagicMock()
        sounds_cycle = [MagicMock(), MagicMock(), MagicMock(), mock_death]
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', side_effect=sounds_cycle):
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            sm.play_death()
            mock_death.play.assert_called_once()


if __name__ == '__main__':
    unittest.main()
