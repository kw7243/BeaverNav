import React from 'react';
import { StyleSheet, View, Text } from 'react-native';

export default function NavLoc() {
    return (
        <View style={styles.container}> 
            <Text> NavLoc </Text> 
        </View>
    )
}

const styles = StyleSheet.create({
    container: {
        padding: 24
    }
});