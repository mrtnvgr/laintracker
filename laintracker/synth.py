from numpy import pi,sin,cos,exp,mod,array,frombuffer
import itertools, struct, wave
from random import randint

class Synth:
    def __init__(self, framerate=44100, amplitude=1.0, speed=1.0, quantize=2/15, downgrade=True, downgradeSamples=False, normalize_volume=True):
        self.notefreqs = {
            "C":  [16.35, 32.70, 65.41, 130.81, 261.63, 523.25, 1046.50, 2093.00, 4186.01],
            "C#": [17.32, 34.65, 69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46, 4434.92],
            "D":  [18.35, 36.71, 73.42, 146.83, 293.66, 587.33, 1174.66, 2349.32, 4698.64],
            "D#": [19.45, 38.89, 77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02, 4978.03],
            "E":  [20.60, 41.20, 82.41, 164.81, 329.63, 659.26, 1318.51, 2637.02, 5274.04],
            "F":  [21.83, 43.65, 87.31, 174.61, 349.23, 698.46, 1396.91, 2793.83, 5587.65],
            "F#": [23.12, 46.25, 92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96, 5919.91],
            "G":  [24.50, 49.00, 98.00, 196.00, 392.00, 783.99, 1567.98, 3135.96, 6271.93],
            "G#": [25.96, 51.91, 103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44, 6644.88],
            "A":  [27.50, 55.00, 110.00, 220.00, 440.00, 880.00, 1760.00, 3520.00, 7040.00],
            "A#": [29.14, 58.27, 116.54, 233.08, 466.16, 932.33, 1864.66, 3729.31, 7458.62],
            "B":  [30.87, 61.74, 123.47, 246.94, 493.88, 987.77, 1975.53, 3951.07, 7902.13]
        }
        self.normalize_volume = normalize_volume
        self.framerate = framerate
        self.speed = speed
        self._downgrade = downgrade
        self._downgrade_samples = downgradeSamples
        self._amplitude_scale = 32767
        self._default_amplitude = amplitude
        self._quantize = quantize
        self._channels = 1
        self._bits = 16
    
    def sine_generator(self, frequency, amplitude):
        period_length = int(self.framerate / frequency)
        step = 2 * pi * frequency
        one_period = [amplitude*sin(step * i / self.framerate) for i in range(period_length)]
        return itertools.cycle(self.downgrade(one_period))

    def square_generator(self, frequency, amplitude, duty_cycle=50):
        period_length = int(self.framerate / frequency)
        duty_cycle = int(duty_cycle * period_length / 100)
        one_period = [amplitude*(int(i < duty_cycle) * 2 - 1) for i in range(period_length)]
        return itertools.cycle(self.downgrade(one_period))

    def sawtooth_generator(self, frequency, amplitude):
        period_length = int(self.framerate / frequency)
        one_period = [amplitude*(frequency * (i / self.framerate) * 2 - 1) for i in range(period_length)]
        return itertools.cycle(self.downgrade(one_period))

    def triangle_generator(self, frequency, amplitude):
        period_length = int(self.framerate / frequency)
        half_period = period_length / 2
        one_period = [amplitude*(1 / half_period * (half_period - abs(i - half_period) * 2 - 1) + 0.02)
                      for i in range(period_length)]
        return itertools.cycle(self.downgrade(one_period))
    
    def noise_generator(self, amplitude, **kwargs):
        period = [amplitude*randint(-1,1) for i in range(self.framerate)]
        return itertools.cycle(self.downgrade(period))

    def fnoise_generator(self, frequency, amplitude):
        period = int(self.framerate / frequency)
        lookup_table = [amplitude*randint(-1, 1) for i in range(period)]
        return itertools.cycle(self.downgrade(lookup_table))

    def drum_generator(self, frequency, amplitude):
        period_length = int(self.framerate)
        if frequency.upper() in ("KICK", "KIK"):
            drum = array([sin(2000*exp(-15*0.25*i/self.framerate)*i/self.framerate) for i in range(period_length)])**3*16
        return itertools.cycle(self.downgrade(amplitude*drum))

    def sample_generator(self, frequency, file, amplitude, cut=None):
        try:
            with wave.open(file, 'r') as f:
                data = f.readframes(f.getnframes())
            data = frombuffer(data, dtype=f'int{f.getsampwidth()*8}')/self._amplitude_scale
            if cut!=None:
                if len(cut)!=2: cut = (cut[0],cut[1])
                cut = [int(i*self.framerate) for i in cut]
                data = data[cut[0]:cut[1]]
            if frequency!=None:
                pass # TODO
            sample = (amplitude*data)
            if self._downgrade_samples: sample = self.downgrade(sample)
            return sample
        except FileNotFoundError:
            print(f"{file}: not found")
            return itertools.repeat(0)

    def downgrade(self, arr):
        if self._downgrade: arr = arr - mod(arr, self._quantize)
        return arr
    
    def getAmplitude(self, wavetype, amplitude):
        if amplitude!=None: return amplitude
        if self.normalize_volume:
            if wavetype in ("sine", "drum"):
                return 2
            elif wavetype=="square":
                return 0.5
            else:
                return 1
        return self._default_amplitude

    @staticmethod
    def getReverse(res, reverse):
        if reverse:
            return 1-res
        else:
            return res

    def getFrequency(self, frequency):
        if frequency==None: return None
        if frequency[:-1] in self.notefreqs:
            return self.notefreqs[frequency[:-1]][int(frequency[-1])]
        else:
            return frequency
        
    @staticmethod
    def silence_generator(**kwargs):
        return itertools.repeat(0)

    @staticmethod
    def composite_generator(*generators):
        return (sum(samples) / len(samples) for samples in zip(*generators))
    
    def overlay_waves(self, *waves, chord=False):
        returnlist = []
        for sample in itertools.zip_longest(*waves, fillvalue=0):
            mix = sum(sample)
            if chord:
                chordSample = len(sample)-sample.count(0)
                if chordSample>0: mix = mix//chordSample
            if mix>self._amplitude_scale: mix = self._amplitude_scale
            if mix<-self._amplitude_scale: mix = -self._amplitude_scale
            returnlist.append(mix)
        return returnlist

    def adsr_envelope(self, attack, decay, release, length, sustain_level=0.5, reverse=False, note_length=None):
        attack = attack*note_length
        decay = decay*note_length
        release = release*note_length
        length = length*note_length
        assert length >= attack + decay + release
        total_bytes = int(self.framerate * length)
        attack_bytes = int(self.framerate * attack)
        decay_bytes = int(self.framerate * decay)
        release_bytes = int(self.framerate * release)
        sustain_bytes = total_bytes - attack_bytes - decay_bytes - release_bytes
        decay_step = (1 - sustain_level) / decay_bytes
        release_step = sustain_level / release_bytes
        for i in range(1, attack_bytes + 1):
            yield self.getReverse(i / attack_bytes, reverse)
        for i in range(1, decay_bytes + 1):
            yield self.getReverse(1 - (i * decay_step), reverse)
        for i in range(1, sustain_bytes + 1):
            yield self.getReverse(sustain_level, reverse)
        for i in range(1, release_bytes + 1):
            yield self.getReverse(sustain_level - (i * release_step), reverse)

    def linear_decay_envelope(self, length, peak=1.0, reverse=False, note_length=None):
        length = note_length*length
        total_bytes = int(self.framerate * length)
        for i in range(total_bytes):
            yield self.getReverse((total_bytes - i) / total_bytes * peak, reverse)
    
    def wave_envelope(self, length, wavetype, frequency, peak=1.0, reverse=False, note_length=None):
        wave_generator = eval(f"self.{wavetype}_generator(frequency=frequency, amplitude=peak)")
        length = note_length*length
        total_bytes = int(self.framerate * length)
        wave_slices = itertools.islice(wave_generator, total_bytes)
        for elem in wave_slices:
            if wavetype=="square":
                if elem<0: elem = 0
            else:
                elem = abs(elem)
            yield self.getReverse(float(elem), reverse)

    @staticmethod
    def flat_envelope(amplitude=1):
        return itertools.repeat(amplitude)

    def pack_wave_data(self, wavetype, frequency, length, amplitude=None, envelope=None, **kwargs):
        amplitude = self.getAmplitude(amplitude=amplitude, wavetype=wavetype)
        wave_generator = eval(f"self.{wavetype}_generator(frequency=frequency, amplitude=amplitude, **kwargs)")
        amplitude_scale = self._amplitude_scale
        num_bytes = int(self.framerate * length)
        if not envelope:
            wave_envelope = self.flat_envelope()
        else:
            wave_envelope = eval("self."+envelope["type"]+"_envelope")(note_length=length, **envelope["args"])
        wave_slices = itertools.islice(wave_generator, num_bytes)
        wavedata = [int(next(wave_envelope, 0) * elem * amplitude_scale) for elem in wave_slices]
        return wavedata
    
    @staticmethod
    def pack_pcm_data(wave):
        return struct.pack("<{}h".format(len(wave)), *wave)

    def add_wave_header(self, pcm_data):
        header = struct.pack('<4sI8sIHHIIHH4sI',
                             b"RIFF",
                             len(pcm_data) + 44 - 8,
                             b"WAVEfmt ",
                             16,
                             1,
                             self._channels,
                             self.framerate,
                             self.framerate * self._channels * self._bits // 8,
                             self._channels * self._bits // 8,
                             self._bits,
                             b"data",
                             len(pcm_data))
        return header + pcm_data

    def save_wave(self, pcm_data, file_name="output.wav"):
        with open(file_name, "wb") as f:
            if bytes(pcm_data[:4]) == b"RIFF":
                f.write(pcm_data)
            else:
                f.write(self.add_wave_header(pcm_data))
            print("saved file: {}".format(file_name))
    
    def output(self, text, **kwargs):
        if self.verbose: print(text, **kwargs)

    def compilePatterns(self, data):
        compiled_patterns = {}
        cnpatterns = 0
        cut, file = (None, None)
        npatterns = len(data["patterns"])
        self.output(f"Compiling patterns:")
        for pattern in data["patterns"]:
            cnpatterns += 1
            self.output(f"[{cnpatterns}/{npatterns}] {pattern}")
            compiled_patterns[pattern] = []
            for note in data["patterns"][pattern]:
                if note!=None:
                    if pattern not in data["instruments"]: continue
                    instrument = data["instruments"][pattern]
                    waveargs = {"wavetype": instrument["wavetype"]}
                    if "length" in note: length = note["length"]/self.speed
                    if "cut" in note: cut = note["cut"]
                    if "file" in note: file = note["file"]
                    waveargs["length"] = length
                    if waveargs["wavetype"]=="sample":
                        if cut!=None: waveargs["cut"] = cut
                        if file!=None: waveargs["file"] = file
                        if file in ("NN",""):
                            waveargs["wavetype"] = "silence"
                    frequency = note["note"]
                    if "amplitude" in instrument:
                        waveargs["amplitude"] = instrument["amplitude"]
                    if "filename" in instrument: 
                        waveargs["filename"] = instrument["filename"]
                    if "envelope" in instrument:
                        waveargs["envelope"] = instrument["envelope"]
                    if frequency in ("NN", ""):
                        waveargs["wavetype"] = "silence"
                    if type(frequency) is list:
                        notes = []
                        for fr in range(len(frequency)):
                            waveargs["frequency"] = self.getFrequency(frequency[fr])
                            if "amplitude" in waveargs:
                                originalAmplitude = waveargs["amplitude"]
                                if type(originalAmplitude) is list and len(frequency)<=len(originalAmplitude):
                                    waveargs["amplitude"] = originalAmplitude[fr]
                            notes.append(self.pack_wave_data(**waveargs))
                        notewave = self.overlay_waves(*notes, chord=True)
                    else:
                        waveargs["frequency"] = self.getFrequency(frequency)
                        notewave = self.pack_wave_data(**waveargs)
                    compiled_patterns[pattern] = compiled_patterns[pattern] + notewave
        return compiled_patterns

    def joinPatterns(self, data, compiled_patterns):
        waves = [[]]
        oldIndex = 0
        norder = len(data["order"])
        self.output(f"\nJoining in order:",end="")
        for offset,segment in enumerate(data["order"]):
            if offset!=oldIndex: waves.append([])
            oldIndex = offset
            self.output(f"\n[{offset+1}/{norder}]",end="")
            for pattern in segment:
                self.output(f" {pattern}", end="")
                if pattern not in ("", None):
                    waves[offset] = self.overlay_waves(waves[offset],compiled_patterns[pattern])
        wave = [item for innerlist in waves for item in innerlist]
        self.output("\n")
        return wave

    def compile(self, data, verbose=False):
        self.verbose = verbose
        compiled_patterns = self.compilePatterns(data)
        wave = self.joinPatterns(data, compiled_patterns)
        self.save_wave(self.pack_pcm_data(wave))
