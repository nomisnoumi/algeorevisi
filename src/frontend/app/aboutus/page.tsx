"use client";

import Image from 'next/image';
import React, { useState } from 'react';
import './aboutus.css'; 
import Top from '../components/Top/Top'; 

export default function AboutUs() {

  return (
    <>
      <Top /> 
      <main className='aboutus-page'>
        <h1>GET TO KNOW</h1>
        <p>
            <span>people behind </span>
            <u>simsalabim</u>
        </p>

        <div className="member-row-data">

            <div className="member-container-data">
                <div
                className="w-[200px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center"
                >
                          <Image
                            src="/dinda.jpg"
                            alt="Adinda Putri"
                            width={175} 
                            height={175}
                            className="rounded-md object-cover"
                        />
                </div>
                <h2>Adinda Putri</h2>
                <p>sehat-sehat orang baik</p>
            </div>

            <div className="member-container-data">
                <div
                className="w-[200px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center"
                >
                <p className="text-black">Extra Box</p>
                </div>
                <h2>Noumisyifa Nabila</h2>
                <p>loremipsum</p>
            </div>

            <div className="member-container-data">
                <div
                className="w-[200px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center"
                >
                <p className="text-black">Extra Box</p>
                </div>
                <h2>Ranashahira Reztaputri</h2>
                <p>loremipsum</p>
            </div>
            </div>
        <p className='tm-aboutus'><u>kelompok 11</u></p>
      </main>
    </>
  );
}