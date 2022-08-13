import { FlatList, Image, Text, TouchableOpacity, View } from 'react-native';
import React from 'react';
import tw from "tailwind-react-native-classnames";
import { Icon } from 'react-native-elements';
import { useNavigation } from '@react-navigation/native';
 
const data = [
  {
    id: "123",
    title: "Get a ride",
    image: "https://links.papareact.com/3pn",
    screen: "MapScreen"
  },
  {
    id: "456",
    title: "Order food",
    image: "https://links.papareact.com/28w",
    screen: "OTHERSCREEN" // change to relevant screen... 
  }
];

const NavOptions = () => {
  const navigation = useNavigation();

  // takes array, render out 
   return (
    <FlatList
      data={data}
      horizontal
      keyExtractor={(item) => item.id} // Assigns every element of FlatList to id
      renderItem={({ item }) => (
        <TouchableOpacity 
          style={tw`p-2 pl-6 pb-8 pt-4 bg-gray-200 m-2 w-40`}
          onPress={() => navigation.navigate(item.screen)}
        >
          <View>
            <Image
              style={{width: 120, height: 120, resizeMode: "contain"}}
              source={{ uri: item.image }}
            />
            <Text style={tw`mt-2 text-lg font-semibold`}>{item.title}</Text>
            <Icon 
              style={tw`p-2 bg-black rounded-full w-10 mt-4`}
              name="arrowright" 
              color="white" 
              type="antdesign"
            />
          </View>
        </TouchableOpacity>
      )} // end renderItem
    />
   );
 };
 
 export default NavOptions;