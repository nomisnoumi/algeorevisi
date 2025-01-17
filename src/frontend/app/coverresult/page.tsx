"use client"

import React, { useEffect, useState, useRef } from "react";
import Navbar from '../components/Navbar/Navbar';
import Link from 'next/link';
import './coverresult.css'
import Image from 'next/image'
import logo from '../../public/simsalabimlogoblack.png';
import cmiygl from '../../public/cmiygl.png';
import Script from "next/script";

const page = () => {

  interface Song {
    name: string;
    singer: string;
    img: string;
    music: string;
  }

  const [bestCover, setBestCover] = useState<string | null>(null);
  const [songs, setSongs] = useState<Song[]>([]); // State untuk menyimpan semua data mapper
  const [selectedSong, setSelectedSong] = useState<Song | null>(null); // Lagu yang dipilih
  const [distance, setDistance] = useState<number | null>(null);
  const [loadingTime, setLoadingTime] = useState<number | null>(null); // Store loading time in seconds
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isScriptLoaded, setIsScriptLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [coverFileUrl, setCoverFileUrl] = useState<string>(""); // Dynamic Cover file URL
  const [coverName, setCoverName] = useState<string>("");
  // const [progress, setProgress] = useState(0); // Progress percentage
  const [scriptReady, setScriptReady] = useState(false);
  const [isMidiLoaded, setIsMidiLoaded] = useState(false);
  // const durationRef = useRef<number>(120); // Set an estimated total duration (in seconds)
  // const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
      const script = document.createElement("script");
      script.src = "https://www.midijs.net/lib/midi.js";
      script.type = "text/javascript";
      script.onload = () => {
          setIsMidiLoaded(true); // Tandai bahwa MIDI.js sudah dimuat
          console.log("MIDI.js loaded successfully!");
      };
      script.onerror = () => {
          console.error("Failed to load MIDI.js script!");
      };
      document.body.appendChild(script);
  }, []);

  useEffect(() => {
    const fetchMapper = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/simsalabim/fetch-mapper/");
        const data = await response.json();
        setSongs(data.data.songs); // Simpan semua lagu ke state songs
      } catch (error) {
        console.error("Failed to fetch mapper data", error);
      }
    };
  
    fetchMapper();
  }, []);

  useEffect(() => {
    const fetchSearchResult = async () => {
      const startTime = performance.now(); // Start measuring time
      try {
        // Use the full backend URL to avoid fetch failure
        const response = await fetch("http://127.0.0.1:8000/simsalabim/cover-search-result/");
        if (!response.ok) {
          throw new Error("Failed to fetch data from the server.");
        }
        const data = await response.json();

        // Update state with API data
        // setCoverName(data.cover_name || "");
        setBestCover(data.best_cover || "No match found");
        setDistance(data.similarity_percentage || 0);
        setCoverFileUrl(`http://127.0.0.1:8000/datasets/cover/${data.best_cover}`);
      } catch (err: any) {
        setError(err.message);
      } finally {
        const endTime = performance.now(); // End measuring time
        setLoadingTime(parseFloat(((endTime - startTime) / 1000).toFixed(2)));
        setIsLoading(false);
      }
    };
    fetchSearchResult();
  }, []);

  useEffect(() => {
    const fetchSearchResult = async () => {
      const startTime = performance.now();
      try {
        const response = await fetch("http://127.0.0.1:8000/simsalabim/cover-search-result/");
        if (!response.ok) throw new Error("Failed to fetch data");
  
        const data = await response.json();
        const fileName = data.best_cover;
  
        // Tambahkan prefix path ke fileName
        const coverPath = `/datasets/cover/${fileName}`;
  
        console.log("Searching for coverPath:", coverPath);
        console.log("Available songs:", songs);
  
        // Temukan lagu dari mapper berdasarkan file cover
        const matchedSong = songs.find(song => song.img === coverPath);
  
        if (matchedSong) {
          console.log("Matched song:", matchedSong);
          setSelectedSong(matchedSong); // Set lagu yang dipilih
          setCoverFileUrl(`http://127.0.0.1:8000${matchedSong.img}`); // URL lagu
        } else {
          console.warn("No matching song found!");
        }
  
        setDistance(data.similarity_percentage || 0);
      } catch (err: any) {
        setError(err.message);
      } finally {
        const endTime = performance.now();
        setLoadingTime(parseFloat(((endTime - startTime) / 1000).toFixed(2)));
        setIsLoading(false);
      }
    };
  
    if (songs.length > 0) fetchSearchResult();
  }, [songs]); // Tambahkan dependency songs agar mapper tersedia sebelum mencari

  const handleScriptLoad = () => {
    setScriptReady(true);
  }

  const handleScriptError =() => {
    setError("Failed to load image");
    setScriptReady(false);
  }



  // // Stop progress updates
  // const stopProgress = () => {
  //   if (intervalRef.current) {
  //     clearInterval(intervalRef.current);
  //     intervalRef.current = null;
  //   }
  // };

  // // Cleanup on unmount
  // useEffect(() => {
  //   return () => {
  //     if (isPlaying) {
  //       window.MIDIjs?.stop();
  //     }
  //     stopProgress();
  //   };
  // }, [isPlaying]);

  // if (isLoading) return <div className="loading">Loading...</div>;
  // if (error) return <div className="error">Error: {error}</div>;

  // if (isLoading) {
  //   return <div className="loading">Loading...</div>;
  // }

  // if (error) {
  //   return <div className="error">Error: {error}</div>;
  // }

  // const playMapperSong = () => {
  //   if (isPlaying) {
  //     window.MIDIjs.stop();
  //     setIsPlaying(false);
  //   } else {
  //     const songUrl = midiFileUrl; // URL lagu dari mapper
  //     window.MIDIjs.play(songUrl);
  //     setIsPlaying(true);
  //   }
  // };
  
  return (
    <div className='cover-result'>
      <Script
        src="https://cdn.jsdelivr.net/gh/mudcube/MIDI.js@master/build/MIDI.min.js"
        strategy="afterInteractive"
      />
      <div className='top-cover-res'>
        <div className='back-cover-res'>
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
    <div className='content-container'>
      <h1 className="title-res-sound">
          <span>SEARCH BY </span>
          <u>COVER</u>
      </h1>
      <div className='content2-container'>
        <div className='stat-container'>
          <div className='similarity-container'></div>
            <div className='bottom-stat'>
              <div className='similarity-container'>
                <div className='circle-percentage'>
                  <Image 
                      src="/circle-text.png"  /* Replace with your circle text image */
                      alt="Circle Text"
                      layout="fill" 
                      objectFit="contain"
                      className="circle-text-image"
                  />
                  <h2 className="percentage">
                    {distance !== null ? `${distance}%` : "N/A"}
                  </h2>
                </div>
                </div>
                <h4 className="font-semibold text bl">
                  Time execution: <span className="text-[#7776F6]">{loadingTime !== null ? `${loadingTime}s` : "N/A"}</span>
                </h4>
                </div>
            </div>
            <div className='result-container'>
              <div className="result-section-sound">
                {/* Album Image */}
                <div className="w-[200px] h-[200px] border-2 border-solid rounded-md border-black overflow-hidden mb-2">
                <Image
                  src={coverFileUrl || '/default-image.png'} // Dynamic URL or fallback image
                  alt="Song Preview"
                  width={200}
                  height={200}
                  objectFit="cover"
                  className="rounded-md"
                />
                </div>

                {/* Song Title */}
                <h4>{selectedSong?.name || 'No song selected'}</h4>
                <p>him</p>
                  
                {/* Search Again */}
                <Link href="/searchcover" legacyBehavior>
                  <button className="back-search-sound">
                    Search Again
                  </button>
                </Link>
              </div>
            </div>
            </div>
          </div>
        <div className='navbar-sound'>
          <Navbar theme='light' />
      </div>
    </div>
  )
}

export default page

