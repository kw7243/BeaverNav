import { StyleSheet, Text, View, Image } from 'react-native';
import React, { useState } from 'react';
import { get } from '../utilities';
import DirectionsCard from '../components/DirectionsCard';
import Map from '../components/Map';
import tw from 'tailwind-react-native-classnames';

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

    // Called when first loading DirectionsScreen
    // with origin + destination
    useEffect(() => {
        get(MULTIPLE_FLOORS_API).then((floorQueries) => {
            setFloorPlanQueries(floorQueries); // will have to check if GET response is an array
        });
    }, []);
    
    // Assumming response type is URI
    const floorPlanImageURI = get(SINGLE_FLOOR_API, floorPlanQueries[index]);

    return (
        <View>
            <View style={[tw`flex-initial h-5/6`]}>
                <Image 
                    style={{
                        width: "100%",
                        height: "100%",
                        aspectRatio: 1,
                    }}
                    resizeMode="contain"
                    source={{uri: floorPlanImageURI}}
                />
                {/* <Map/> */}
            </View>
            <View style={tw`h-1/6`}>
                <DirectionsCard 
                    floorPlanQueries={floorPlanQueries}
                    index={index}
                    setIndex={setIndex}
                />
            </View>
        </View>
    )
}

export default DirectionsScreen;
