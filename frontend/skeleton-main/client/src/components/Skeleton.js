import { GoogleOAuthProvider, GoogleLogin, googleLogout } from "@react-oauth/google";
import React from 'react';
import "../utilities.css";
import "./Skeleton.css";
import Navbar from "./Navbar";
import Router from "@reach/router"

//TODO: REPLACE WITH YOUR OWN CLIENT_ID
const GOOGLE_CLIENT_ID = "11864695476-05vltj5euv2m1noiq4d74l2tertvo0jo.apps.googleusercontent.com";

const Skeleton = ({ userId, handleLogin, handleLogout, name }) => {
  return (      
    <>
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        {userId ? (
          <>
          <button
            onClick={() => {
              googleLogout();
              handleLogout();
            }}
            >
            Logout
            </button>

            <h1>
            Welcome back {name}
            </h1>
          </>
        ) 
        : (
          <GoogleLogin onSuccess={handleLogin} onError={(err) => console.log(err)} />
        )}
      </GoogleOAuthProvider>
    </>
  );
};


export default Skeleton;


