import { SafeAreaView, StyleSheet, Text, TextInput, View } from 'react-native'
import React, { useState } from 'react'
import tw from 'tailwind-react-native-classnames'
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete'
import { useDispatch } from 'react-redux'
import { setDestination } from '../slices/navSlice'
import { useNavigation } from '@react-navigation/native'
import NavFavorites from './NavFavorites'
import { TouchableOpacity } from 'react-native-gesture-handler'
import { Icon } from 'react-native-elements'

const NavigateCard = () => {
  const dispatch = useDispatch();
  const navigation = useNavigation();
  
  const [startLocation, setStartLocation] = useState("");
  const [endLocation, setEndLocation] = useState("");

  return (
    <SafeAreaView style={tw`bg-white flex-1 border-t border-gray-200`}>
      <Text style={tw`text-center py-5 text-xl`}>Good morning, Kevin</Text>
      <View style={tw`border-t border-gray-200 flex-shrink mx-5 mt-5`}>
        <View>
          <TextInput
            placeholder="Start location?"
            style={tw`p-2 bg-gray-200 flex-none text-lg rounded-md`}
            onChangeText={(text) => setStartLocation(text)}
            onSubmitEditing={() => {
              // dispatch setOrigin ACTION to Redux slice
              // send up location and name of chosen origin
              // console.log(setDestination);
              // dispatch(setDestination({
              // 	location: {lat: 42.360001, lng: -71.092003}, 
              // 	// description: data.description
              // }));
              
              // // reset destination in case of back and forth
              // if (startLocation) navigation.navigate("RideOptionsCard");
            }}
          />
          <TextInput
            placeholder="Where to?"
            style={tw`my-5 p-2 bg-gray-200 flex-none text-lg rounded-md`}
            onChangeText={(text) => setEndLocation(text)}
            onSubmitEditing={() => {
              // dispatch setOrigin ACTION to Redux slice
              // send up location and name of chosen origin
              // console.log(setDestination);
              // dispatch(setDestination({
              // 	location: {lat: 42.360001, lng: -71.092003}, 
              // 	// description: data.description
              // }));
              
              // // reset destination in case of back and forth
              
              // if (endLocation) navigation.navigate("RideOptionsCard");
            }}
          />

                {/* <GooglePlacesAutocomplete
            placeholder="Where to?"
            styles={styles}
            onPress={(data, details=null) => {
              // dispatch setOrigin ACTION to Redux slice
              // send up location and name of chosen origin
              dispatch(setDestination({
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
          
        </View>
        <NavFavorites/>
      </View>

      <View style={tw`flex-row bg-white justify-evenly py-2 mt-auto border-t border-gray-100`}>
        <TouchableOpacity 
          style={tw`flex flex-row justify-between bg-black w-28 px-4 py-3 rounded-full`}
          onPress={() => navigation.navigate("RideOptionsCard")}
        >
          <Icon name="walking" type="font-awesome-5" color="white" size={16}/>
          <Text style={tw`text-white text-center`}>Directions</Text>
        </TouchableOpacity>

        {/* <TouchableOpacity style={tw`flex flex-row justify-between w-24 px-4 py-3 rounded-full`}>
          <Icon name="fast-food-outline" type="ionicon" color="black" size={16}/>
          <Text style={tw`text-center`}>Food</Text>
        </TouchableOpacity> */}
      </View>

    </SafeAreaView>
  )
}

export default NavigateCard

const styles = StyleSheet.create({
  container: {
    backgroundColor: "white",
    paddingTop: 20,
    flex: 0
  },
  textInput: {
    backgroundColor: "#DDDDDF",
    borderRadius: 0,
    fontSize: 18
  },
  textInputContainer: {
    paddingHorizontal: 20,
    paddingBottom: 0
  }
})