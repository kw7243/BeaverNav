import { StyleSheet, Text, View, Animated } from 'react-native';
import React, { useState, useRef, useEffect } from 'react';
import { PanGestureHandler, PinchGestureHandler, State } from 'react-native-gesture-handler';
import DirectionsCard from '../components/DirectionsCard';
import tw from 'tailwind-react-native-classnames';
import { useSelector } from 'react-redux';
import { selectDestination, selectOrigin } from '../slices/navSlice';

const floorPlanQueries = [
  {
    floor_plan: "4_1",
    start_location: "Building 4 entrance",
    end_location: "Building 2",
    src: require("../local_test/4_1.png")
  },
  {
    floor_plan: "2_1",
    start_location: "Building 2 entrance from building 4",
    end_location: "Building 6",
    src: require("../local_test/2_1.png")
  },
  {
    floor_plan: "6_1",
    start_location: "Building 6 entrance from building 2",
    end_location: "Room 6-132",
    src: require("../local_test/6_1.png")
  }
];

const get = (endpoint, floorPlanQuery) => {
  return floorPlanQuery.src;
};

const DirectionsScreen = () => {
  const MULTIPLE_FLOORS_API = "http://127.0.0.1:5000/interfloorplan";
  const SINGLE_FLOOR_API = "http://127.0.0.1:5000/intrafloorplan";

  const [index, setIndex] = useState(0);
  const [floorPlanImage, setFloorPlanImage] = useState(null);
  const floorPlanURI = `data:image/png;base64,${floorPlanImage}`
  const { startLocation, endLocation } = useSelector(state => ({
    startLocation: selectOrigin(state),
    endLocation: selectDestination(state)
  }))

  useEffect(() => {
    const fetchFloorData = async () => {
      try {
        const response = await fetch(MULTIPLE_FLOORS_API, {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
          body: JSON.stringify({
            floor_plan: "",
            start_location: startLocation,
            end_location: endLocation
          })
        });
        
        if (!response.ok) {
          throw new Error("Failed to fetch image");
        }

        let data = await response.json();
        data = data['path_list'];
        console.log(data)
        // Assuming the response data is an array of path objects
        // [{ floorPlan: "26_1", start: "Room 100", end: "Room 121" }, ...]
        // We will get the last floorPlan in the path as it represents the destination floorPlan
        const destinationFloorPlan = data[index]?.floorplan;
        if (destinationFloorPlan) {
          const intraFloorData = {
            floor_plan: destinationFloorPlan,
            start_location: data[index]?.["start location"],
            end_location: data[index]?.["end location"],
          };
          fetchFloorImage(intraFloorData);
        }
      } catch (error) {
        console.error("Error fetching floor data:", error);
      }
    };

    const fetchFloorImage = async (intraData) => {
      try {
        const response = await fetch(SINGLE_FLOOR_API, {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
          body: JSON.stringify(intraData)
        });
        if (!response.ok) {
          throw new Error("Failed to fetch image");
        }

        const data = await response.json();
        // Assuming the response contains the image URI as "image_uri"
        const source = data.image;
        setFloorPlanImage(source);
      } catch (error) {
        console.error("Error fetching floor image:", error);
      }
    };

    fetchFloorData();
  }, [index]);
  const scale = useRef(new Animated.Value(1)).current;
  const translateX = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(0)).current;

  const onPinchEvent = Animated.event(
    [{ nativeEvent: { scale } }],
    { useNativeDriver: true }
  );

  const onPanEvent = Animated.event(
    [
      {
        nativeEvent: {
          translationX: translateX,
          translationY: translateY,
        },
      },
    ],
    { useNativeDriver: true }
  );

  const handlePinchStateChange = ({ nativeEvent }) => {
    // when scale < 1, reset scale back to original (1)
    const nScale = nativeEvent.scale;
    if (nativeEvent.state === State.END) {
      if (nScale < 1) {
        Animated.spring(scale, {
          toValue: 1,
          useNativeDriver: true,
        }).start();
        Animated.spring(translateX, {
          toValue: 0,
          useNativeDriver: true,
        }).start();
        Animated.spring(translateY, {
          toValue: 0,
          useNativeDriver: true,
        }).start();
      }
    }
  };

  const imageStyle = [
    styles.image,
    {
      transform: [
        { scale },
        { translateX },
        { translateY },
      ],
    },
  ];

  return (
    <View style={styles.container}>
      <View style={[tw`flex-initial h-5/6`]}>
        <PanGestureHandler onGestureEvent={onPanEvent}>
          <Animated.View>
            <PinchGestureHandler onGestureEvent={onPinchEvent} onHandlerStateChange={handlePinchStateChange}>
              <Animated.View>
                {floorPlanImage && ( // Check if the image source is available before rendering
                  <Animated.Image
                    style={imageStyle}
                    resizeMode="contain"
                    source={{ uri: floorPlanURI }} // Use the image source as a URI
                  />
                )}
              </Animated.View>
            </PinchGestureHandler>
          </Animated.View>
        </PanGestureHandler>
      </View>
      <View style={tw`h-1/6`}>
        <DirectionsCard
          floorPlanQueries={floorPlanQueries}
          index={index}
          setIndex={setIndex}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'pink',
  },
  image: {
    width: '80%',
    height: '80%',
    aspectRatio: 1,
  },
});

export default DirectionsScreen;
