"""Audio system using Pygame MIDI synthesizer with mute support and custom SFX."""

import pygame
import pygame.midi

MIDI_NOTE_OFF_EVENT = pygame.USEREVENT + 1
MIDI_MUSIC_EVENT = pygame.USEREVENT + 2


class MidiSynth:
    """MIDI synthesizer for zero-asset retro synth audio."""

    def __init__(self) -> None:
        self.output: pygame.midi.Output | None = None
        self.music_index: int = 0
        self.active_notes: set[int] = set()
        self.is_muted: bool = False
        self._init_device()

    def _init_device(self) -> None:
        try:
            if not pygame.midi.get_init():
                pygame.midi.init()
            output_count = pygame.midi.get_count()
            for device_id in range(output_count):
                info = pygame.midi.get_device_info(device_id)
                if info and info[3] == 1:  # Is output device
                    self.output = pygame.midi.Output(device_id)
                    self.output.write_short(0xC0, 80)  # Synth Lead program
                    break
        except (pygame.midi.MidiException, Exception):
            self.output = None

    def toggle_mute(self) -> bool:
        """Toggle mute state. Releases active notes when muting."""
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.release_notes()
        return self.is_muted

    def note(self, pitch: int, duration_ms: int = 120, volume: int = 90) -> None:
        """Play a single MIDI note if not muted."""
        if self.is_muted or self.output is None:
            return
        try:
            self.output.note_on(pitch, volume)
            self.active_notes.add(pitch)
            pygame.time.set_timer(MIDI_NOTE_OFF_EVENT, duration_ms, True)
        except (pygame.midi.MidiException, Exception):
            self.output = None

    def eat_regular(self) -> None:
        """SFX for regular fruit."""
        self.note(76, 150, 105)
        self.note(83, 150, 80)

    def eat_golden(self) -> None:
        """SFX for golden bonus fruit."""
        self.note(76, 220, 115)
        self.note(81, 220, 115)
        self.note(88, 300, 125)

    def eat_freeze(self) -> None:
        """SFX for freeze berry."""
        self.note(84, 180, 95)
        self.note(86, 240, 100)
        self.note(91, 320, 110)

    def eat_ghost(self) -> None:
        """SFX for ghost berry."""
        self.note(69, 200, 90)
        self.note(74, 250, 100)
        self.note(81, 350, 110)

    def death(self) -> None:
        """SFX on crash/game over."""
        if self.is_muted or self.output is None:
            return
        for pitch in (55, 53, 50, 46):
            self.note(pitch, 380, 100)

    def start(self) -> None:
        """SFX when starting a match."""
        self.note(64, 180, 85)
        self.note(67, 220, 95)

    def music_tick(self) -> None:
        """Periodic background music step."""
        if self.is_muted or self.output is None:
            return
        melody = (60, 64, 67, 71, 67, 64, 62, 67)
        pitch = melody[self.music_index % len(melody)]
        self.note(pitch, 380, 42)
        if self.music_index % 4 == 0:
            bass = (36, 38, 36, 43)[(self.music_index // 4) % 4]
            self.note(bass, 600, 60)
        self.music_index += 1

    def release_notes(self) -> None:
        """Silences all active notes."""
        if self.output is None:
            return
        for pitch in tuple(self.active_notes):
            try:
                self.output.note_off(pitch, 0)
            except (pygame.midi.MidiException, Exception):
                pass
        self.active_notes.clear()

    def close(self) -> None:
        """Clean shutdown of MIDI device."""
        if self.output:
            try:
                self.release_notes()
                self.output.close()
            except (pygame.midi.MidiException, Exception):
                pass
            self.output = None


# Global audio singleton
midi_synth: MidiSynth = MidiSynth()
