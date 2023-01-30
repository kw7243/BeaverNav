import './SearchMap.css';
import React, { useState } from 'react';
import Map from './Map.js';
import SearchBar from './SearchBar.js';
import Desc from './Desc.js';
import data from './Rooms.json';

function SearchMap(props) {
    const [start, setStart] = useState(null);
    const [end, setEnd] = useState(null);
    const [about, setAbout] = useState(null);
    const route = (dummy) => dummy;

    return (<div className='full-screen'>
        <Map />
        <SearchBar loc={end} forbid={null} setLoc={setEnd} setAbout={setAbout} def='Start' />
        {end ? <>
            <SearchBar loc={start} forbid={end} setLoc={setStart} setAbout={null} def='End' />
            <Desc about={about} route={route} />
        </> : <></>}
    </div>);
}

export default SearchMap;