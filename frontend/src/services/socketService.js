import { io } from 'socket.io-client';

let socket;

export const connectToSocket = () => {
  if (!socket) {
    // Connect to the WebSocket server
    socket = io({
      path: '/socket.io',
      transports: ['websocket']
    });
    
    // Set up error handling
    socket.on('error', (error) => {
      console.error('Socket error:', error);
    });
    
    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
    });
  }
  
  return socket;
};

export const disconnectFromSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};
