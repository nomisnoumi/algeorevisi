"use client";

import React, { useState } from "react";
import "./searchbycover.css";
import Image from 'next/image'
import logo from "../../public/simsalabimlogoblack.png";
import { useRouter } from 'next/navigation';
import Navbar from '../components/Navbar/Navbar';
import addimage from "../../public/addimage.png";
import Link from 'next/link';

const App: React.FC = () => {
  const [coverFile, setCoverFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: string) => {
      if (e.target.files && e.target.files.length > 0) {
        const file = e.target.files[0];
        const fileExtension = file.name.split('.').pop()?.toLowerCase(); // Extract file extension
  
        if (fileExtension === "png" || fileExtension === "jpeg" || fileExtension === "jpg") {
          setCoverFile(file);
          setStatusMessage(''); // Clear error message
        } else {
          setCoverFile(null); // Reset file
          setStatusMessage('Error: Only .jpg/.jpeg/.png files are allowed!'); // Display error message
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
        const response = await fetch('http://127.0.0.1:8000/simsalabim/upload-img/', {
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
      if (!coverFile) {
        setStatusMessage("Please upload a valid .png/.jpeg/.jpg file first!");
        return;
      }
  
      const uploadSuccess = await handleFileUpload(coverFile, 'cover');
      if (uploadSuccess) {
        router.push('./coverresult'); // Navigate only if upload is successful
      }
    };

  return (
    <div className="page-cover">
        <div className='top-cover'>
            <div className='back-cover'>
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
      <div className="main-content-cover">
        <h1 className="title-cover">
          <span>SEARCH BY </span>
          <u>COVER</u>
        </h1>
        <div className="upload-section-cover">
          <div
              className="w-[200px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center cursor-pointer"
              onClick={() => document.getElementById('cover-dataset-input')?.click()}
          >
            <input
              type="file"
              accept=".jpg, .jpeg, .png"
              onChange={(e) => handleFileChange(e, 'cover')}
              id="cover-dataset-input"
              className='hidden w-full h-full'
            />
            {coverFile ? (
              <p className='text-[10px] underline text-black-500'>{coverFile.name}</p>
            ) : (
              <Image src={addimage} alt="addimage" width={60} />
            )}
          </div>
          <div className="search-instruction-cover">
            <button className="search-button-cover" onClick={handleImportClick}>
              search
            </button>
            {statusMessage && <p className="error-message">{statusMessage}</p>}
          </div>
          <div className="instruction-container-cover">
            <span className="arrow-cover">&#10548;</span>
              <p className="instruction-cover">
                Add album cover you <br/> want to search here!
              </p>
          </div>
        </div>
      </div>
      <div className='navbar-cover'>
            <Navbar theme='light'/>
      </div>
    </div>
  );
};

export default App;