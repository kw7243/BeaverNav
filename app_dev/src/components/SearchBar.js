import { StyleSheet, Text, View } from 'react-native'
import React from 'react'

/**
 * Proptypes
 * @param {string} placeholder 
 * @param {() => void} onSubmitEditing (function) what to when submit editing
 */
const SearchBar = (props) => {
    const dispatch = useDispatch();
    
    return (
        <View>
            <TextInput
                placeholder={props.placeholder}
                style={tw`p-2 bg-pink-200 flex-none text-lg rounded-md`}
                // onChangeText={(text) => setStartLocation(text)}
                onSubmitEditing={onSubmitEditing()}
            />
        </View>
    )
}

export default SearchBar

const styles = StyleSheet.create({})