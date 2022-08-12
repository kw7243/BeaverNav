import { configureStore } from "@reduxjs/toolkit"; // set up data layer
import navReducer from "./slices/navSlice"; // one of many slices to pull from

export const store = configureStore({
  reducer: {
    nav: navReducer
  }
});