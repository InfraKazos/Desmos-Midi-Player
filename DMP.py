from mido import MidiFile
import pyperclip
import sys

note_count_cutoff = 10000

def midi_to_frequency(midi_note):
    return 440 * 2 ** ((midi_note - 69) / 12)

def play_midi(file_path):
    global note_count_cutoff
    try:
        midi = MidiFile(file_path)
    except OSError:
        print("File does not exist.")
        sys.exit()

    active_notes = {}

    freq_list = []
    start_list = []
    duration_list = []
    sustain_list = []
    velocity_list = []
    midi_value_list = []

    sustain = False

    current_time = 0

    note_count = 0
    
    for message in midi:
        if message.is_meta:
            continue
        current_time += message.time

        if message.channel == 9:
            continue
        
        if message.type == 'note_on' and message.velocity > 0:
            active_notes[message.note] = (current_time, message.velocity / 127)
        
        elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
            if message.note in active_notes:
                start_time, velocity = active_notes.pop(message.note)
                end_time = current_time
                frequency = midi_to_frequency(message.note)
                freq_list.append(frequency)
                start_list.append(start_time)

                duration = end_time - start_time
                length = min(duration, 1)
                sustain_length = max(min(duration - length, 2.5), 0.3) if not sustain else 1 + max(duration - 1, 0)

                duration_list.append(length)
                sustain_list.append(sustain_length)

                velocity_list.append(velocity)
                midi_value_list.append(message.note)
                note_count += 1
                if note_count == note_count_cutoff:
                    print("Note count exceeds 10,000. It will be cut off.")
                    break
        elif message.type == "control_change" and message.control == 64:
            sustain = message.value > 0

                
    return freq_list, start_list, duration_list, sustain_list, velocity_list, midi_value_list
if len(sys.argv) < 2:
    print("Please input a file path")
    sys.exit()
file_path = sys.argv[1]
print("Encoding {}".format(file_path))
freq, start, duration, sustain, velocity, midi_values = play_midi(file_path)
pyperclip.copy("Calc.setExpressions([{id: 'Freq', latex:'f_{req}=*1'}, {id: 'Start', latex:'s_{tart}=*2'}, {id: 'Duration', latex:'d_{uration}=*3'}, {id: 'Sustain', latex:'s_{ustain}=*4'}, {id: 'Velocity', latex:'v_{elocity}=*5'}, {id: 'MidiValues', latex:'m_{idiValues}=*6'}])".replace("*1", repr(freq)).replace("*2", repr(start)).replace("*3", repr(duration)).replace("*4", repr(sustain)).replace("*5", repr(velocity)).replace("*6", repr(midi_values)))
print("Encoded {} notes. Copied to clipboard. Paste into console on the Desmos website.".format(len(freq)))
