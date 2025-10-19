const API_URL = process.env.REACT_APP_API_URL || 'https://absurdly-visual-production.up.railway.app';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_URL}/api`;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  }

  async getBlackCards() {
    return this.get('/cards/black');
  }

  async getWhiteCards() {
    return this.get('/cards/white');
  }

  async getGame(gameId: string) {
    return this.get(`/game/${gameId}`);
  }

  async getGameState(gameId: string, playerId: string) {
    return this.get(`/game/${gameId}/state/${playerId}`);
  }

  async listGames() {
    return this.get('/games');
  }

  async getStats() {
    return this.get('/stats');
  }
}

export const apiService = new ApiService();
