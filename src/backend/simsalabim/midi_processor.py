import os
from mido import MidiFile
import numpy as np
import json

# Define paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
AUDIO_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets/audio'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets'))
INPUT_FILE = os.path.join(AUDIO_FOLDER, 'input.mid')

# Output files for specific channels
OUTPUT_FILES = {
    0: os.path.join(OUTPUT_DIR, 'midi_ch0.json'),
    1: os.path.join(OUTPUT_DIR, 'midi_ch1.json'),
    2: os.path.join(OUTPUT_DIR, 'midi_ch2.json'),
    10: os.path.join(OUTPUT_DIR, 'midi_ch10.json'),
}

OUTPUT_INPUT_FILES = {
    0: os.path.join(OUTPUT_DIR, 'midi_input_ch00.json'),
    1: os.path.join(OUTPUT_DIR, 'midi_input_ch01.json'),
    2: os.path.join(OUTPUT_DIR, 'midi_input_ch02.json'),
    10: os.path.join(OUTPUT_DIR, 'midi_input_ch10.json'),
}


def clear_existing_data(output_file):
    """Clear existing data in the output JSON file."""
    if os.path.exists(output_file):
        with open(output_file, 'w') as f:
            f.write("{}")  # Clear with an empty JSON object
        print(f"Cleared existing data in {output_file}")

def process_midi_files_by_channel(channel, output_file):
    """
    Processes MIDI files and extracts data for a specific channel using windowing logic.
    
    Args:
        channel (int): The MIDI channel to process (0-15).
        output_file (str): Path to save the JSON output.
    """
    midi_data = {}

    for file_name in os.listdir(AUDIO_FOLDER):
        # Skip 'input.mid' and process other MIDI files
        if file_name.endswith('.mid') and file_name != 'input.mid':
            file_path = os.path.join(AUDIO_FOLDER, file_name)
            midi = MidiFile(file_path)
            
            melody = []
            for track in midi.tracks:
                for msg in track:
                    if msg.type == 'note_on' and msg.channel == channel:
                        melody.append([msg.note, msg.time])
            
            # Apply windowing logic
            index_note = 0
            segments = 20  # Notes per segment
            windowing = 6  # Notes to overlap
            
            segment_list = []
            while index_note + segments <= len(melody):
                segment = melody[index_note:index_note + segments]
                
                # Separate the pitch and duration data for the segment
                pitches = [note for note, _ in segment]
                durations = [time for _, time in segment]
                
                # Calculate mean and std for pitch and duration
                pitch_mean = np.mean(pitches)
                pitch_std = np.std(pitches)
                duration_mean = np.mean(durations)
                duration_std = np.std(durations)
                
                # Normalize pitch and duration for each note in the segment
                normalized_segment = [
                    [
                        (note - pitch_mean) / pitch_std if pitch_std != 0 else 0,
                        (time - duration_mean) / duration_std if duration_std != 0 else 0
                    ]
                    for note, time in segment
                ]
                
                # Add the normalized segment to the segment list
                segment_list.append(normalized_segment)
                index_note += segments - windowing
            
            # Handle remaining notes if any
            if index_note < len(melody):
                segment = melody[index_note:]
                
                # Separate the pitch and duration data for the remaining segment
                pitches = [note for note, _ in segment]
                durations = [time for _, time in segment]
                
                # Calculate mean and std for pitch and duration
                pitch_mean = np.mean(pitches)
                pitch_std = np.std(pitches)
                duration_mean = np.mean(durations)
                duration_std = np.std(durations)
                
                # Normalize pitch and duration for each note in the remaining segment
                normalized_segment = [
                    [
                        (note - pitch_mean) / pitch_std if pitch_std != 0 else 0,
                        (time - duration_mean) / duration_std if duration_std != 0 else 0
                    ]
                    for note, time in segment
                ]
                
                # Add the normalized remaining segment to the segment list
                segment_list.append(normalized_segment)

            midi_data[file_name] = segment_list

    # Write to JSON file with the specified format
    with open(output_file, 'w') as f:
        formatted_json = "{\n"
        for file_name, segments in midi_data.items():
            formatted_json += f'    "{file_name}": [\n'
            segment_strings = []
            for segment in segments:
                segment_str = "        [" + ",".join(f"[{note},{time}]" for note, time in segment) + "]"
                segment_strings.append(segment_str)
            formatted_json += ",\n".join(segment_strings)
            formatted_json += "\n    ]"
            if file_name != list(midi_data.keys())[-1]:
                formatted_json += ","
            formatted_json += "\n"
        formatted_json += "}"
        f.write(formatted_json)
    print(f"Processed data for channel {channel} saved to {output_file}")

    
