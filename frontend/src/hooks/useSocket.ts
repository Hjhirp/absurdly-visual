import { useEffect, useState } from 'react';
import { Socket } from 'socket.io-client';
import { socketService } from '../services/socketService';

export const useSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const newSocket = socketService.connect();
    setSocket(newSocket);

    newSocket.on('connect', () => {
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      setIsConnected(false);
    });

    return () => {
      socketService.disconnect();
    };
  }, []);

  return { socket, isConnected };
};
