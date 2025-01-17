"use client";

import Image from 'next/image';
import React, { useState } from 'react';
import "./searchbysound.css";
import { useRouter } from 'next/navigation';
import logo from "../../public/simsalabimlogoblack.png";
import Navbar from '../components/Navbar/Navbar';
import addaudio from '../../public/audio.png';
import Link from 'next/link'; 

export default function Home() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: string) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const fileExtension = file.name.split('.').pop()?.toLowerCase(); // Extract file extension

      // Validate that the file is a .mid file
      if (fileExtension === 'mid') {
        setAudioFile(file);
        setStatusMessage(''); // Clear error message
      } else {
        setAudioFile(null); // Reset file
        setStatusMessage('Error: Only .mid files are allowed!'); // Display error message
      }
    }
  };

  const handleFileUpload = async (file: File | null, folder: string) => {
    if (!file) {
      setStatusMessage(`Please select a file to upload to ${folder}.`);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder); // Specify the target folder

    try {
      const response = await fetch('http://127.0.0.1:8000/simsalabim/upload-mid/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        console.log(`File uploaded successfully to ${folder}!`);
        setStatusMessage('');
        return true; // Success
      } else {
        const errorData = await response.json();
        console.error('Upload failed:', errorData.message);
        setStatusMessage(`Upload failed: ${errorData.message}`);
        return false; // Failure
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setStatusMessage('An unexpected error occurred. Please try again.');
      return false; // Failure
    }
  };

  const handleImportClick = async () => {
    if (!audioFile) {
      setStatusMessage("Please upload a valid .mid file first!");
      return;
    }

    const uploadSuccess = await handleFileUpload(audioFile, 'audio');
    if (uploadSuccess) {
      router.push('./soundresult'); // Navigate only if upload is successful
    }
  };

  return (
    <div className="page-sound">
      <div className='top-sound'>
        <div className='back-sound'>
          <Link href="/" legacyBehavior>
            <a style={{ textDecoration: 'none', display: 'flex', alignItems: 'center' }}>
              <i className="fa-solid fa-arrow-right fa-rotate-180" style={{ color: '#000000' }}></i>
              <p>Back to Dataset</p>
            </a>
          </Link>
        </div>
        <div>
          <Image src={logo} alt="logo" width={160} />
        </div>
      </div>
      <div className="main-content-sound">
        <h1 className="title-sound">
          <span>SEARCH BY </span>
          <u>SOUND</u>
        </h1>
        <div className="upload-section-sound">
          <div
            className="w-[200px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center cursor-pointer"
            onClick={() => document.getElementById('audio-dataset-input')?.click()}
          >
            <input
              type="file"
              accept=".mid"
              onChange={(e) => handleFileChange(e, 'audio')}
              id="audio-dataset-input"
              className='hidden w-full h-full'
            />
            {audioFile ? (
              <p className='text-[10px] underline text-black-500'>{audioFile.name}</p>
            ) : (
              <Image src={addaudio} alt="addaudio" width={60} />
            )}
          </div>
          <div className="search-instruction-sound">
            <button className="search-button-sound" onClick={handleImportClick}>
              search
            </button>
            {statusMessage && <p className="error-message">{statusMessage}</p>}
          </div>
          <div className="instruction-container-sound">
            <span className="arrow-sound">&#10549;</span>
            <p className="instruction-sound">
              Add a MIDI file you <br /> want to search here!
            </p>
          </div>
        </div>
      </div>
      <div className='navbar-sound'>
        <Navbar theme='light' />
      </div>
    </div>
  );
}