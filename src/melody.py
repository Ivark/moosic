__author__ = 'ivar'

import wave
from math import sin, pi
from random import random
from sys import stdout

def makeMelodyWav(filename, beatsberminute, melodyArray):

    tonenames = [
        "A" , None, "B" , "C" , None, "D" , None, "E" , "F" , None, "G" , None,  # natural
        None, "Bb", "Cb", None, "Db", None, "Eb", "Fb", None, "Gb", None, "Ab",  # flat
        None, "A#", None, "B#", "C#", None, "D#", None, "E#", "F#", None, "G#"   # sharp
    ]

    beatduration = 60.0 / beatsberminute
    samplerate = 48000.0
    samplewidth = 4
    amplitude = 2 ** 30.0

    samplesperbeat = int(samplerate * beatduration)

    o = []
    for beat in melodyArray:
        while len(beat) > len(o): o.append(random())

    samples = [0] * samplesperbeat * len(melodyArray)
    for i in range(len(melodyArray)):
        for j in range(samplesperbeat):
            s = i * samplesperbeat + j
            # stdout.write(str(s))
            for k in range(len(melodyArray[i])):
                note = melodyArray[i][k]
                l = len(note) - 1
                if l == -1: continue
                m = 1.0
                if note[l] in "+-*":
                    if note[l] in "-*": m *= 1.0 - (float(j) / samplesperbeat) ** 25
                    if note[l] in "+*": m *= 1.0 - (float(samplesperbeat - j) / samplesperbeat) ** 25
                    l -= 1
                freq = 27.5 * 2.0 ** ((12.0 * int(note[l]) + (tonenames.index(note[:l]) % 12)) / 12.0) / samplerate
                samples[s] += int(m * amplitude * sin((s * freq + o[k]) * 2 * pi) / (1 + k) ** 0.3)
            #     stdout.write('%2s%1d, f: %6.1fHz\n' % (note[:l], int(note[l:]), freq * samplerate))
            # stdout.write('\n')

    wavedata = ''
    for sample in samples:
        # stdout.write(str(sample) + '\n')
        bytes = [(sample >> j * 8) % 256 for j in range(samplewidth)]

        for byte in bytes:
            wavedata += chr(byte)
        #     stdout.write('%03d.' % byte)
        # stdout.write('\n')

    # for i in range(4):
    #     sample = int(samples[len(samples) - 1] * (4 - i) / 5.0)
    #     bytes = [(sample >> j * 8) % 256 for j in range(samplewidth)]
    #     for byte in bytes:
    #         wavedata += chr(byte)
    #
    # for i in range(4 * samplewidth):
    #     wavedata += chr(0)

    wavefile = wave.open(filename, 'wb')
    wavefile.setframerate(samplerate)
    wavefile.setsampwidth(samplewidth)
    wavefile.setnchannels(1)
    wavefile.writeframes(wavedata)
    wavefile.close()