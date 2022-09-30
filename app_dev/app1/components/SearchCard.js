import { SafeAreaView, StyleSheet, Text, TextInput, View } from 'react-native'
import React, { useState } from 'react'
import tw from 'tailwind-react-native-classnames'
import { GooglePlacesAutocomplete } from 'react-native-google-places-autocomplete'
import { useDispatch } from 'react-redux'
import { setDestination, setOrigin } from '../slices/navSlice'
import { useNavigation } from '@react-navigation/native'
import NavFavorites from './NavFavorites'
import { TouchableOpacity } from 'react-native-gesture-handler'
import { Icon } from 'react-native-elements'

const SearchCard = () => {
  const dispatch = useDispatch();
  const navigation = useNavigation();
  
  const [startLocation, setStartLocation] = useState("");
  const [endLocation, setEndLocation] = useState("");

  return (
    <SafeAreaView style={tw`bg-white flex-1 border-t border-gray-200`}>
      <Text style={tw`text-center py-5 text-xl`}>Good morning, Kevin</Text>
        <View>
          <TextInput
            placeholder="Start location?"
            style={tw`mx-5 p-2 bg-gray-200 flex-none text-lg rounded-md`}
            onChangeText={(text) => setStartLocation(text)}
            onSubmitEditing={() => {
              // dispatch setOrigin ACTION to Redux slice
              // send up location and name of chosen origin
              dispatch(setOrigin({
                location: {lat: 42.360001, lng: -71.099003}, 
                // description: data.description
              }));
              
              // reset destination in case of back and forth
              dispatch(setDestination(null)); 
            }}
          />
          <TextInput
            placeholder="Where to?"
            style={tw`mx-5 my-5 p-2 bg-gray-200 flex-none text-lg rounded-md`}
            onChangeText={(text) => setEndLocation(text)}
            onSubmitEditing={() => {
              // dispatch setOrigin ACTION to Redux slice
              dispatch(setDestination({
              	location: {lat: 42.37001, lng: -71.084003}, 
              	// description: data.description
              }));
              
              // if (endLocation) navigation.navigate("RideOptionsCard");
            }}
          />
        </View>
        <NavFavorites/>

      <View style={tw`flex-row bg-white justify-evenly py-2 mt-auto border-t border-gray-100`}>
        <TouchableOpacity 
          style={tw`flex flex-row justify-between bg-black w-28 px-4 py-3 rounded-full`}
          onPress={() => {
              navigation.navigate("DirectionsScreen");
            }
          }
        >
          <Icon name="walking" type="font-awesome-5" color="white" size={16}/>
          <Text style={tw`text-white text-center`}>Directions</Text>
        </TouchableOpacity>
      </View>

    </SafeAreaView>
  )
}

export default SearchCard

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