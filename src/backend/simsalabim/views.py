from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str
import glob  # For matching file patterns
import os
import zipfile
import json
from imageprocessing import *
import numpy as np
from PIL import Image

from .tesmidi import (
    process_all_channels_atb,
    process_all_channels_rtb_ftb,
    process_all_channels,
    process_all_midi_files,
    process_midi_file,
    extract_melody_track_by_channel,
    normalize_segment,
    calculate_highest_similarity
)

AUDIO_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets/audio'))

# Base directory and datasets folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, 'datasets')
JSON_DIR = os.path.join(BASE_DIR, 'datasets/mapper')

# Ensure the datasets folder exists
if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)

@api_view(['GET'])
def test_connection(request):
    return Response({
        "message": "Successfully connected to Django backend!"
    })

import glob  # For matching file patterns

def delete_files_by_extension(folder_path, extensions):
    """
    Deletes all files in a folder matching the specified extensions.
    Args:
        folder_path (str): Path to the target folder.
        extensions (list): List of file extensions to delete (e.g., ['*.mid', '*.png']).
    """
    for ext in extensions:
        files = glob.glob(os.path.join(folder_path, ext))
        for file in files:
            try:
                os.remove(file)
                print(f"DEBUG: Deleted file: {file}")
            except OSError as e:
                print(f"ERROR: Failed to delete file {file}: {e}")

