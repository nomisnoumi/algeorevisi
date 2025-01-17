"use client";

import React, { useState } from 'react';
import './howtouse.css'; 
import Top from '../components/Top/Top'; 

export default function HowToUse() {

  return (
    <>
      <Top />
      <main className='howtouse-page'>
        <h1>USAGE GUIDES</h1>

        <div className="usage-row-data">

            <div className="usage-container-data">
                <div
                className="w-[350px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center">
                <h2>1. Navigation<br/>
                    <p>Use the navigation bar to:<br/>
	                    •	About Us: View the team members.<br/>
	                    •	Simsalabim Logo: Import your dataset.<br/>
	                    •	How to Use: Read the usage guide.</p>
                </h2>
                </div>
            </div>

            <div className="usage-container-data">
                <div
                className="w-[350px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center">
                <h2>2. Import Dataset<br/>
                    <p>Click the Simsalabim Logo to go to the <br/> Dataset Input page, then:<br/>
	                    •	Upload audio files via the Audio Dataset <br/> Box (in .zip format).<br/>
                    	•	Upload image files via the Cover Dataset <br/> Box (in .zip format).<br/>
	                    •	Click Import Dataset to proceed.</p>
                </h2>
                </div>
            </div>

            <div className="usage-container-data">
                <div
                className="w-[350px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center">
                <h2>3. Music Gallery<br/>
                    <p>After click Import Dataset button, view all <br/>
                    uploaded datasets in the Music Gallery. <br/>
                    Use this space to browse and verify your data.</p>
                </h2>
                </div>
            </div>

            <div className="usage-container-data">
                <div
                className="w-[350px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center"
                >
                <h2>4. Search Methods<br/>
                    <p>Choose a search method:<br/>
	                •	Search by Cover: Compare an uploaded <br/>
                    image with the dataset to find <br/>
                    matching content.<br/>
	                •	Search by Sound: Compare an uploaded <br/>
                    audio file with the dataset to find <br/>
                    matching sounds.</p>
                </h2>
                </div>
            </div>

            <div className="usage-container-data">
                <div
                className="w-[350px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center"
                >
                <h2>5. Upload and Search<br/>
                    <p>	•	For Search by Cover, upload an image file <br/>
                    to compare against your dataset, then <br/>
                    click 'search'.<br/>
                    •	For Search by Sound, upload an audio file <br/>
                    to compare, then click 'search'.</p>
                </h2>
                </div>
            </div>

            <div className="usage-container-data">
                <div
                className="w-[350px] h-[200px] border-2 border-dashed rounded-md border-black flex items-center justify-center"
                >
                <h2>6. View Result, Explore <br/>
                    <p>Check the similarity scores to find <br/>
                    the closest matches in your dataset, <br/>
                    then perform another search or explore <br/>
                    other pages for more features.</p>
                </h2>
                </div>
            </div>

            </div>
        <p className='tm-aboutus'><u>kelompok 11</u></p>
      </main>
    </>
  );
}