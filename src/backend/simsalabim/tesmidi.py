import os
import json
import mido
import numpy as np
from scipy.spatial.distance import cosine

def process_midi_file_timing(file_path, channel, use_delta=True):
    mid = mido.MidiFile(file_path)
    notes_and_timing = extract_notes_and_timing_by_channel(mid, channel, use_delta)
    
    if notes_and_timing is None:
        return []

    segments = []
    segment_length = 20
    sliding_window = 6
    i = 0

    while i + segment_length <= len(notes_and_timing):
        # Create a segment of length 20
        segment = notes_and_timing[i:i + segment_length]
        
        # Normalize both notes and timing in the segment
        normalized_segment = normalize_segment2(segment, 'note')
        normalized_segment = normalize_segment2(normalized_segment, 'time')
        
        segments.append(normalized_segment)
        
        i += segment_length
        i -= sliding_window

    return segments

def process_all_midi_files_timing(folder_path, channel, use_delta=True):
    midi_data = {}
    
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mid'):
            file_path = os.path.join(folder_path, file_name)
            segments = process_midi_file_timing(file_path, channel, use_delta)
            if segments:
                midi_data[file_name] = segments
    
    return midi_data

def process_and_save_timing_data(folder_path):
    channels = [0, 1, 2, 10]
    
    # Process delta times
    for channel in channels:
        midi_data = process_all_midi_files_timing(folder_path, channel, use_delta=True)
        if midi_data:
            json_file_path = os.path.join(folder_path, f'midi_delta_time_channel_{channel}.json')
            with open(json_file_path, 'w') as json_file:
                json.dump(midi_data, json_file, indent=4)
            print(f"Delta time data for channel {channel} has been saved to {json_file_path}")
        else:
            print(f"No delta time data found for channel {channel}")
    
    # Process absolute times
    for channel in channels:
        midi_data = process_all_midi_files_timing(folder_path, channel, use_delta=False)
        if midi_data:
            json_file_path = os.path.join(folder_path, f'midi_absolute_time_channel_{channel}.json')
            with open(json_file_path, 'w') as json_file:
                json.dump(midi_data, json_file, indent=4)
            print(f"Absolute time data for channel {channel} has been saved to {json_file_path}")
        else:
            print(f"No absolute time data found for channel {channel}")
def normalize_segment2(segment, key='note'):
    values = [item[key] for item in segment]
    values_array = np.array(values, dtype=float)
    
    # Calculate mean and standard deviation
    mean = np.mean(values_array)
    std = np.std(values_array)
    
    # Avoid division by zero
    if std == 0:
        return segment
    
    # Normalize
    normalized = (values_array - mean) / std
    
    # Scale to 0-127 range
    min_val = np.min(normalized)
    max_val = np.max(normalized)
    scaled = ((normalized - min_val) * (127 - 0)/(max_val - min_val) + 0)
    rounded = np.round(scaled)
    clipped = np.clip(rounded, 0, 127)
    
    # Create new normalized segment
    normalized_segment = []
    for i, item in enumerate(segment):
        normalized_item = item.copy()
        normalized_item[key] = int(clipped[i])
        normalized_segment.append(normalized_item)
    
    return normalized_segment

def extract_notes_and_timing_by_channel(mid, target_channel, use_delta=True):
    notes_and_timing = []
    cumulative_time = 0
    last_note_time = 0
    
    for track in mid.tracks:
        for msg in track:
            cumulative_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0 and msg.channel == target_channel:
                if use_delta:
                    # Calculate time since last note
                    time_value = cumulative_time - last_note_time
                    last_note_time = cumulative_time
                else:
                    # Use absolute time
                    time_value = cumulative_time
                
                notes_and_timing.append({
                    'note': msg.note,
                    'time': time_value
                })
    
    return notes_and_timing if notes_and_timing else None

def extract_melody_track_by_channel(mid, target_channel):
    notes_by_channel = []
    
    for track in mid.tracks:
        track_notes = []
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0 and msg.channel == target_channel:
                track_notes.append(msg.note)
        if track_notes:
            notes_by_channel.extend(track_notes)
    
    return notes_by_channel if notes_by_channel else None

def normalize_segment(segment):
    # Convert to numpy array for easier calculations
    segment_array = np.array(segment, dtype=float)
    
    # Calculate mean and standard deviation for this segment
    mean = np.mean(segment_array)
    std = np.std(segment_array)
    
    # Avoid division by zero
    if std == 0:
        return segment  # Return original segment if std is 0
    
    # Apply the normalization formula: (note - μ) / σ
    normalized = (segment_array - mean) / std
    
    # Find the min and max of normalized values
    min_val = np.min(normalized)
    max_val = np.max(normalized)
    
    # Scale to 0-127 range using the formula: (x - min) * (newmax - newmin)/(max - min) + newmin
    scaled = ((normalized - min_val) * (127 - 0)/(max_val - min_val) + 0)
    
    # Round to nearest integer
    rounded = np.round(scaled)
    
    # Clip to ensure we're within MIDI bounds
    clipped = np.clip(rounded, 0, 127)
    
    return clipped.astype(int).tolist()