@api_view(['POST'])
def handle_zip_upload(request):
    folder = request.POST.get('folder')
    if not folder:
        return JsonResponse({'message': 'No target folder specified!'}, status=400)

    target_dir = os.path.join(DATASET_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_path = os.path.join(target_dir, uploaded_file.name)

        # Save the uploaded file
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Validate ZIP contents
        allowed_extensions = {'.mid'} if folder == 'audio' else {'.png', '.jpeg', '.jpg'}
        try:
            is_valid, invalid_file = validate_zip_contents(file_path, allowed_extensions)
            if not is_valid:
                os.remove(file_path)  # Clean up the invalid file
                allowed_types = " or ".join(allowed_extensions)
                return JsonResponse({'message': f'Invalid file in ZIP: {invalid_file}. Only {allowed_types} files are allowed.'}, status=400)

            # Extract valid ZIP contents and flatten structure
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    # Skip directories and __MACOSX directory
                    if member.startswith('__MACOSX/') or member.endswith('/'):
                        continue
                    
                    # Extract the file directly to the target directory
                    filename = os.path.basename(member)
                    if filename:  # Ensure it's a valid file
                        target_path = os.path.join(target_dir, filename)
                        with zip_ref.open(member) as source_file:
                            with open(target_path, 'wb') as output_file:
                                output_file.write(source_file.read())

            os.remove(file_path)  # Remove the original ZIP file
            return JsonResponse({'message': f'File uploaded and extracted to {folder} successfully!'})
        except zipfile.BadZipFile:
            os.remove(file_path)
            return JsonResponse({'message': 'Invalid ZIP file!'}, status=400)

    return JsonResponse({'message': 'No file uploaded!'}, status=400)


def validate_zip_contents(zip_file_path, allowed_extensions):
    """
    Validates that all files inside the ZIP file have the allowed extensions.
    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            # Skip directories
            if member.endswith('/'):
                continue

            filename = os.path.basename(member)
            if filename:  # Ensure it's a file, not a folder
                _, ext = os.path.splitext(filename)
                if ext.lower() not in allowed_extensions:
                    return False, filename
    return True, None



@api_view(['POST'])
def handle_json_upload(request):
    folder = request.POST.get('folder')
    if not folder:
        return JsonResponse({'message': 'No target folder specified!'}, status=400)

    target_dir = os.path.join(DATASET_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        if not uploaded_file.name.endswith('.json'):
            return JsonResponse({'message': 'Only .json files are allowed!'}, status=400)

        file_path = os.path.join(target_dir, uploaded_file.name)

        # Save the uploaded file
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        try:
            with open(file_path, 'r') as f:
                json.load(f)  # Validate JSON content
            return JsonResponse({'message': f'JSON file uploaded successfully to {folder}!'})
        except json.JSONDecodeError:
            os.remove(file_path)
            return JsonResponse({'message': 'Invalid JSON file!'}, status=400)

    return JsonResponse({'message': 'No file uploaded!'}, status=400)



@api_view(['POST'])
def handle_mid_upload(request):
    folder = request.POST.get('folder')  # Retrieve the folder name from the request
    if not folder:
        return JsonResponse({'message': 'No target folder specified!'}, status=400)

    target_dir = os.path.join(DATASET_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)  # Ensure the target directory exists

    # Delete existing input.mid if it exists
    existing_file_path = os.path.join(target_dir, 'input.mid')
    if os.path.exists(existing_file_path):
        try:
            os.remove(existing_file_path)
            print(f"DEBUG: Deleted existing file: {existing_file_path}")
        except OSError as e:
            return JsonResponse({'message': f'Error deleting existing input.mid: {e}'}, status=500)

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Check if the file has a .mid extension
        if not uploaded_file.name.lower().endswith('.mid'):
            return JsonResponse({'message': 'Invalid file type! Only .mid files are allowed.'}, status=400)

        # Rename the file to "input.mid"
        renamed_file_path = os.path.join(target_dir, 'input.mid')

        # Save the uploaded file with the new name
        with default_storage.open(renamed_file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        print(f"DEBUG: Uploaded and renamed file to: {renamed_file_path}")

        try:
            channels = [0, 1, 2, 10]
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
            print(f"DEBUG: Successfully processed all MIDI files in {AUDIO_FOLDER} for channels {channels}.")
        except Exception as e:
            return JsonResponse({'message': f'Error during processing MIDI files: {str(e)}'}, status=500)

        try:
            process_all_channels_atb(target_dir)
            process_all_channels_rtb_ftb(target_dir)
        except Exception as e:
            return JsonResponse({'message': f'Error during histogram processing: {str(e)}'}, status=500)

        try:
            process_all_channels(target_dir)
        except Exception as e:
            return JsonResponse({'message': f'Error during channel similarity processing: {str(e)}'}, status=500)


        return JsonResponse({'message': f'MIDI file uploaded and processed successfully to {folder} as input.mid!'})

    return JsonResponse({'message': 'No file uploaded!'}, status=400)

@api_view(['GET'])
def audio_search_result(request):
    """
    API endpoint to calculate and return the best matching song,
    its similarity percentage, and provide the .mid file for download.
    """
    base_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets/audio'))

    try:
        # Calculate highest similarity
        result = calculate_highest_similarity(base_folder)
        best_song = result.get("song")
        similarity_percentage = result.get("similarity_percentage")

        if not best_song:
            return JsonResponse({
                "error": "No matching song found."
            }, status=404)

        # Construct the absolute path to the best song
        file_path = os.path.join(base_folder, best_song)

        # Check if the .mid file exists
        if not os.path.exists(file_path):
            return HttpResponseNotFound(f"File '{best_song}' not found on the server.")

        # Return JSON response with file link and similarity percentage
        response_data = {
            "best_song": best_song,
            "similarity_percentage": similarity_percentage,
            "file_path": request.build_absolute_uri(f'/api/download/{best_song}')
        }
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            "error": f"An error occurred: {str(e)}"
        }, status=500)


@api_view(['GET'])
def download_audio_file(request, filename):
    """
    API endpoint to serve the .mid file for download.
    """
    base_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets/audio'))
    file_path = os.path.join(base_folder, filename)

    try:
        if not os.path.exists(file_path):
            return HttpResponseNotFound(f"File '{filename}' not found on the server.")

        # Serve the file as a downloadable stream
        response = FileResponse(open(file_path, 'rb'), content_type='audio/midi')
        response['Content-Disposition'] = f'attachment; filename="{smart_str(filename)}"'
        return response
    except Exception as e:
        return JsonResponse({
            "error": f"An error occurred while serving the file: {str(e)}"
        }, status=500)

@api_view(['GET'])
def fetch_mapper_json(request):
    try:
        # Pastikan direktori 'mapper' ada
        if not os.path.exists(JSON_DIR):
            return JsonResponse({'message': 'Mapper directory does not exist!'}, status=404)

        # Cari file JSON dalam folder mapper
        json_files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]
        if not json_files:
            return JsonResponse({'message': 'No JSON file found in mapper directory!'}, status=404)
        
        # Asumsi hanya ada 1 file JSON
        json_file_path = os.path.join(JSON_DIR, json_files[0])
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

        return JsonResponse({'data': json_data}, status=200)
    except Exception as e:
        return JsonResponse({'message': f'Error reading JSON file: {str(e)}'}, status=500)

@api_view(['POST'])
def handle_cover_upload(request):
    folder = request.POST.get('folder')  # Retrieve the folder name from the request
    if not folder:
        return JsonResponse({'message': 'No target folder specified!'}, status=400)

    target_dir = os.path.join(DATASET_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)  # Ensure the target directory exists

    input_image_name = 'input_image'

    # Look for existing input_image files in the target directory
    existing_file_path = None
    for filename in os.listdir(target_dir):
        if filename.startswith(input_image_name):
            existing_file_path = os.path.join(target_dir, filename)
            print(f"Found file: {existing_file_path}")
            break

    # If an existing file is found, delete it
    if existing_file_path and os.path.exists(existing_file_path):
        try:
            os.remove(existing_file_path)
            print(f"DEBUG: Deleted existing file: {existing_file_path}")
        except OSError as e:
            return JsonResponse({'message': f'Error deleting existing file: {e}'}, status=500)

    # Handle file upload
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Check if the file has a valid extension
        if not uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return JsonResponse({'message': 'Invalid file type! Only .jpg, .jpeg, and .png files are allowed.'}, status=400)

        # Retain the original file extension
        _, file_extension = os.path.splitext(uploaded_file.name)
        renamed_file_path = os.path.join(target_dir, f'input_image{file_extension}')

        # Save the uploaded file with the new name
        with default_storage.open(renamed_file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        print(f"DEBUG: Uploaded and renamed file to: {renamed_file_path}")

        return JsonResponse({'message': f'Cover file uploaded and processed successfully to {folder} as input_image!'}, status=200)

    return JsonResponse({'message': 'No file uploaded!'}, status=400)


def process_image(image_path):
    output_size = (128, 128)
    img = Image.open(image_path)
    img_resized = img.resize(output_size)

    img_array = np.array(img_resized)
    if len(img_array.shape) == 3:  # RGB
        R, G, B = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        grayscale = 0.2989 * R + 0.5870 * G + 0.1140 * B  # Convert to grayscale
    else:
        grayscale = img_array  # Already grayscale

    return grayscale.flatten().tolist()  # Flatten as 1D list to store in JSON

def calculate_similarity_percentage(distance, max_distance):
    """
    Menghitung persentase kemiripan berdasarkan jarak Euclidean.
    """
    similarity = max(0, (1 - (distance / max_distance)) * 100)
    return similarity

def find_similar_images(input_image_path, Uk_numpy, pixel_means, image_vectors, image_names, top_k=5):
    input_vector = process_image(input_image_path)
    input_vector_centered = input_vector - pixel_means
    projected_input = np.dot(input_vector_centered, Uk_numpy)

    distances = []
    for idx, image_vector in enumerate(image_vectors):
        projected_vector = np.dot(image_vector - pixel_means, Uk_numpy)
        distance = np.linalg.norm(projected_input - projected_vector)
        distances.append((image_names[idx], distance))

    # Tentukan jarak maksimum
    max_distance = max([d[1] for d in distances]) if distances else 1.0

    # Hitung persentase kemiripan
    results = [
        (name, distance, calculate_similarity_percentage(distance, max_distance))
        for name, distance in distances
    ]

    # Urutkan berdasarkan jarak
    results = sorted(results, key=lambda x: x[1])
    return results[:top_k]

@api_view(['GET'])
def cover_search_result(request):
    try:
        base_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets/cover'))

        if not os.path.exists(base_folder):
            return JsonResponse({"error": "Base folder does not exist."}, status=404)

        image_files = [
            f for f in os.listdir(base_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]

        if not image_files:
            return JsonResponse({"error": "No images found in the folder."}, status=404)

        input_image_path = None
        for filename in image_files:
            if filename.lower().startswith('input_image'):
                input_image_path = os.path.join(base_folder, filename)
                break

        if not input_image_path:
            return JsonResponse({"error": "Input image not found."}, status=404)

        image_vectors = []
        image_names = []

        for image_file in image_files:
            img_path = os.path.join(base_folder, image_file)
            vector = process_image(img_path)
            image_vectors.append(vector)
            image_names.append(image_file)

        image_vectors = np.array(image_vectors)

        if image_vectors.ndim == 1:
            image_vectors = image_vectors.reshape(1, -1)

        pixel_means = np.mean(image_vectors, axis=0)
        centered_image_vectors = image_vectors - pixel_means

        # SVD PCA
        U_numpy, Sigma_numpy, Vt_numpy = np.linalg.svd(centered_image_vectors, full_matrices=False)

        k = 2
        Uk_numpy = Vt_numpy[:k].T

        similar_images = find_similar_images(input_image_path, Uk_numpy, pixel_means, image_vectors, image_names, top_k=5)
        best_cover, distance, similarity_percentage = similar_images[1]

        response_data = {
            "best_cover": best_cover,
            "similarity_distance": distance,
            "similarity_percentage": similarity_percentage,
            "file_path": request.build_absolute_uri(f'/api/download/{best_cover}')
        }
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@api_view(['GET'])
def download_cover_file(request, filename):
    """
    API endpoint to serve the .mid file for download.
    """
    base_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datasets/cover'))
    file_path = os.path.join(base_folder, filename)

    try:
        if not os.path.exists(file_path):
            return HttpResponseNotFound(f"File '{filename}' not found on the server.")

        # Serve the file as a downloadable stream
        response = FileResponse(open(file_path, 'rb'), content_type='audio/midi')
        response['Content-Disposition'] = f'attachment; filename="{smart_str(filename)}"'
        return response
    except Exception as e:
        return JsonResponse({
            "error": f"An error occurred while serving the file: {str(e)}"
        }, status=500)

