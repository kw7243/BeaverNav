import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button, Image, TextInput } from 'react-native';
import React, { useState } from 'react';
import { useFonts } from 'expo-font';
import { 
  Cabin_400Regular,
  Cabin_400Regular_Italic,
  Cabin_500Medium,
  Cabin_500Medium_Italic,
  Cabin_600SemiBold,
  Cabin_600SemiBold_Italic,
  Cabin_700Bold,
  Cabin_700Bold_Italic 
} from '@expo-google-fonts/cabin'
import AppLoading from 'expo-app-loading'


export default function App() {
  
  let [fontsLoaded, error] = useFonts({
    Cabin_400Regular,
    Cabin_400Regular_Italic,
    Cabin_500Medium,
    Cabin_500Medium_Italic,
    Cabin_600SemiBold,
    Cabin_600SemiBold_Italic,
    Cabin_700Bold,
    Cabin_700Bold_Italic 
  })

  if (!fontsLoaded) {
    return <AppLoading />
  }


  return (
    <View style={styles.body}>
      <Text style={styles.text}> BeaverNav </Text>
      <View> 
        <Image 
        style={{
          resizeMode: "cover",
          height: 100,
          width: 100,
          resizeMode: 'stretch',
        }}
        source={require('./assets/nav.png')} 
        />
      </View>
      <View> 
      <Image 
          style={{
            resizeMode: "cover",
            height: 200,
            width: 300,
            left: 20,
            bottom: 20,
            resizeMode: 'stretch',
          }}
        source={require('./assets/tim.png')} />
      </View>
      <Button title='Get Started'> style={styles.button} </Button>
      <TextInput style={styles.input} placeholder='Enter Start Location' /> 
      
      <View style={styles.body2}>
        <Text style={{fontFamily: 'Cabin_700Bold'}}> Kevin, Michael, Vasu, and Yajvan </Text>
      </View>
    </View>
    
  );
}

const styles = StyleSheet.create({
  body: {
    flex: 1,
    backgroundColor: '#ffb6c1',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 10,
    borderColor: '#dc143c',
    borderRadius: 10,
    margin: 0,

  },
  body2: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginTop: 20,
  },

  text: {
    color: 'red',
    fontSize: 80,
    margin: 10,
    fontFamily: 'Cabin_400Regular'
  },
  text2: {
    color: 'black',
    fontSize: 20,
    justifyContent: 'flex-end',
    margin: 10,
    top: 150,
  },
  button: {
    width: 100,
    height: 60,
    fontFamily: 'Cabin_400Regular'
  },
  input: {
    width:200,
    height:30,
    borderWidth: 2,
    borderColor: 'black',
    borderRadius: 5, 
    textAlign: 'center',
    fontsize: 20,
  }
});
