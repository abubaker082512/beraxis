# Frontend API Integration Guide

This guide details how to connect the existing Vite/React frontend to the newly built FastAPI backend for the Beraxis platform.

## 1. Environment Setup

Update your frontend `.env` (or `.env.local`) file:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## 2. Axios / Fetch Interceptor

All secure endpoints require a JWT Bearer token. Create an interceptor to automatically attach this and handle token refreshes.

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const res = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh`, {
          refresh_token: refreshToken
        });
        localStorage.setItem('access_token', res.data.data.access_token);
        localStorage.setItem('refresh_token', res.data.data.refresh_token);
        return api(originalRequest);
      } catch (err) {
        // Refresh failed, logout user
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

## 3. WebSocket Integration (Live Calls)

For the dashboard live view and agent simulator test:

```javascript
import { useEffect, useState } from 'react';

export function useLiveCall(callId) {
    const [transcripts, setTranscripts] = useState([]);
    
    useEffect(() => {
        if (!callId) return;
        
        const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}/calls/${callId}`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'transcript_partial') {
                // Update UI stream
            } else if (data.type === 'transcript_final') {
                setTranscripts(prev => [...prev, data.payload]);
            }
        };
        
        return () => ws.close();
    }, [callId]);
    
    return { transcripts };
}
```

## 4. Response Wrapping

The backend returns a standardized wrapper schema:
```typescript
interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}
```

When fetching data, make sure to access `.data.data`:
```javascript
const response = await api.get('/campaigns');
const campaigns = response.data.data; // Array of campaigns
```
