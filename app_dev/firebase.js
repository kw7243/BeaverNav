import { initializeApp } from "firebase/app";
import {
  getFirestore,
  collection,
  setDoc,
  doc,
  getDoc,
  addDoc,
  query,
  where,
  getDocs,
  updateDoc,
  orderBy,
} from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyBjGpM4HAuuXc02b_TFKuy7gHjoPH_s-No",

  authDomain: "mit-building-maps-f6ee8.firebaseapp.com",

  projectId: "mit-building-maps-f6ee8",

  storageBucket: "mit-building-maps-f6ee8.appspot.com",

  messagingSenderId: "445831994131",

  appId: "1:445831994131:web:af2ed981807be0e62258e6",

  measurementId: "G-W1T8H70TXV"
};
if (Object.keys(firebaseConfig).length == 0) {
  console.log(
    "\n" +
      "-".repeat(50) +
      "\n\n" +
      "In firebase.js there should be a firebaseConfig. " +
      "It's secret, ask Raul for it " +
      "or find it in the firebase console at " +
      "https://console.firebase.google.com/project/mit-building-maps-f6ee8/settings/general/web:ZWZkNTE1N2EtYTM0Yi00MzM2LTlmMmQtY2ZkNmIzZjQ4NTMw" +
      "\n\n" +
      "-".repeat(50) +
      "\n"
    // "background: #222; color: #bada55"
  );
}

const firebaseApp = initializeApp(firebaseConfig);
let db = getFirestore(firebaseApp);
const NODE_COLLECTION = "Node";
const EDGE_COLLECTION = "Edge";

/**
 * Tries to find if there is a Document in a given collection
 * with a given field values. If there is not, returns null. Otherwise returns
 * the document object.
 *
 * @param {String} collection_name
 * @param {Array[String]} field_name
 * @param {Array[String]} field_val
 * @returns
 */
const findDoc = async (collection_name, field_names, field_vals) => {
  //TODO: Make sure that field_names and field_vals are arrays with same length
  console.log("Trying to find a doc..");
  let q = collection(db, collection_name);
  for (let i = 0; i < field_names.length; i++) {
    let field_name = field_names[i];
    let field_val = field_vals[i];
    console.log(`Adding ${field_name}: ${field_val} to the query`);
    q = query(q, where(field_name, "==", field_val));
  }
  const nodes = await getDocs(q);
  if (!nodes.empty) {
    console.log("found");
    const node = nodes.docs[0];
    return node;
  } else {
    console.log("not found!");
    return null;
  }
};
/**
 * Creates Node object
 * @param {String} node_name : name of node
 * @param {*} x : 3d x-position of the node
 * @param {*} y : 3d y-position of the node
 * @param {*} z : 3d z-position of the node
 * @returns a reference to the node object newly created (or the one that already existed)
 */
const addNode = async (node_name, x, y, z) => {
  //first check if it already exists
  let node = await findDoc(NODE_COLLECTION, ["name"], [node_name]);
  if (node != null) {
    console.log(
      `There is already a Node with this name (id = ${node.id}). Won't create new one.`
    );
    return node;
  }
  console.log("Node didnt exist, creating...");
  //if it doesn't, create it
  const docRef = await addDoc(collection(db, NODE_COLLECTION), {
    name: node_name,
    x: x,
    y: y,
    z: z,
  });
  console.log("Document written with ID: ", docRef.id);
  return docRef;
};

/**
 * Adds start and end having start < end (lexicographically)
 * TODO: Does it make sense for our graph to have directed edges or should they be undirected?
 *
 * This requires both nodes to already exist (`addNode` method)
 * This method creates a new edge with a given weight if it doesn't exist. If it
 * does, it updates the weight instead.
 * @param {String} start_name
 * @param {String} end_name
 * @param {*}
 */
