import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import NavigateCard from '../components/NavigateCard'
import tw from "tailwind-react-native-classnames";
import Map from '../components/Map';

const NavSearchScreen = () => {
    return (
        <View>
            <View style={tw`h-1/2`}>
                <Map/>
            </View>
            <View style={tw`h-1/2`}>
                <NavigateCard/>
            </View>
        </View>
    )
}

export default NavSearchScreen

const styles = StyleSheet.create({})