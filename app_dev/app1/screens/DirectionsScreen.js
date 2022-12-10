import { StyleSheet, Text, View, Image } from 'react-native';
import React, { useState, useEffect } from 'react';
import { get, post } from '../utilities';
import DirectionsCard from '../components/DirectionsCard';
import Map from '../components/Map';
import tw from 'tailwind-react-native-classnames';


import { useSelector } from 'react-redux';
import { selectOrigin, selectDestination } from '../slices/navSlice';

const DirectionsScreen = () => {
    const START_REQUEST_URL = "http://45.33.64.67/route";
    const REQUEST_IMAGE_URL = "http://45.33.64.67/route/images";

    // `index` tracks the current floor plan and displayed directions
    const [index, setIndex] = useState(0);
    const origin = useSelector(selectOrigin);
    const destination = useSelector(selectDestination);

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
     *   },
     *   {
     *     floorPlan: "2_2",
     *     start: "Room 43"
     *     end: "Room 12"
     *   }
     * ]
     */
    const [floorPlanQueries, setFloorPlanQueries] = useState([]);
    const [floorPlanImg, setFloorPlanImg] = useState(undefined) // base64 rep of blob

    // Called when first loading DirectionsScreen
    // with origin + destination
    useEffect(() => {
        post(START_REQUEST_URL, { origin, destination }).then((floorQueries) => {
            setFloorPlanQueries(floorQueries); // will have to check if GET response is an array
        });
        
    }, []);
    
    useEffect(() => {
        console.log(floorPlanQueries.length)
        if (index < floorPlanQueries.length) {
            console.log('getting image')
            console.log(floorPlanQueries[index].image_filepath)
            
            fetch(`${REQUEST_IMAGE_URL}?path=${encodeURIComponent(floorPlanQueries[index].image_filepath)}`).then(res => {
                res.blob().then(blob => {
                    // Look at https://stackoverflow.com/questions/38506971/react-native-populate-image-with-blob-that-has-been-converted-to-a-url
                    

                })
            })
        }
    }, [floorPlanQueries])

    // Assumming response type is URI

    return (
        <View>
            <View style={[tw`flex-initial h-5/6`]}>
                {
                floorPlanImg !== undefined &&
                <Image 
                    style={{
                        width: "100%",
                        height: "100%",
                        aspectRatio: 1,
                    }}
                    resizeMode="contain"
                    source={{ uri: floorPlanImg }}
                />
                }
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
