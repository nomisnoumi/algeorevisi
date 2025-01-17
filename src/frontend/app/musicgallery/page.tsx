"use client";

import React, { useState, useEffect } from "react";
import "./musicgallery.css";
import Image from "next/image";
import logo from "../../public/simsalabimlogo.png";
import Navbar from "../components/Navbar/Navbar";
import Link from "next/link";

const musicgallery = () => {

    interface Song {
        name: string;
        img: string;
        music: string;
        singer: string;
    }

    const [songs, setSongs] = useState<Song[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [isMidiLoaded, setIsMidiLoaded] = useState(false);
    const [currentSong, setCurrentSong] = useState<Song | null>(null); // State lagu yang sedang diputar
    const [isPlaying, setIsPlaying] = useState(false); 

    const songsPerPage = 6;

    // Load MIDI.js secara dinamis
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
    
    // Fetch daftar lagu
    useEffect(() => {
        const fetchSongs = async () => {
            const response = await fetch("http://127.0.0.1:8000/simsalabim/fetch-mapper/");
            const data = await response.json();
            setSongs(data.data.songs.map((song: any) => ({
                name: song.name,
                img: song.img,
                music: song.music,
                singer: song.singer, // Tambahkan penyanyi dari data JSON
            })));
        };
        fetchSongs();
    }, []);

    useEffect(() => {
        return () => {
            if (window.MIDIjs && window.MIDIjs.stop) {
                window.MIDIjs.stop();
            }
            setIsPlaying(false);
            setCurrentSong(null);
        };
    }, []);

    const startIndex = (currentPage - 1) * songsPerPage;
    const endIndex = startIndex + songsPerPage;

    const paginatedSongs = songs.slice(startIndex, endIndex);

    const handleNextPage = () => {
        if (currentPage < Math.ceil(songs.length / songsPerPage)) {
        setCurrentPage(currentPage + 1);
        }
    };

    const handlePreviousPage = () => {
        if (currentPage > 1) {
        setCurrentPage(currentPage - 1);
        }
    };

    // Fungsi untuk lagu berikutnya
    const handleNextSong = () => {
        if (currentSong) {
            const currentIndex = songs.findIndex((song) => song.music === currentSong.music);
            const nextIndex = (currentIndex + 1) % songs.length; // Loop ke awal jika terakhir
            playMidi(songs[nextIndex]);
        }
    };

    // Fungsi untuk lagu sebelumnya
    const handlePreviousSong = () => {
        if (currentSong) {
            const currentIndex = songs.findIndex((song) => song.music === currentSong.music);
            const prevIndex = (currentIndex - 1 + songs.length) % songs.length; // Loop ke akhir jika pertama
            playMidi(songs[prevIndex]);
        }
    };

    const playMidi = (song: Song) => {
        if (isPlaying) {
            if (window.MIDIjs && window.MIDIjs.stop) {
                window.MIDIjs.stop(); // Stop lagu jika window.MIDIjs sudah tersedia
            }
            setIsPlaying(false);
        } else {
            if (window.MIDIjs && window.MIDIjs.play) {
                const songUrl = `http://127.0.0.1:8000/${song.music.replace(/ /g, "%20")}`;
                window.MIDIjs.play(songUrl); // Mainkan lagu
                setCurrentSong(song);
                setIsPlaying(true);
            }
        }
    };
    

    const SongCard: React.FC<Song> = ({ name, img, music, singer }) => {
        const playMidiCard = () => {
            playMidi({ name, img, music, singer });
        };
    
        return (
            <div className="song-card">
                <div className="content">
                    {/* Album Image */}
                    <img src={`http://127.0.0.1:8000/${img}`} alt={name} className="small-image" />
                    
                    {/* Name, Singer, and Controls */}
                    <div className="song-details">
                        <h3>{name}</h3>
                        <p>{singer}</p>
                        <div className="player-buttons-card">
                            <button
                                className="fa-solid fa-backward-step fa-lg"
                                onClick={handlePreviousSong}
                                style={{ color: "#FFFFFF" }}
                            ></button>
                            <button
                                className={`fa-solid ${currentSong?.music === music && isPlaying ? "fa-stop" : "fa-play"} fa-lg`}
                                onClick={playMidiCard}
                                style={{ color: "#FFFFFF" }}
                            ></button>
                            <button
                                className="fa-solid fa-backward-step fa-rotate-180 fa-lg"
                                onClick={handleNextSong}
                                style={{ color: "#FFFFFF" }}
                            ></button>
                        </div>
                    </div>
                </div>
                <hr />
            </div>
        );
    };

  return (
    <div className='page-gallery'>
        <div className='top-gallery'>
            <div className='back-gallery'>
            <Link href="/" legacyBehavior>
                <a style={{ textDecoration: 'none', display: 'flex', alignItems: 'center' }}>
                <i className="fa-solid fa-arrow-right fa-rotate-180" style={{ color: '#ffffff' }}></i>
                <p>Back to Dataset</p>
                </a>
            </Link>
            </div>
            <div>
                <Image src={logo} alt="logo" width={160} />
            </div>
        </div>
        <div className='gallery'>
            <div className='gallery-top'>
                <button onClick={handlePreviousPage} style={{ color: 'black' }} disabled={currentPage === 1}>
                    &lt;
                </button>
                <h1>Music Gallery</h1>
                <button onClick={handleNextPage} style={{ color: 'black' }} disabled={currentPage === Math.ceil(songs.length / songsPerPage)}>
                    &gt;
                </button>
            </div>
            <div className="pagination-gallery">
                <span className='page-text-gallery'>Page {currentPage} of {Math.ceil(songs.length / songsPerPage)}</span>
            </div>
            <div className="songs-container-gallery">
                    {paginatedSongs.map((song, index) => (
                        <SongCard key={index} name={song.name} img={song.img} music={song.music} singer={song.singer} />
                    ))}
            </div>
            {/* Player Box */}
            <div className="player-container-gallery">
                {currentSong ? (
                    <>
                        <img
                            src={`http://127.0.0.1:8000/${currentSong.img}`}
                            alt={currentSong.name}
                            className="small-image"
                        />
                        <div className="player-texts-gallery">
                            <h3>{currentSong.name}</h3>
                            <h4>{currentSong.singer}</h4>
                        </div>
                    </>
                ) : (
                    <div className="player-texts-gallery">
                        <h3>No song playing</h3>
                    </div>
                )}

                <div className="player-gallery">
                    <div className="player-buttons-gallery">
                        <button
                            className="fa-solid fa-backward-step fa-lg"
                            style={{
                                color: currentSong && isMidiLoaded ? "#000000" : "#cccccc",
                                cursor: currentSong && isMidiLoaded ? "pointer" : "not-allowed",
                            }}
                            onClick={handlePreviousSong}
                            disabled={!currentSong || !isMidiLoaded} 
                        ></button>
                        <button
                            className={`fa-solid ${isPlaying ? "fa-stop" : "fa-play"} fa-lg`}
                            style={{
                                color: currentSong && isMidiLoaded ? "#000000" : "#cccccc",
                                cursor: currentSong && isMidiLoaded ? "pointer" : "not-allowed",
                            }}
                            onClick={() => currentSong && isMidiLoaded && playMidi(currentSong)}
                            disabled={!currentSong || !isMidiLoaded} 
                        ></button>
                        <button
                            className="fa-solid fa-backward-step fa-rotate-180 fa-lg"
                            style={{
                                color: currentSong && isMidiLoaded ? "#000000" : "#cccccc",
                                cursor: currentSong && isMidiLoaded ? "pointer" : "not-allowed",
                            }}
                            onClick={handleNextSong}
                            disabled={!currentSong || !isMidiLoaded} 
                        ></button>
                    </div>
                </div>
            </div>
        </div>
        <div className='navbar-gallery'>
            <Navbar/>
        </div>
    </div>
  )
}

export default musicgallery