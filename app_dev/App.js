import { StatusBar } from "expo-status-bar";
import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  TextInput,
  View,
  Image,
  Dimensions,
  ImageBackground,
  SafeAreaView,
  LogBox, // For getting rid of annoying log warnings (https://github.com/facebook/react-native/issues/12981)
} from "react-native";
import ImageZoom from "react-native-image-pan-zoom";
LogBox.ignoreLogs(["Warning: Setting a timer"]); // For getting rid of annoying log warnings (https://github.com/facebook/react-native/issues/12981)

import { SearchBar, Button } from "react-native-elements";
import Directions from "./Directions.js";
import Search from "./Search.js";
import { addNode, addEdge, getGraph } from "./firebase.js";
import {a_star} from './astar.js'
const d = Dimensions.get("window");


const n1 = {
  name: "a",
  x: 100,
  y: 100,
  z: 0,
};

const n2 = {
  name: "b",
  x: 100,
  y: 200,
  z: 0
};

const n3 = {
  name: "c",
  x: 200,
  y: 200,
  z: 0
};

const n4 = {
  name: "d",
  x: 300,
  y: 300,
  z: 1
};

const n5 = {
  name: "e",
  x: 100,
  y: 350,
  z: 0
};

const n6 = {
  name: "f",
  x: 50,
  y: 200,
  z: 0,
};

const n7 = {
  name: "g",
  x: 50,
  y: 100,
  z: 0
};

const n8 = {
  name: "h",
  x: 100,
  y: 400,
  z: 0
};

const n9 = {
  name: "i",
  x: 100,
  y: 50,
  z: 1
};

const n10 = {
  name: "j",
  x: 300,
  y: 50,
  z: 0
};

//function getGraph() {
//  return [[n1,n2,n3,n4,n5,n6,n7,n8,n9,n10],[[1,2,6],[0,2],[0,1,3],[2,7],[5],[4,6,8],[0,5],[3,4],[5,9],[8]]];
//}

let nodes = null;
let edges = null;

export default function App() {
  let [path, setPath] = useState(null);
  let [nodes, setNodes] = useState(null);
  let [edges, setEdges] = useState(null);
  //This will be ran only once (at the beginning)
  useEffect(async () => {
    graph = await getGraph();
    setNodes(graph[0]);
    setEdges(graph[1]);
  }, []);
  
  const updatePath = (start,end) => {
    console.log(start);
    console.log(end);
    let start_index = -1;
    let end_index = -1;
    for (let i=0; i<nodes.length; i++) {
      console.log(nodes[i].name);
      if (nodes[i].name == start) {
        start_index = i;
      }
      if (nodes[i].name == end) {
        end_index = i;
      }
    }
    setPath(a_star(nodes,edges,start_index,end_index));
  };
  const demo = async () => {
    console.log("aaaa - starting");
    try {
      await addNode("a", 100, 100, 0); //n1
      await addEdge("i", "j", 0);
      console.log("hehe");
    } catch (e) {
      console.error("Error adding document: ", e);
    }
    console.log("aaaa - ending");
  };
  return (
    <View style = {styles.background}>
        <ImageZoom cropWidth={d.width}
                    cropHeight={d.height-200}
                    imageWidth={5000}
                    imageHeight={5000}
                    maxOverflow={1000}
                    minScale={0.1}
                    maxScale={100}
                    enableCenterFocus={false}>
            <Directions path = {path} nodes = {nodes} edges = {edges} height = {5000} width = {5000} uri = {"https://drive.google.com/uc?id=1--kPRgt3169cOsD1g-kYVIGvo5YBoQZi"}/>
        </ImageZoom>


      <SafeAreaView style={styles.container}>
        <Search style={styles.searchbar} update_start_end={updatePath}/>
      </SafeAreaView>
  </View>
 
 );
}

const styles = StyleSheet.create({
 background: {
  //backgroundColor: 'yellow',
 },
 container: {
   
   //flex:1,
   justifyContent: 'flex-end',
   backgroundColor: 'green',
   //justifyContent:'center',
   width:'100%',

   //alignContent:'center',
   position:'absolute',

   //backgroundColor: '#fff',

   //justifyContent:'space-evenly',
  
 },
 image: {
  width:d.width+300,
  height:d.height+100,
  //resizeMode: 'cover',

 },
searchbar:{
  //width:d.width+300,
  //height:d.height+100,

},
});