def process_midi_input_by_channel(channel, output_file):
    """
    Processes a single MIDI file and extracts data for a specific channel using windowing logic.
    
    Args:
        channel (int): The MIDI channel to process (0-15).
        output_file (str): Path to save the JSON output.
    """
    midi_data = {}

    # Open and process the input MIDI file
    midi = MidiFile(INPUT_FILE)
    
    melody = []
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.channel == channel:
                melody.append([msg.note, msg.time])
    
    # Apply windowing logic
    index_note = 0
    segments = 20  # Notes per segment
    windowing = 6  # Notes to overlap
    
    segment_list = []
    while index_note + segments <= len(melody):
        segment = melody[index_note:index_note + segments]
        
        # Separate the pitch and duration data for the segment
        pitches = [note for note, _ in segment]
        durations = [time for _, time in segment]
        
        # Calculate mean and std for pitch and duration
        pitch_mean = np.mean(pitches)
        pitch_std = np.std(pitches)
        duration_mean = np.mean(durations)
        duration_std = np.std(durations)
        
        # Normalize pitch and duration for each note in the segment
        normalized_segment = [
            [
                (note - pitch_mean) / pitch_std if pitch_std != 0 else 0,
                (time - duration_mean) / duration_std if duration_std != 0 else 0
            ]
            for note, time in segment
        ]
        
        segment_list.append(normalized_segment)
        index_note += segments - windowing
    
    # Handle remaining notes if any (less than 20 notes)
    if index_note < len(melody):
        segment = melody[index_note:]
        
        # Separate the pitch and duration data for the remaining segment
        pitches = [note for note, _ in segment]
        durations = [time for _, time in segment]
        
        # Calculate mean and std for pitch and duration
        pitch_mean = np.mean(pitches)
        pitch_std = np.std(pitches)
        duration_mean = np.mean(durations)
        duration_std = np.std(durations)
        
        # Normalize pitch and duration for each note in the remaining segment
        normalized_segment = [
            [
                (note - pitch_mean) / pitch_std if pitch_std != 0 else 0,
                (time - duration_mean) / duration_std if duration_std != 0 else 0
            ]
            for note, time in segment
        ]
        
        segment_list.append(normalized_segment)

    midi_data["input.mid"] = segment_list

    # Write to JSON file with the specified format
    with open(output_file, 'w') as f:
        formatted_json = "{\n"
        for file_name, segments in midi_data.items():
            formatted_json += f'    "{file_name}": [\n'
            segment_strings = []
            for segment in segments:
                segment_str = "        [" + ",".join(f"[{note},{time}]" for note, time in segment) + "]"
                segment_strings.append(segment_str)
            formatted_json += ",\n".join(segment_strings)
            formatted_json += "\n    ]"
            formatted_json += "\n"
        formatted_json += "}"
        f.write(formatted_json)
    print(f"Processed data for channel {channel} saved to {output_file}")




def ATB():
    """
    Processes all relevant JSON files in the 'datasets' folder to compute the Absolute Tone Based (ATB) histogram
    for each segment in each MIDI file, and outputs the normalized histogram as a probability distribution.
    Generates individual ATB files per input JSON (e.g., atb_input_ch00.json).
    """
    # Define the input and output directories
    datasets_folder = os.path.join(BASE_DIR, 'datasets')  # Adjusted path
    atb_folder = os.path.join(OUTPUT_DIR, 'ATB')

    # Create the ATB folder if it doesn't exist
    if not os.path.exists(atb_folder):
        os.makedirs(atb_folder)
    
    # Iterate through all JSON files in the datasets folder
    for file_name in os.listdir(datasets_folder):
        if not file_name.endswith('.json'):
            continue

        file_path = os.path.join(datasets_folder, file_name)
        print(f"Processing {file_name}...")

        # Read the JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Process each song in the JSON file
        for song_name, song_data in data.items():
            print(f"  Processing song: {song_name}")

            # Initialize the list to store histograms for each segment
            song_histograms = []

            # Process each segment in the song
            for segment in song_data:
                # Initialize the histogram for this segment
                histogram = [0] * 128  # A histogram for the 0-127 MIDI note range
                total_notes = 0

                # Process each note in the segment
                for note_time in segment:  # Each element is a [note, time] pair
                    note, time = note_time  # Note and time (normalized as floats)
                    
                    try:
                        # Convert the note (which is normalized) to the 0-127 range for histogram
                        if 0 <= note <= 1:
                            # Scale the normalized value back to a MIDI note range (0-127)
                            midi_note = int(np.clip(note * 127, 0, 127))  # Map the float to 0-127 range
                            histogram[midi_note] += 1
                            total_notes += 1
                    except ValueError:
                        continue  # If the note value is not valid, skip it

                # Normalize the histogram for the segment to make it a probability distribution
                if total_notes > 0:
                    histogram = [x / total_notes for x in histogram]
                
                # Append the histogram of the current segment to the song's list
                song_histograms.append(histogram)
            
            # Save the histograms for this song to a JSON file
            output_file = os.path.join(atb_folder, f'atb_{file_name}')
            
            # Write the histograms to the file in JSON format
            with open(output_file, 'w') as f:
                json.dump({song_name: song_histograms}, f, indent=4)

            print(f"Processed ATB data for {song_name} and saved to {output_file}")








if __name__ == "__main__":
    # Clear existing data
    for channel, output_file in OUTPUT_FILES.items():
        clear_existing_data(output_file)

    # Process channels
    for channel, output_file in OUTPUT_FILES.items():
        process_midi_files_by_channel(channel, output_file)
    
        # Clear existing data for each output file
    for channel, output_file in OUTPUT_INPUT_FILES.items():
        clear_existing_data(output_file)

    # Process channels 0, 1, 2, 10 for the input MIDI file
    for channel, output_file in OUTPUT_INPUT_FILES.items():
        process_midi_input_by_channel(channel, output_file)
    
    ATB()
