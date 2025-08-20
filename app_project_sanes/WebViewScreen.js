import React from 'react';
import { StyleSheet, View } from 'react-native';
import { WebView } from 'react-native-webview';

const WebViewScreen = () => {
  return (
    <View style={styles.container}>
      <WebView source={{ uri: '10.0.2.2:8000' }} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default WebViewScreen;
