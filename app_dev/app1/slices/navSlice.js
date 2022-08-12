import { createSlice } from "@reduxjs/toolkit";

const initialState = {
	origin: null,
	destination: null,
	travelTimeInformation: null
}

export const navSlice = createSlice({
	name: "nav", // name of slice
	initialState, // 
	reducer: { // for dispatching actions into slice
		setOrigin: (state, action) => {
			state.origin = action.payload;
		},
		setDestination: (state, action) => {
			state.destination = action.payload;
		},
		setTravelTimeInformation: (state, action) => {
			state.travelTimeInformation = action.payload;
		},
	} 
});

export const { setOrigin, setDestination, setTravelTimeInformation } = navSlice.actions;

// selectors - lets you pull things from data layer
export const selectOrigin = (state) => state.nav.origin;
export const selectDestination = (state) => state.nav.destination;
export const selectTravelTimeInformation = (state) => state.nav.travelTimeInformation;

export default navSlice.reducer;
