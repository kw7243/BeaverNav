import { StatusBar } from 'expo-status-bar';
import { KeyboardAvoidingView, Platform, StyleSheet, Text, View } from 'react-native';
import { Provider } from "react-redux";
import { SafeAreaProvider } from "react-native-safe-area-context";

import HomeScreen from './screens/HomeScreen';
import MapScreen from './screens/MapScreen';

import { store } from './store';
import "react-native-gesture-handler";
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

export default function App() {
  // create stack for swiping through pages
  const Stack = createStackNavigator();

  return (
    <Provider store={store}>
      <NavigationContainer>
        <SafeAreaProvider>
          <KeyboardAvoidingView 
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={{flex: 1}}
            keyboardVerticalOffset={Platform.OS === "ios" ? -64 : 0}
          >
            <Stack.Navigator>
              {/* <Stack.Screen
                name="HomeScreen"
                component={HomeScreen}
                options={{
                  headerShown: false
                }}
              /> */}
              <Stack.Screen
                name="MapScreen"
                component={MapScreen}
                options={{
                  headerShown: false
                }}
              />
            </Stack.Navigator>
          </KeyboardAvoidingView>
       </SafeAreaProvider>
      </NavigationContainer>
    </Provider>
  );
}

