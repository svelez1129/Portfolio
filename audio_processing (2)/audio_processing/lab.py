"""
6.101 Lab 0:
Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Returns a new sound containing the samples of the original in reverse
    order, without modifying the input sound.

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary with the samples in reversed order
    """
    # create a new dictionary to copy sound
    dictionary = {}
    dictionary["rate"] = sound["rate"]
    dictionary["samples"] = []
    # add the samples of sound into dictionary in reverse order
    for i in sound["samples"][::-1]:
        dictionary["samples"].append(i)
    return dictionary


def mix(sound1, sound2, p):
    """
    Mix two audio sounds based on given porportion

    Args:
        sound1: a dictionary representing a mono sound
        sound2: another dictionary representing a mono sound
        p: mixing parameter
    Returns:
        A new mixed mono sound dictionary that is the mix of sound1 and sound2
    """
    # mix 2 good sounds
    if "rate" not in sound1 or "rate" not in sound2 or sound1["rate"] != sound2["rate"]:
        return None

    r = sound1["rate"]  # get rate
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]
    len_new_sound = len(sound1)
    if len(sound1) < len(sound2):
        len_new_sound = len(sound1)
    elif len(sound2) < len(sound1):
        len_new_sound = len(sound2)
    new_sound = []
    x = 0
    while x <= len_new_sound:
        s2, s1 = p * sound1[x], sound2[x] * (1 - p)
        new_sound.append(s1 + s2)  # add sounds
        x += 1
    mixed_sound = {"rate": r, "samples": new_sound}
    return mixed_sound  # return new sound


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """
    # create a new echo sound dictionary, copy of sound
    echo_sound = {
        "rate": sound["rate"],
        "samples": sound["samples"].copy(),
    }
    num = 0  # the starting index for an echoed sample to add on the the previous sample
    sample_delay = round(delay * sound["rate"])
    original_scale = scale
    #create a new echo for each num_echoes
    for echoes in range(1, num_echoes + 1):
        new_sample = [x * scale for x in sound["samples"]]
        echo_sound["samples"] += [0] * sample_delay
        for index in range(sample_delay * echoes, len(echo_sound["samples"])):
            echo_sound["samples"][index] += new_sample[num]
            num += 1
        scale *= original_scale
        num = 0
    return echo_sound


def pan(sound):
    """
    Compute a new sound from stereo sound such
    that the left and right samples are scaled
    differently to create an affect

    Args:
        sound: a stereo dictionary
    Returns:
        new_sound: a new stereo dictionary with the added changes
    """
    # create new sound to store stereo sound
    new_sound = {}
    new_sound["rate"] = sound["rate"]
    new_sound["right"] = []
    new_sound["left"] = []
    len_overall = len(sound["right"])
    changing_scale = 1
    for i in range(len_overall):
        # appends the correct number for starting index
        if i == 0:
            new_sound["right"].append(0)
            new_sound["left"].append(sound["left"][i])
        # appends the correct number for the last index
        elif i == range(len_overall):
            new_sound["right"].append(sound["right"][i])
            new_sound["left"].append(0)
        # adds number to right or left according to formula given
        else:
            new_sound["right"].append(
                sound["right"][i] * ((changing_scale) / (len_overall - 1))
            )
            new_sound["left"].append(
                sound["left"][i] * (1 - (changing_scale) / (len_overall - 1))
            )
            changing_scale += 1
    return new_sound


def remove_vocals(sound):
    #creates new sound to remove vocals from the original sound
    new_sound = {}
    new_sound["rate"] = sound["rate"]
    new_sound["samples"] = []
    len_sound = len(sound["left"])
    # compute difference of left and right samples of the stereo sound into new sound
    for i in range(len_sound):
        new_sound["samples"].append(sound["left"][i] - sound["right"][i])
    return new_sound=


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    mystery = load_wav("sounds/mystery.wav")
    write_wav(backwards(mystery), "mystery_reversed.wav")
    water = load_wav("sounds/water.wav")
    synth = load_wav("sounds/synth.wav")
    write_wav(mix(synth, water, 0.2), "mixed_synth_water.wav")
    car = load_wav("sounds/car.wav", stereo=True)
    write_wav(pan(car), "car_changed.wav")
    mountain = load_wav("sounds/lookout_mountain.wav", stereo=True)
    write_wav(remove_vocals(mountain), "mountain_no_vocals.wav")
    chord = load_wav("sounds/chord.wav")
    write_wav(echo(chord, 5, 0.3, 0.6), "echoed_chord.wav")
