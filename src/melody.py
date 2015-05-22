__author__ = 'ivar'

import wave
import re
from math import sin, pi, ceil
from random import random
from types import IntType, ListType, StringType
from tools import every, clamp
from sys import stdout

TONE_NAMES = {
    "Ab": -1, "A":  0, "A#":  1, "Bb":  1, "B":  2, "B#":  3, "Cb": -10, "C": -9, "C#": -8,
    "Db": -8, "D": -7, "D#": -6, "Eb": -6, "E": -5, "E#": -4, "Fb":  -5, "F": -4, "F#": -3,
    "Gb": -3, "G": -2, "G#": -1
}
SAMPLE_RATE = 48000
SAMPLE_WIDTH = 4
MAX_AMPLITUDE = 2.0 ** 31.0 - 1
HARDNESS = 0.2

class Note:
    def __init__(self, tonename, octave=None, duration=None, start=None, amplitude=None):
        global _octave, _duration, _head, _amplitude
        if "_octave"    not in globals(): _octave    = 4
        if "_duration"  not in globals(): _duration  = 1.0
        if "_head"      not in globals(): _head      = 0.0
        if "_amplitude" not in globals(): _amplitude = 0.5

        assert tonename in TONE_NAMES
        assert octave    is None or (type(octave) is IntType             and 0 <= octave <= 8)
        assert duration  is None or (isinstance(duration , (int, float)) and 0.0 < duration)
        assert start     is None or (isinstance(start , (int, float))    and 0.0 <= start)
        assert amplitude is None or (isinstance(amplitude, (int, float)) and 0.0 <= amplitude <= 1.0)

        if octave    is not None: _octave    = octave
        if duration  is not None: _duration  = duration
        if start     is not None: _head      = start
        if amplitude is not None: _amplitude = amplitude

        semitone = TONE_NAMES[tonename]

        self.tonename  = tonename
        self.semitone  = semitone
        self.octave    = _octave
        self.frequency = 27.5 * 2.0 ** (((12.0 * _octave) + semitone) / 12.0) / SAMPLE_RATE
        self.duration  = _duration
        self.start     = _head
        self.amplitude = _amplitude
        self.offset    = random() * 0

        _head += _duration

    def end(self):
        return self.start + self.duration

def n(*args, **kwargs):
    _kwargs = dict()
    if "o" in kwargs: _kwargs["octave"]    = kwargs["o"]
    if "d" in kwargs: _kwargs["duration"]  = kwargs["d"]
    if "s" in kwargs: _kwargs["start"]     = kwargs["s"]
    if "a" in kwargs: _kwargs["amplitude"] = kwargs["a"]
    return Note(*args, **_kwargs)

def makeMelodyWav(filename, beatsperminute, notes):
    assert type(filename) is StringType and re.match(r'^[^/\:*?\"<>|]*[^/.\:*?\"<>|]+$', filename)
    assert isinstance(beatsperminute, (int, float)) and 0.0 < beatsperminute
    assert type(notes) is ListType and every(notes, lambda note: isinstance(note, Note))

    beatduration = 60.0 / beatsperminute
    samplesperbeat = int(SAMPLE_RATE * beatduration)

    beats = int(ceil(max(notes, key=lambda n: n.end()).end()))
    notesSorted = sorted(notes, key=lambda n: n.start)
    notesIndex = 0
    notesOpen = set()
    samples = [0] * (samplesperbeat * beats)
    for s in range(len(samples)):
        beat = float(s) / samplesperbeat
        while notesIndex < len(notes) and beat >= notesSorted[notesIndex].start:
            notesOpen.add(notesSorted[notesIndex])
            notesIndex += 1
        closeNotes = set()
        for note in notesOpen:
            if beat > note.end():
                closeNotes.add(note)
                continue
            dbeat = beat - note.start
            hardness = clamp(7.0, (HARDNESS * 43.0 + 7.0), 50.0)
            magnitude = 1.0 - 1.0 / (dbeat + 1.0) ** hardness - 1.0 / (note.duration + 1.0 - dbeat) ** hardness
            sample = int(MAX_AMPLITUDE * magnitude * note.amplitude * sin((s * note.frequency + note.offset) * 2 * pi))
            if samples[s] + sample > MAX_AMPLITUDE: samples[s] = MAX_AMPLITUDE
            elif samples[s] + sample < -MAX_AMPLITUDE: samples[s] = -MAX_AMPLITUDE
            else: samples[s] += sample
        notesOpen = notesOpen.difference(closeNotes)

    wavedata = ''
    for sample in samples:
        bytes = [(sample >> j * 8) % 256 for j in range(SAMPLE_WIDTH)]
        for byte in bytes: wavedata += chr(byte)


    wavefile = wave.open(filename, 'wb')
    wavefile.setframerate(SAMPLE_RATE)
    wavefile.setsampwidth(SAMPLE_WIDTH)
    wavefile.setnchannels(1)
    wavefile.writeframes(wavedata)
    wavefile.close()