def process_midi_file(file_path, channel):
    mid = mido.MidiFile(file_path)
    notes = extract_melody_track_by_channel(mid, channel)
    
    if notes is None:
        return []

    segments = []
    segment_length = 20
    sliding_window = 6
    i = 0

    while i + segment_length <= len(notes):
        # Create a segment of length 20
        segment = notes[i:i + segment_length]
        
        # Normalize the segment
        normalized_segment = normalize_segment(segment)
        
        segments.append(normalized_segment)
        
        # Move forward by segment_length then back by sliding_window
        i += segment_length
        i -= sliding_window
    print(f"DEBUG: Successfully processed all MIDI files in channel: {channel}.")
    return segments

def process_all_midi_files(folder_path, channel):
    midi_data = {}
    
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mid'):
            file_path = os.path.join(folder_path, file_name)
            try:
                segments = process_midi_file(file_path, channel)
                if segments:  # Only add to midi_data if segments were found
                    midi_data[file_name] = segments
            except OSError as e:
                print(f"Skipping corrupted file: {file_name}. Error: {e}")
            except Exception as e:
                print(f"Unexpected error processing {file_name}: {e}")
    
    return midi_data


def create_atb_histogram(segment):
    """
    Creates an Absolute Tone Based (ATB) histogram for a segment.
    
    Args:
        segment: List of normalized MIDI notes (0-127)
    
    Returns:
        Normalized histogram array with 128 bins
    """
    # Create histogram with 128 bins (0-127)
    hist, _ = np.histogram(segment, bins=128, range=(0, 128))
    
    # Normalize the histogram (if sum is 0, return zeros)
    hist_sum = np.sum(hist)
    if hist_sum > 0:
        normalized_hist = hist / hist_sum
    else:
        normalized_hist = np.zeros(128)
    
    return normalized_hist.tolist()

def process_midi_data_to_atb(input_json_path, output_json_path):
    """
    Processes MIDI data from input JSON and creates ATB histograms.
    
    Args:
        input_json_path: Path to input JSON file with normalized segments
        output_json_path: Path to save the ATB histogram data
    """
    # Load the input JSON data
    with open(input_json_path, 'r') as f:
        midi_data = json.load(f)
    
    # Dictionary to store ATB histograms
    atb_data = {}
    
    # Process each MIDI file
    for file_name, segments in midi_data.items():
        file_histograms = []
        
        # Create histogram for each segment
        for segment in segments:
            histogram = create_atb_histogram(segment)
            file_histograms.append(histogram)
        
        atb_data[file_name] = file_histograms
    
    # Save the ATB histogram data
    with open(output_json_path, 'w') as f:
        json.dump(atb_data, f, indent=4)

def process_all_channels_atb(base_folder):
    """
    Processes ATB histograms for all channels.
    
    Args:
        base_folder: Folder containing the MIDI data JSON files
    """
    channels = [0, 1, 2, 10]
    
    for channel in channels:
        input_json = os.path.join(base_folder, f'midi_data_channel_{channel}.json')
        output_json = os.path.join(base_folder, f'atb_histogram_channel_{channel}.json')
        
        if os.path.exists(input_json):
            process_midi_data_to_atb(input_json, output_json)
            print(f"ATB histograms for channel {channel} saved to {output_json}")
        else:
            print(f"No input data found for channel {channel}")


def create_rtb_histogram(segment):
    """
    Creates a Relative Tone Based (RTB) histogram for a segment.
    Analyzes changes between consecutive notes, creating a histogram
    with values from -127 to +127.
    
    Args:
        segment: List of normalized MIDI notes
    
    Returns:
        Normalized histogram array with 255 bins representing intervals from -127 to +127
    """
    if len(segment) < 2:
        return np.zeros(255).tolist()
    
    # Calculate intervals between consecutive notes (no shifting needed)
    intervals = np.diff(segment)
    
    # Create histogram with 255 bins for range -127 to +127
    hist, _ = np.histogram(intervals, bins=255, range=(-127, 128))
    
    # Normalize the histogram
    hist_sum = np.sum(hist)
    if hist_sum > 0:
        normalized_hist = hist / hist_sum
    else:
        normalized_hist = np.zeros(255)
    
    return normalized_hist.tolist()

