import { StyleSheet, Text, View } from 'react-native';
import React, { useState } from 'react';
import { post, get } from '../utilities';

const DirectionsScreen = () => {
    const MULTIPLE_FLOORS_API = "INSERT HERE";
    const SINGLE_FLOOR_API = "INSERT HERE";

    // `index` tracks the current floor plan and displayed directions
    const [index, setIndex] = useState(0);


    /**
     * floorPlanQueries stores a floor plan and 2 locations
     * within that floor plan between which to calculate a path 
     * from `SINGLE_FLOOR_API`
     * 
     * ex.
     * [
     *   {
     *     floorPlan: "26_1",
     *     start: "Room 100"
     *     end: "Room 121"
     *   }
     * ]
     */
    const [floorPlanQueries, setFloorPlanQueries] = useState([]);


    // called when first loading DirectionsScreen
    // with origin + destination
    // useEffect(() => {
    //     get(MULTIPLE_FLOORS_API).then((floorQueries) => {
    //         setFloorPlanQueries(floorQueries); // will have to check if GET response is an array
    //     });
    // }, []);
    

    return (
        <View>
            <Text>DirectionsScreen</Text>
        </View>
    )
}

export default DirectionsScreen;

const styles = StyleSheet.create({})