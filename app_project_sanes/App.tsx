import React from 'react';
import { StatusBar } from 'react-native';
import { AuthProvider } from './src/contexts/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <StatusBar 
        barStyle="dark-content" 
        backgroundColor="#F8FAFC" 
        translucent={false}
      />
      <AppNavigator />
    </AuthProvider>
  );
};

export default App;