def create_ftb_histogram(segment):
    """
    Creates a First Tone Based (FTB) histogram for a segment.
    Analyzes differences between each note and the first note,
    creating a histogram with values from -127 to +127.
    
    Args:
        segment: List of normalized MIDI notes
    
    Returns:
        Normalized histogram array with 255 bins representing intervals from -127 to +127
    """
    if len(segment) < 2:
        return np.zeros(255).tolist()
    
    # Calculate intervals relative to the first note (no shifting needed)
    first_note = segment[0]
    intervals = [note - first_note for note in segment[1:]]
    
    # Create histogram with 255 bins for range -127 to +127
    hist, _ = np.histogram(intervals, bins=255, range=(-127, 128))
    
    # Normalize the histogram
    hist_sum = np.sum(hist)
    if hist_sum > 0:
        normalized_hist = hist / hist_sum
    else:
        normalized_hist = np.zeros(255)
    
    return normalized_hist.tolist()

def process_midi_data_to_rtb_ftb(input_json_path, output_rtb_path, output_ftb_path):
    """
    Processes MIDI data from input JSON and creates both RTB and FTB histograms.
    
    Args:
        input_json_path: Path to input JSON file with normalized segments
        output_rtb_path: Path to save the RTB histogram data
        output_ftb_path: Path to save the FTB histogram data
    """
    # Load the input JSON data
    with open(input_json_path, 'r') as f:
        midi_data = json.load(f)
    
    # Dictionaries to store histograms
    rtb_data = {}
    ftb_data = {}
    
    # Process each MIDI file
    for file_name, segments in midi_data.items():
        rtb_histograms = []
        ftb_histograms = []
        
        # Create histograms for each segment
        for segment in segments:
            rtb_histogram = create_rtb_histogram(segment)
            ftb_histogram = create_ftb_histogram(segment)
            rtb_histograms.append(rtb_histogram)
            ftb_histograms.append(ftb_histogram)
        
        rtb_data[file_name] = rtb_histograms
        ftb_data[file_name] = ftb_histograms
    
    # Save the histogram data
    with open(output_rtb_path, 'w') as f:
        json.dump(rtb_data, f, indent=4)
    with open(output_ftb_path, 'w') as f:
        json.dump(ftb_data, f, indent=4)

def process_all_channels_rtb_ftb(base_folder):
    """
    Processes RTB and FTB histograms for all channels.
    
    Args:
        base_folder: Folder containing the MIDI data JSON files
    """
    channels = [0, 1, 2, 10]
    
    for channel in channels:
        input_json = os.path.join(base_folder, f'midi_data_channel_{channel}.json')
        output_rtb = os.path.join(base_folder, f'rtb_histogram_channel_{channel}.json')
        output_ftb = os.path.join(base_folder, f'ftb_histogram_channel_{channel}.json')
        
        if os.path.exists(input_json):
            process_midi_data_to_rtb_ftb(input_json, output_rtb, output_ftb)
            print(f"RTB and FTB histograms for channel {channel} saved to {output_rtb} and {output_ftb}")
        else:
            print(f"No input data found for channel {channel}")



def calculate_histogram_similarity(hist1, hist2):
    """
    Calculates similarity between two histograms using cosine similarity.
    
    Args:
        hist1, hist2: Normalized histogram arrays
    
    Returns:
        Similarity score between 0 and 1
    """
    h1 = np.array(hist1)
    h2 = np.array(hist2)
    return 1 - cosine(h1, h2)

def compare_segments_to_dataset(json_path):
    """
    Compares each segment of input.mid with all segments in the dataset
    from a single histogram file (ATB, RTB, or FTB).
    
    Args:
        json_path: Path to the histogram JSON file
    
    Returns:
        Dictionary with max similarities per segment for each song
    """
    # Load the histogram data
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    if "input.mid" not in data:
        print(f"'input.mid' not found in file: {json_path}")
        return {}
    
    # Get input.mid segments
    input_segments = data["input.mid"]
    
    # Initialize results dictionary
    results = {}
    
    # Process each song (except input.mid)
    for song_name, song_segments in data.items():
        if song_name == "input.mid":
            continue
            
        # For each input segment, find its maximum similarity with any segment in current song
        max_similarities = []
        for input_segment in input_segments:
            max_sim = max(
                calculate_histogram_similarity(input_segment, song_seg)
                for song_seg in song_segments
            )
            max_similarities.append(max_sim)
        
        results[song_name] = max_similarities
    
    return results

def calculate_weighted_similarity(atb_results, rtb_results, ftb_results):
    """
    Calculates weighted similarity scores across all features.
    
    Args:
        atb_results, rtb_results, ftb_results: Dictionaries containing similarity scores
    
    Returns:
        Dictionary with weighted similarity scores
    """
    weights = {'atb': 0.15, 'rtb': 0.60, 'ftb': 0.25}
    weighted_results = {}
    
    for song_name in atb_results.keys():
        weighted_sims = []
        for i in range(len(atb_results[song_name])):
            weighted_sim = (
                weights['atb'] * atb_results[song_name][i] +
                weights['rtb'] * rtb_results[song_name][i] +
                weights['ftb'] * ftb_results[song_name][i]
            )
            weighted_sims.append(weighted_sim)
        weighted_results[song_name] = weighted_sims
    
    return weighted_results

