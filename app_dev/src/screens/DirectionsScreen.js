import { StyleSheet, Text, View, Image, Animated } from 'react-native';
import React, { useState, useRef } from 'react';
import { PanGestureHandler, PinchGestureHandler, State } from 'react-native-gesture-handler';
import DirectionsCard from '../components/DirectionsCard';
import Map from '../components/Map';
import tw from 'tailwind-react-native-classnames';

const floorPlanQueries = [
  {
    floorPlan: "4_1",
    start: "Building 4 entrance",
    end: "Building 2",
    src: require("../local_test/4_1.png")
  },
  {
    floorPlan: "2_1",
    start: "Building 2 entrance from building 4",
    end: "Building 6",
    src: require("../local_test/2_1.png")
  },
  {
    floorPlan: "6_1",
    start: "Building 6 entrance from building 2",
    end: "Room 6-132",
    src: require("../local_test/6_1.png")
  }
];

const get = (endpoint, floorPlanQuery) => {
  return floorPlanQuery.src;
};

const DirectionsScreen = () => {
  const MULTIPLE_FLOORS_API = "INSERT HERE";
  const SINGLE_FLOOR_API = "INSERT HERE";

  const [index, setIndex] = useState(0);
  const floorPlanImage = get(SINGLE_FLOOR_API, floorPlanQueries[index]);

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
        <PinchGestureHandler onGestureEvent={onPinchEvent} onHandlerStateChange={handlePinchStateChange}>
          <Animated.View>
            <PanGestureHandler onGestureEvent={onPanEvent}>
              <Animated.Image
                style={imageStyle}
                resizeMode="contain"
                source={floorPlanImage}
              />
            </PanGestureHandler>
          </Animated.View>
        </PinchGestureHandler>
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
    width: '100%',
    height: '100%',
    aspectRatio: 1,
  },
});

export default DirectionsScreen;
