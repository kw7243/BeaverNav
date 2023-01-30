import './App.css';
import SearchMap from './components/SearchMap.js';
import React, { useState } from "react"
import Navbar from "./components/HomePage/Navbar"
import Home from "./pages/Home"
import About from './pages/About';
import { Route, Routes} from "react-router-dom"

function App () {
  return (
    <>
      <Navbar />
      <div className='container'>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </>
  )
}

export default App

// function App() {
//   return (<div style={styles}>
//     Let's build BeaverNav!
//   </div>
//   // <div className='no-overflow'>
//   //   <SearchMap />
//   // </div>
//   );
// }