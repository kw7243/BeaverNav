import { Link} from "react-router-dom"
import React from 'react'
import { Routes } from "@reach/router";

export default function Navbar() {
    const toggle = () => {
        setVisible(!visible);
    };

    return (
        <>
            <span className="navPages"><Link to="/" className="navLinks" onClick={toggle}><button className="navButtons">Home</button></Link></span>
            <span className="navPages"><Link to="/about" className="navLinks" onClick={toggle}><button className="navButtons">About</button></Link></span>
        </>
    )
}