import { StatusBar } from "expo-status-bar";
import {
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { Provider } from "react-redux";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { store } from "./store";
import "react-native-gesture-handler";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import DirectionsScreen from "./screens/DirectionsScreen";
import NavSearchScreen from "./screens/NavSearchScreen";

export default function App() {
  // create stack for swiping through pages
  const Stack = createStackNavigator();

  return (
    <Provider store={store}>
      <NavigationContainer>
        <SafeAreaProvider>
          <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={{ flex: 1 }}
            keyboardVerticalOffset={Platform.OS === "ios" ? -64 : 0}
          >
            <Stack.Navigator>
              <Stack.Screen
                name="NavSearchScreen"
                component={NavSearchScreen}
                options={{
                  headerShown: false,
                  // gestureEnabled: false
                }}
              />
              <Stack.Screen
                name="DirectionsScreen"
                component={DirectionsScreen}
                options={{
                  headerShown: false,
                  // gestureEnabled: false
                }}
              />
            </Stack.Navigator>
          </KeyboardAvoidingView>
        </SafeAreaProvider>
      </NavigationContainer>
    </Provider>
  );
}
