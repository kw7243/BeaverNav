import { StyleSheet, Text, View, SafeAreaView, Image } from 'react-native';
import React from 'react';
import tw from "tailwind-react-native-classnames";
import NavOptions from '../components/NavOptions';
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete';
import { GOOGLE_MAPS_APIKEY } from "@env";

import { useDispatch } from 'react-redux';
import { setOrigin, setDestination } from '../slices/navSlice';
import { TextInput } from 'react-native-gesture-handler';
import NavFavorites from '../components/NavFavorites';

const HomeScreen = () => {
	const dispatch = useDispatch();

	return (
		<SafeAreaView style={tw`bg-white h-full`}>
			<View style={tw`p-5`}>
				<Image 
					style={{
						width: 100,
						height: 100,
						resizeMode: "contain"
					}}
					source={{
						uri: "https://1000logos.net/wp-content/uploads/2017/09/Uber-logo.jpg"
					}}
				/>
				<TextInput
					placeholder="Start location?"
					style={tw`p-2 m-1 text-lg`}
					onSubmitEditing={() => {
						// dispatch setOrigin ACTION to Redux slice
						// send up location and name of chosen origin
						dispatch(setOrigin({
							location: {lat: 42.360001, lng: -71.092003}, 
							// description: data.description
						}));
						
						// reset destination in case of back and forth
						dispatch(setDestination(null)); 
					}}
				/>

				{/* <GooglePlacesAutocomplete
					placeholder="Start location?"
					styles={{
						container: {
							flex: 0
						},
						textInput: {
							fontSize: 18
						}
					}}
					onPress={(data, details=null) => {
						// dispatch setOrigin ACTION to Redux slice
						// send up location and name of chosen origin
						console.log("PRESSED");
						dispatch(setOrigin({
							location: {lat: 42.360001, lng: -71.092003}, 
							// description: data.description
						}));
						
						// reset destination in case of back and forth
						dispatch(setDestination(null)); 
					}} // end onPress

					// fetchDetails={true}
					returnKeyType={"search"}
					enablePoweredByContainer={false}
					minLength={2} // minimum search value before autocomplete
					// query={{
					// 	key: GOOGLE_MAPS_APIKEY,
					// 	language: "en"
					// }}
					nearbyPlacesAPI="GooglePlacesSearch"
					debounce={400}
				/> */}

				<NavOptions />
				<NavFavorites/>
			</View>
		</SafeAreaView>
	)
}

export default HomeScreen

const styles = StyleSheet.create({})