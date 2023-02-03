import { BrowserRouter as Router, Route} from "react-router-dom";
import { Routes } from "react-router-dom";
import jwt_decode from "jwt-decode";

import Skeleton from "./components/Skeleton.js";

import "./utilities.css";

import { socket } from "./client-socket";

import { get, post } from "./utilities";

import './App.css';
import Navbar from "./components/Navbar"
import About from './components/About';

import React, { useState, useEffect } from 'react';


/**
 * Define the "App" component
 */
const App = () => {
  const [userId, setUserId] = useState(undefined);

  useEffect(() => {
    get("/api/whoami").then((user) => {
      if (user._id) {
        // they are registed in the database, and currently logged in.
        setUserId(user._id);
      }
    });
  }, []);

  const handleLogin = (credentialResponse) => {
    const userToken = credentialResponse.credential;
    const decodedCredential = jwt_decode(userToken);
    console.log(`Logged in as ${decodedCredential.name}`);
    post("/api/login", { token: userToken }).then((user) => {
      setUserId(user._id);
      post("/api/initsocket", { socketid: socket.id });
    });
  };

  const handleLogout = () => {
    setUserId(undefined);
    post("/api/logout");
  };

  return (
    <>
      <Router>
        <div><Navbar /></div>
          <Routes>
            <Route path="/" element={<Skeleton />}/>
            <Route path="/about" element={<About />}/>
          </Routes>
      </Router>
    </>
  );
};

export default App