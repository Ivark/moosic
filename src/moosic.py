__author__ = 'ivar'

from sys import stdout
import wave
from matplotlib import pyplot as plt
import audioop
import random
from math import log, pi, sin, sqrt


def out(obj): stdout.write(str(obj) + '\n')


let = wave.open('go-let-it.wav', 'rb')
nchords = 4

sampwidth = let.getsampwidth()
rate = let.getframerate()
framesperchord = let.getnframes() / 4 + (1 if let.getnframes() % 4 != 0 else 0)
frags = [let.readframes(framesperchord) for i in range(nchords)]
let.rewind()
all = let.readframes(let.getnframes())
duration = float(let.getnframes())/let.getframerate()
let.close()

colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'orange', 'black', 'darkgrey', 'purple']
random.shuffle(colors)

nrows = 3
ncols = nchords

fig = plt.figure()


def freqsFromFrag(frag, sampwidth, rate):
    samples = [audioop.getsample(frag, sampwidth, i) for i in range(len(frag) / sampwidth)]
    freqs = {}
    pos0 = samples[0] > 0
    t0 = 0.0
    t1 = 0.0
    for i in range(1, len(samples)):
        pos1 = samples[i] > 0
        # out('%5s - %5s - %8.2f - %8.2f - %8.2f' % (pos0, pos1, t0, t1, samples[i]))
        if pos0 != pos1:
            t2 = i - 1.0 + samples[i - 1] / (samples[i - 1] - samples[i])
            if t2 > t1 > t0 > 0.0:
                freq = float(rate) / (t2 - t0)
                if not freqs.has_key(freq):
                    freqs[freq] = 1
                else:
                    freqs[freq] += 1
            pos0 = pos1
            t0 = t1
            t1 = t2
    return freqs


def noteAndFreq(freq):
    notes = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'F', 'F#', 'G', 'G#', 'A']
    logfreq = 12 * log(freq / 55, 2)
    return notes[round(logfreq % 12, 0)], 2 ** (logfreq / 12 + log(55, 2))


allfreqs = freqsFromFrag(all, sampwidth, rate)
nfreqs = sum(allfreqs.values())
avefreq = float(sum([key * value for (key, value) in allfreqs.items()]) / nfreqs)
maxy = max([avefreq * value / key for (key, value) in allfreqs.items()])

moosic = ''

for plti in range(len(frags)):
    freqs = freqsFromFrag(frags[plti], sampwidth, rate)
    keys = sorted(freqs.keys())
    values = [avefreq * freqs[key] * nchords / key for key in keys]
    adjvalues = [values[i] - avefreq * allfreqs[keys[i]] / keys[i] for i in range(len(keys))]
    modfreqs = {}
    for i in range(len(keys)):
        key = keys[i]
        modkey = log(key - 55, 2) % 1
        if not modfreqs.has_key(modkey):
            modfreqs[modkey] = values[i]
        else:
            modfreqs[modkey] += values[i]

    modkeys2 = map(lambda k: float(k / 1000.0), range(1000))
    modvalues2 = [sum([v / (0.5 + k - key) ** 2 for (k, v) in modfreqs.items()]) for key in modkeys2]

    # out(sum(modadjfreqs.values()))
    # out(sum(adjvalues))
    # out('')

    color = colors.pop()

    ax1 = fig.add_subplot(nrows, ncols, plti + 1)
    ax1.set_xscale('log')
    ax1.set_autoscaley_on(True)
    ax1.set_autoscalex_on(False)
    ax1.set_xbound(300, 5000)
    ax1.get_yaxis().set_visible(False)
    ax1.get_xaxis().set_ticks([440, 880, 1760, 3520])
    ax1.get_xaxis().set_ticklabels(map(str, [440, 880, 1760, 3520]))
    ax1.plot([min(allfreqs.keys()), max(allfreqs.keys())], [0, 0], color='lightgrey')
    ax1.fill([keys[0]] + keys + [keys[len(keys) - 1]], [0] + values + [0], color=color)

    ax1c = ax1.twiny()
    ax1c.set_xscale('log')
    ax1c.set_autoscalex_on(False)
    ax1c.set_xbound(300, 5000)
    ax1c.get_xaxis().set_ticks([300, 700])
    ax1c.get_xaxis().set_ticklabels(['300', '700'])
    ax1c.plot([300, 300], [0, max(values)])
    ax1c.plot([700, 700], [0, max(values)])

    ax2 = fig.add_subplot(nrows, ncols, plti + ncols + 1)
    ax2.set_xscale('log')
    ax2.set_autoscaley_on(True)
    ax2.set_autoscalex_on(False)
    ax2.set_xbound(300, 5000)
    ax2.get_yaxis().set_visible(False)
    ax2.get_xaxis().set_ticks([440, 880, 1760, 3520])
    ax2.get_xaxis().set_ticklabels(map(str, [440, 880, 1760, 3520]))
    ax2.plot([min(allfreqs.keys()), max(allfreqs.keys())], [0, 0], color='lightgrey')
    ax2.plot(keys, adjvalues, color=color)

    ax3 = fig.add_subplot(nrows, ncols, plti + 2 * ncols + 1)
    ax3.set_autoscaley_on(True)
    ax3.set_autoscalex_on(False)
    ax3.set_xbound(0, 1)
    ax3.get_yaxis().set_ticks([])
    ax3.get_xaxis().set_ticks([0.0, 1.0 / 12.0, 2.0 / 12.0, 3.0 / 12.0,
                               4.0 / 12.0, 5.0 / 12.0, 6.0 / 12.0, 7.0 / 12.0,
                               8.0 / 12.0, 9.0 / 12.0, 10.0 / 12.0, 11.0 / 12.0, 1.0])
    ax3.get_xaxis().set_ticklabels(map(str, ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A']))
    ax3.plot([0, 1], [0.88 * max(modfreqs.values())] * 2, color='lightgrey')
    ax3.plot(sorted(modfreqs), [modfreqs[key] for key in sorted(modfreqs)], color=color)

    winners = [(k, v) for (k, v) in modfreqs.items() if v > 0.95 * max(modfreqs.values())]

    out(len(winners))

    amplitudes = [32.0 * v / max(modfreqs.values()) for (k, v) in winners]
    frequencies = [(2 ** k * 440) / rate for (k, v) in winners]
    offsets = [0] * len(winners)

    chordduration = duration / nchords
    bufferduration = 0.05
    buffernsamples = int(bufferduration * rate)

    nbuffers = int(chordduration / bufferduration)

    for b in range(nbuffers):
        for s in range(buffernsamples):
            # out('b: %d, s: %d' % (b, s))
            sampleflt = 0
            for i in range(len(amplitudes)):
                sampleflt += float(amplitudes[i]) * sin(20 * pi * s * frequencies[i] + offsets[i])
            sample = int(sampleflt)
            # out(bin(sample))
            moosic += chr((sample >> 8) & 255)
            moosic += chr((sample >> 0) & 255)
        for i in range(len(offsets)):
            offsets[i] = (offsets[i] + float(buffernsamples) * frequencies[i]) % (2.0 * pi)


plt.show()



maestro = wave.open('maestro.wav', 'wb')
maestro.setframerate(rate)
maestro.setsampwidth(2)
maestro.setnchannels(1)
maestro.writeframes(moosic)
maestro.close()