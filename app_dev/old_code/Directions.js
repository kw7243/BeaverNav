import React from 'react';
import { StyleSheet, Text, View, Image, Dimensions, ImageBackground } from 'react-native';
import Svg, {Path, Circle, SvgUri} from 'react-native-svg';
import a_star from './astar.js'

export default class Directions extends React.Component {
    constructor(props) {
        super(props);
        this.state = {"floor": 0};
    }

    prepareData() {
        let circles = [];
        let path = ``;
        let connections = [];
        let prevKey = -1;

        if (this.props.nodes != null && this.props.edges != null) {
            for (let i=0; i<this.props.nodes.length; i++) {
                for (let j=0; j<this.props.edges[i].length; j++) {
                    let node1 = this.props.nodes[i];
                    let node2 = this.props.nodes[this.props.edges[i][j]];
                    prevKey += 1;
                    connections.push(<Path d = {`M${node1.x} ${node1.y} L${node2.x} ${node2.y}`} 
                        stroke="red"
                        strokeWidth={5}
                        fill="none"
                        key = {prevKey}
                        />);
                }
            }
        }

        if (this.props.path != null && this.props.path != -1 && this.props.path != "") {
            path = `M ${this.props.path[0][0]} ${this.props.path[0][1]}`;
            let on_floor = (this.props.path[0][2] == this.state["floor"]);
            let previous_on_floor = this.props.path[0];
            if (on_floor) {
                prevKey += 1;
                circles.push(<Circle cx={this.props.path[0][0]} cy={this.props.path[0][1]} r="10" fill="green" key={prevKey}/>)
            }

            for (let i=1; i<this.props.path.length; i++) {
                if (this.props.path[i][2] == this.state["floor"]) {
                    if (on_floor) {
                        path += ` L${this.props.path[i][0]} ${this.props.path[i][1]}`;
                    } else {
                        path += ` M${this.props.path[i][0]} ${this.props.path[i][1]}`;
                        on_floor = true;
                        prevKey += 1;
                        circles.push(<Circle cx={this.props.path[i][0]} cy={this.props.path[i][1]} r="10" fill="yellow" key={prevKey}/>)
                        prevKey += 1;
                        connections.push(<Path d = {`M${previous_on_floor[0]} ${previous_on_floor[1]} L${this.props.path[i][0]} ${this.props.path[i][1]}`} 
                        stroke="red"
                        strokeWidth={5}
                        fill="none"
                        key = {previous_on_floor}
                        />);
                    }
                    previous_on_floor = this.props.path[i];
                } else {
                    if (on_floor) {
                        prevKey += 1;
                        circles.push(<Circle cx={this.props.path[i-1][0]} cy={this.props.path[i-1][1]} r="10" fill="yellow" key={prevKey}/>)
                    }
                    on_floor = false;
                }
            }
            if (on_floor) {
                prevKey += 1;
                circles.push(<Circle cx={this.props.path[this.props.path.length-1][0]} cy={this.props.path[this.props.path.length-1][1]} r="10" fill="green" key={prevKey}/>)
            } else {
                prevKey += 1;
                circles.push(<Circle cx={this.props.path[this.props.path.length-1][0]} cy={this.props.path[this.props.path.length-1][1]} r="10" stroke="green" strokeWidth="3" strokeDasharray="2 2" key={prevKey}/>)
            }
        }

        return [path, circles, connections];
    }

    render() {
        let data = this.prepareData();
        return (
            <Svg height={this.props.height} width={this.props.width}>
                <SvgUri
                    width="100%"
                    height="100%"
                    uri={this.props.uri}
                />
                {data[2]}
                <Path d = {data[0]} 
                    stroke="yellow"
                    strokeWidth={5}
                    fill="none"
                />
                {data[1]}
            </Svg> 

        )
    }
}