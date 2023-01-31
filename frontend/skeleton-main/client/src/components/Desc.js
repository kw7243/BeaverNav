import './Desc.css';
import React from 'react'

function Desc(props) {
    return (<div className='destination-container'>
        {props.about ? props.about : ''}
        <br />
        <br />
        <button className='direction' onClick={props.route} >Directions</button>
    </div>);
}

export default Desc;