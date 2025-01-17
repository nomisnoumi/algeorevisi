"use client";

import Image from 'next/image';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import './dataset.css'; 
import addimage from '../public/addimage.png'; 
import addaudio from '../public/audio.png';
import mapper from '../public/mapper.png'
import Link from 'next/link'; 
import Top from './components/Top/Top';

export default function Home() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [coverFile, setCoverFile] = useState<File | null>(null);
  const [mapperFile, setMapperFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: string) => {
    if (e.target.files && e.target.files.length > 0) {
      if (type === 'audio') setAudioFile(e.target.files[0]);
      if (type === 'cover') setCoverFile(e.target.files[0]);
      if (type == 'mapper') setMapperFile(e.target.files[0]);
    }
  };
  

  const handleFileUpload = async (file: File | null, folder: string, fileType: 'zip' | 'json'): Promise<boolean> => {
    if (!file) {
      setStatusMessage(`Please select a file to upload to ${folder}.`);
      return false;
    }
  
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder); // Specify the target folder
  
    try {
      const endpoint = fileType === 'zip' 
        ? 'http://127.0.0.1:8000/simsalabim/upload-zip/' 
        : 'http://127.0.0.1:8000/simsalabim/upload-json/';
  
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });
  
      const responseData = await response.json(); // Parse the JSON response
  
      if (response.ok) {
        console.log(`File uploaded successfully to ${folder}!`);
        setStatusMessage(responseData.message || `File uploaded successfully to ${folder}!`);
        return true; // Success
      } else {
        // Instead of console.error, just update the UI
        setStatusMessage(`Error: ${responseData.message}`);
        return false; // Failure
      }
    } catch (error) {
      // Prevent console error popup, display message in UI instead
      setStatusMessage('An unexpected error occurred. Please try again.');
      return false; // Failure
    }
  };
  
  

  const handleImportClick = async () => {
    if (!audioFile || !coverFile || !mapperFile) {
      setStatusMessage("Error: upload all files first!");
      return;
    }
    setStatusMessage("");
  
    try {
      // Upload audio file
      const audioResponse = await handleFileUpload(audioFile, 'audio', 'zip');
      if (!audioResponse) return; // Stop execution if upload fails
  
      // Upload cover file
      const coverResponse = await handleFileUpload(coverFile, 'cover', 'zip');
      if (!coverResponse) return;
  
      // Upload mapper file
      const mapperResponse = await handleFileUpload(mapperFile, 'mapper', 'json');
      if (!mapperResponse) return;
  
      // If all uploads succeed, navigate to the next page
      router.push('./musicgallery');
    } catch (error) {
      console.error('Error during file upload process:', error);
      setStatusMessage("An unexpected error occurred. Please try again.");
    }
  };
  

  return (
    <>
      <Top /> 
      <main className='data-page'>
        <h1>DATASET INPUT</h1>
        <div className="input-row-data">
          <div className="input-container-data">
            <div
              className="w-[200px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center cursor-pointer"
              onClick={() => document.getElementById('audio-dataset-input')?.click()}
            >
              <input
                type="file"
                accept=".zip"
                onChange={(e) => handleFileChange(e, 'audio')}
                id="audio-dataset-input"
                className='hidden w-full h-full'
              />
              {audioFile ? (
                <p className='text-[10px] underline text-black'>{audioFile.name}</p>
              ) : (
                <Image src={addaudio} alt="addaudio" width={60} />
              )}
            </div>
            <p>Input audio dataset</p>
          </div>
 
          <div className="input-container-data">
            <div
              className="w-[200px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center cursor-pointer"
              onClick={() => document.getElementById('cover-dataset-input')?.click()}
            >
              <input
                type="file"
                accept=".zip"
                onChange={(e) => handleFileChange(e, 'cover')}
                className='hidden'
                id="cover-dataset-input"
              />
              {coverFile ? (
                <p className='text-[10px] underline text-black'>{coverFile.name}</p>
              ) : (
                <Image src={addimage} alt="addimage" width={60} />
              )}
            </div>
            <p>Input cover dataset</p>
          </div>

          <div className="input-container-data">
            <div
              className="w-[200px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center cursor-pointer"
              onClick={() => document.getElementById('mapper-dataset-input')?.click()}
            >
              <input
                type="file"
                accept=".json" 
                onChange={(e) => handleFileChange(e, 'mapper')}
                id="mapper-dataset-input"
                className='hidden w-full h-full'
              />
              {mapperFile ? ( 
                <p className='text-[10px] underline text-black'>{mapperFile.name}</p>
              ) : (
                <Image src={mapper} alt="mapper" width={60} />
              )}
            </div>
            <p>Input mapper.json</p>
          </div>
                    
        </div>
        <button className='submit-data' onClick={handleImportClick}>import dataset</button>
        {statusMessage && <p className="error-message">{statusMessage}</p>}
        <p className='tm-data'><u>kelompok 11</u></p>
      </main>
    </>
  );
}