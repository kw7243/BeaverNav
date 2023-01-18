import { StatusBar } from 'expo-status-bar';
import { useState } from 'react';
import { Button, Linking, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

export default function App() {
  const [name, setName] = useState("");
  const [submitted, setPressed] = useState(false);

  return (
    <View style={styles.body}>

      <TextInput 
        placeholder="Type name..." 
        style={styles.input}
        onChangeText={(value) => setName(value)}
      />

      <Pressable>
        <Text></Text>

      </Pressable> 
      {submitted ? 
        <Text> Your name: {name} </Text>
        :
        null
      }
    </View>
  );
}

const styles = StyleSheet.create({
  body: {
    flex: 1,
    backgroundColor: "#ffff",
    alignItems: "center", 
    justifyContent: "center"
  },
  text: {
    fontSize: 20,
  },
  input: {
    width: 200,
    height: 30,
    borderWidth: 1
  }
});
