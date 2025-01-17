import os
import json
import numpy as np
from PIL import Image

# Fungsi untuk konversi gambar menjadi grayscale
def convert_to_grayscale(image):
    img_array = np.array(image)
    if img_array.shape[-1] == 3:  # pastikan gambar memiliki 3 channel RGB
        R, G, B = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        grayscale = 0.2989 * R + 0.5870 * G + 0.1140 * B
        return grayscale
    else:
        raise ValueError("gambar tidak memiliki 3 channel RGB.")

# Fungsi untuk memproses gambar (resize, konversi grayscale, flatten)
def process_image(image_path, output_size=(128, 128)):
    img = Image.open(image_path)
    img_resized = img.resize(output_size)
    grayscale_matrix = convert_to_grayscale(img_resized)
    grayscale_vector = grayscale_matrix.flatten()
    return grayscale_vector

# Fungsi untuk membaca metadata dan memproses gambar
def load_and_process_images(metadata_file):
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    image_vectors = []
    for data in metadata:
        img_path = data["pic_name"]
        if os.path.isfile(img_path):
            vector = process_image(img_path)
            image_vectors.append(vector)
        else:
            print(f"gambar tidak ditemukan: {img_path}")
    
    return np.array(image_vectors), metadata

# Fungsi untuk menghitung proyeksi PCA dan mengembalikan hasilnya
def compute_pca(image_vectors):
    # data centering
    pixel_means = np.mean(image_vectors, axis=0)
    centered_image_vectors = image_vectors - pixel_means

    # SVD PCA
    U_numpy, Sigma_numpy, Vt_numpy = np.linalg.svd(centered_image_vectors, full_matrices=False)

    # k = 2 dua dimensi
    k = 2
    Uk_numpy = Vt_numpy[:k].T
    Z_numpy = np.dot(centered_image_vectors, Uk_numpy)

    return Uk_numpy, pixel_means

# Fungsi untuk mencari gambar yang mirip berdasarkan jarak Euclidean
def find_similar_images(query_image_path, Uk_numpy, pixel_means, image_vectors, metadata, num_of_img):
    query_vector = process_image(query_image_path)  # q'
    query_vector_centered = query_vector - pixel_means  # (q' - μ)
    query_projection = np.dot(query_vector_centered, Uk_numpy)  # (q' - μ) . Uk
    image_projections = np.dot(image_vectors - pixel_means, Uk_numpy)  # Proyeksi dataset ke ruang PCA
    distances = []

    for i, image_projection in enumerate(image_projections):
        distance = np.linalg.norm(image_projection - query_projection)
        distances.append((i, distance))

    distances.sort(key=lambda x: x[1]) 
    similar_images = [(metadata[idx], distance) for idx, distance in distances[:num_of_img]]
    return similar_images

# Fungsi utama untuk memproses dan mencari gambar mirip
def process_and_find_similar_images(metadata_file, query_image_path, num_of_img=5):
    # Memuat dan memproses gambar
    image_vectors, metadata = load_and_process_images(metadata_file)
    
    # Menghitung PCA
    Uk_numpy, pixel_means = compute_pca(image_vectors)
    
    # Menemukan gambar yang mirip
    similar_images = find_similar_images(query_image_path, Uk_numpy, pixel_means, image_vectors, metadata, num_of_img)

    # Menampilkan hasil
    for image, distance in similar_images:
        print(f"Gambar yang mirip: {image['pic_name']}, Jarak Euclidean: {distance}")

# Eksekusi utama
# metadata_file = "midi_data.json"
# query_image_path = "./datasets/cover/1.jpeg"
# process_and_find_similar_images(metadata_file, query_image_path, num_of_img=5)
