import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import tw from 'tailwind-react-native-classnames'
import { TouchableOpacity } from 'react-native-gesture-handler'
import { Icon } from 'react-native-elements'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useNavigation } from '@react-navigation/native'


/**
 * Proptypes
 * @param {FloorPlanQuery[]} floorPlanQueries
 * @param {number} index tracks index in floorPlanQueries at which to GET (pixel1, pixel2) path
 * @param {(index) => void} setIndex (function) sets index
 */

const DirectionsCard = (props) => {
    const navigation = useNavigation();

    const incrementIndex = () => {
        if (props.index < props.floorPlanQueries.length - 1) {
            props.setIndex(props.index + 1);
        } // if not at destination
        else {
            navigation.navigate("NavSearchScreen");
        }
    };

    const decrementIndex = () => {
        if (props.index > 0) {
            props.setIndex(props.index - 1);
        }
        else {
            navigation.navigate("NavSearchScreen");
        }
    };


    return (
        <View style={tw`flex-auto`}>
            <View 
                    style={tw`flex py-3 px-5 bg-black bg-opacity-90`}
                    onLayout={(event) => {
                        const layout = event.nativeEvent.layout;
                        // save layout.height somewhere accessible by DirectionsScreen
                    }}
                    >
                <Text style={tw`text-center text-white font-bold text-xl`}> 
                    {props.index < props.floorPlanQueries.length && props.floorPlanQueries[props.index].text}
                </Text>
            </View>
            <SafeAreaView style={tw`flex-none absolute bottom-0 inset-x-0 flex-row justify-between`}>
                <TouchableOpacity
                    onPress={() => {
                        decrementIndex();
                    }}
                >
                    <Icon 
                        style={tw`p-2 bg-black rounded-full w-20 mt-4 mx-4`}
                        name="arrowleft" 
                        color="red" 
                        type="antdesign"
                    />
                </TouchableOpacity>

                <View style={tw`flex-row justify-center mt-auto`}>
                    <View style={tw`p-2 mt-4 bg-red-500 rounded-full w-20`}>
                        <TouchableOpacity
                            onPress={() => {
                                navigation.navigate("NavSearchScreen");
                            }}
                        >
                            <Text style={tw`text-white font-bold text-xl text-center`}>
                                End
                            </Text>
                        </TouchableOpacity>
                    </View>
                </View>
                
                {props.index < props.floorPlanQueries.length - 1 ?
                    <TouchableOpacity
                        onPress={() => {
                            incrementIndex();
                        }}
                    >
                        <Icon 
                            style={tw`p-2 bg-black rounded-full w-20 mt-4 mx-4`}
                            name="arrowright" 
                            color="red" 
                            type="antdesign"
                        />
                    </TouchableOpacity>
                    :
                    null
                }
            </SafeAreaView>

        </View>
  )
}

export default DirectionsCard;

const styles = StyleSheet.create({});