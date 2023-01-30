import './SearchBar.css';
import React, { useState, useEffect } from 'react';
import data from "./Rooms.json";

function List(props) {
    const filteredData = Object.keys(data).filter((room) => {
        if (props.input === '') {
            return room;
        }
        else {
            return room.toLowerCase().includes(props.input)
        }
    });

    if (filteredData.length === 0 || props.input === '' || props.disable) {
        props.left("text left");
        props.right("submit right");
    } else {
        props.left("text top-left");
        props.right("submit top-right");
    }

    return (<div className='scroll'>
        {
            props.input !== '' && !props.disable
            ? 
            filteredData.map((room) => (
                <input type='button' value={room} onClick={props.handler} className='location-card' />
            ))
            :
            <></>
        }
    </div>);
}

function SearchBar(props) {
    const [inputText, setInputText] = useState(props.def);
    const [leftRad, setLeftRad] = useState("text left");
    const [rightRad, setRightRad] = useState("submit right");
    const [disableCards, setDisableCards] = useState(true);
    const textHandler = (e) => {
        var room = e.target.value;
        setInputText(room);
        setDisableCards(false);
    };
    const tapLocHandler = (e) => {
        setInputText(e.target.value);
        setDisableCards(true);
    };
    const submitHandler = (e) => {
        e.preventDefault();
        if (inputText in data) {
            props.setLoc(inputText);
            if (props.setAbout !== null) {
                props.setAbout(data[inputText]);
            }
        }
    };

    return (<div className='search-bar-container'>
        <form onSubmit={submitHandler}>
            <input type='text' value={inputText} onChange={textHandler} className={leftRad} />
            <input type='submit' value='submit' className={rightRad} />
        </form>
        <List input={inputText} handler={tapLocHandler} left={setLeftRad} right={setRightRad} disable={disableCards} />
    </div>);
}

export default SearchBar;