const addEdge = async (start_name, end_name, weight) => {
  console.log("Trying to add edge...");

  if (start_name === end_name) {
    console.log("Edges cannot have the same node names!");
    return;
  }
  // Ordering the names such that start < end
  if (start_name > end_name) {
    let prev = start_name;
    start_name = end_name;
    end_name = prev;
  }
  //First lets make sure both nodes already exist
  const start_node = await findDoc(NODE_COLLECTION, ["name"], [start_name]);
  if (start_node == null) {
    console.log(
      `start_name (${start_name}) does not exist. Please create a node with the addNode method.`
    );
    return;
  }
  const end_node = await findDoc(NODE_COLLECTION, ["name"], [end_name]);
  if (end_node == null) {
    console.log(
      `end_node (${end_name}) does not exist. Please create a node with the addNode method first.`
    );
    return;
  }
  console.log(
    "Confirmed that both nodes exist, now trying to create/update edge"
  );
  //Now lets see if there is already an edge with both start and end
  const edge = await findDoc(
    EDGE_COLLECTION,
    ["start_name", "end_name"],
    [start_name, end_name]
  );

  if (edge != null) {
    //There is one already, so just update the weight
    console.log(
      `Found edge with same endpoints and weight ${weight} (id = ${edge.id})`
    );
    let prev_weight = edge.data().weight;
    console.log(`Previous weight: ${prev_weight}`);
    const edgeRef = doc(db, EDGE_COLLECTION, edge.id);
    let newEdge = await updateDoc(edgeRef, {
      weight: weight,
    });
    // Adding this console.log for some reason breaks stuff, maybe .data() has not been propagated yet?
    // console.log(`Updated from ${prev_weight} to ${newEdge.data().weight}`);
    return newEdge;
  } else {
    //There is none, so create one
    console.log("Not edge found, creating new one");
    let newEdge = await addDoc(collection(db, EDGE_COLLECTION), {
      weight: weight,
      start_name: start_name,
      start_id: start_node.id,
      end_name: end_name,
      end_id: end_node.id,
    });
    console.log(`Edge created with id = ${newEdge.id}`);
    return newEdge;
  }
};

/**
 * Returns a list of node objects and the a mapping from their id to their positions
 *
 * For example, if list of nodes = [{id: 10, name:'a'}, {id: 30, name:'b'}, {id: 20, name:'c'}]
 * then `positions` would be {10: 0, 20: 2, 30: 1}
 *
 * @returns {Array} [nodes, positions]
 */
const getNodes = async () => {
  let node_docs = await getDocs(
    query(collection(db, NODE_COLLECTION), orderBy("name"))
  );
  let docs = node_docs.docs; // extract the objects
  console.log(`Found ${docs.length} nodes`);
  //Adding the _id to the objects
  let nodes = [];
  let positions = {};
  for (let [i, doc] of docs.entries()) {
    let data = doc.data();
    data["_id"] = doc.id;
    nodes.push(data);
    positions[doc.id] = i;
  }

  return [nodes, positions];
};
/**
 * @returns a list of all the edges in the database, each augmented with their `_id`
 */
const getEdges = async () => {
  let edges = await getDocs(collection(db, EDGE_COLLECTION));
  let docs = edges.docs; // extract the objects
  let res = [];
  for (let [i, doc] of docs.entries()) {
    let data = doc.data();
    data["_id"] = doc.id;
    res.push(data);
  }
  return res;
};
/**
 *
 * @returns a list of nodes and all the connections they have (see `astar.js`)
 */
const getGraph = async () => {
  let [nodes, positions] = await getNodes();
  let edges = await getEdges();
  let connections = [];
  for (let i = 0; i < nodes.length; i++) {
    connections.push([]);
  }
  for (let edge of edges) {
    let start_id = edge["start_id"];
    let start_index = positions[start_id];
    let end_id = edge["end_id"];
    let end_index = positions[end_id];
    connections[start_index].push(end_index);
    connections[end_index].push(start_index);
  }

  return [nodes, connections];
};
/**
 * Another version of getGraph method, but this one makes
 * multiple API request to Firestore so it's probably slower.
 * However something like this could be useful if we wanted to get
 * just a part of the graph rather than everything
 */
// const getGraph2 = async () => {
//   let [nodes, positions] = await getNodes(); //list of node objects
//   let connections = [];
//   console.log(nodes);
//   // return;
//   for (let [i, node] of nodes.entries()) {
//     console.log(node._id, " => ", node);
//     let neighbors = [];
//     //Getting the nodes that start on it

//     let q_start = query(
//       collection(db, EDGE_COLLECTION),
//       where("start_id", "==", node._id)
//     );
//     let edges_start = await getDocs(q_start);
//     console.log("edges_start:");
//     edges_start.forEach((edge) => {
//       console.log(edge.id, " => ", edge.data());
//       neighbors.push(positions[edge.data()["end_id"]]);
//     });
//     let q_end = query(
//       collection(db, EDGE_COLLECTION),
//       where("end_id", "==", node._id)
//     );
//     let edges_end = await getDocs(q_end);
//     console.log("edges_end: ");
//     edges_end.forEach((edge) => {
//       console.log(edge.id, " => ", edge.data());
//       neighbors.push(positions[edge.data()["start_id"]]);
//     });
//     console.log("Done with node");
//     connections.push(neighbors);
//   }
//   console.log("Nodes = ", nodes);
//   console.log("Connections", connections);
//   return [nodes, connections];
// };

export { addNode, addEdge, getGraph };