def process_channel_similarities(base_folder, channel):
    """
    Process similarities for a specific channel.
    
    Args:
        base_folder: Base folder containing histogram files
        channel: Channel number to process
    """
    # Define paths for each histogram type
    atb_path = os.path.join(base_folder, f'atb_histogram_channel_{channel}.json')
    rtb_path = os.path.join(base_folder, f'rtb_histogram_channel_{channel}.json')
    ftb_path = os.path.join(base_folder, f'ftb_histogram_channel_{channel}.json')
    
    # Calculate similarities for each feature type
    atb_results = compare_segments_to_dataset(atb_path)
    rtb_results = compare_segments_to_dataset(rtb_path)
    ftb_results = compare_segments_to_dataset(ftb_path)
    
    # Calculate weighted similarities
    weighted_results = calculate_weighted_similarity(atb_results, rtb_results, ftb_results)
    
    # Save results
    output_files = {
        f'atb_similarities_channel_{channel}.json': atb_results,
        f'rtb_similarities_channel_{channel}.json': rtb_results,
        f'ftb_similarities_channel_{channel}.json': ftb_results,
        f'weighted_similarities_channel_{channel}.json': weighted_results
    }
    
    for filename, results in output_files.items():
        output_path = os.path.join(base_folder, filename)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Saved {filename}")

def process_all_channels(base_folder):
    """
    Process similarities for all channels.
    
    Args:
        base_folder: Folder containing histogram files
    """
    channels = [0, 1, 2, 10]
    for channel in channels:
        print(f"\nProcessing channel {channel}...")
        process_channel_similarities(base_folder, channel)


def calculate_highest_similarity(base_folder):
    """
    Calculate the highest similarity percentage from weighted similarity files.
    
    Args:
        base_folder: Path to the folder containing weighted similarity JSON files.
    
    Returns:
        Dictionary with the highest similarity song and its value in percentage.
    """
    channels = [0, 1, 2, 10]
    song_avg_similarity = {}

    for channel in channels:
        file_path = os.path.join(base_folder, f'weighted_similarities_channel_{channel}.json')

        # Skip if the file does not exist or is empty
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            print(f"DEBUG: Skipping empty or missing file: {file_path}")
            continue

        try:
            with open(file_path, 'r') as f:
                channel_data = json.load(f)
        except json.JSONDecodeError:
            print(f"DEBUG: Skipping invalid JSON file: {file_path}")
            continue

        # Process each song's similarity values
        for song_name, similarities in channel_data.items():
            # If the song has no similarities (empty list), treat its average as 0
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0

            if song_name not in song_avg_similarity:
                song_avg_similarity[song_name] = []

            song_avg_similarity[song_name].append(avg_similarity)

    # Calculate overall average similarity across all valid channels
    overall_avg_similarity = {}
    for song_name, avg_list in song_avg_similarity.items():
        if not avg_list:  # Skip songs with no data
            continue
        overall_avg_similarity[song_name] = sum(avg_list) / len(avg_list)

    # If no valid songs are found, return a default response
    if not overall_avg_similarity:
        return {
            "song": None,
            "similarity_percentage": 0
        }

    # Find the song with the highest similarity
    best_song = max(overall_avg_similarity, key=overall_avg_similarity.get)
    best_value = overall_avg_similarity[best_song] * 100  # Convert to percentage
    print({best_song}, {round(best_value, 2)})
    return {
        "song": best_song,
        "similarity_percentage": round(best_value, 2)
    }

        

# Path to the folder containing MIDI files
AUDIO_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets/audio'))

# List of channels to process
channels = [0, 1, 2, 10]


# Process each channel separately
for channel in channels:
    # Process all MIDI files in the folder for this channel
    midi_data = process_all_midi_files(AUDIO_FOLDER, channel)
    
    # Only create a JSON file if there's data for this channel
    if midi_data:
        # Save the extracted data to a JSON file inside the same folder
        json_file_path = os.path.join(AUDIO_FOLDER, f'midi_data_channel_{channel}.json')
        with open(json_file_path, 'w') as json_file:
            json.dump(midi_data, json_file, indent=4)
        print(f"Data for channel {channel} has been successfully extracted and saved to {json_file_path}.")
    else:
        print(f"No data found for channel {channel}.")


process_all_channels_atb(AUDIO_FOLDER)
#process_and_save_timing_data(AUDIO_FOLDER)
process_all_channels_rtb_ftb(AUDIO_FOLDER)
process_all_channels(AUDIO_FOLDER)
calculate_highest_similarity(AUDIO_FOLDER)