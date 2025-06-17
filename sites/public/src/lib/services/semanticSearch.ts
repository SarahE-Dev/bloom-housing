import axios from 'axios';

interface SearchResult {
  provider: string;
  services: string;
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
}

export const semanticSearch = async (query: string): Promise<SearchResponse> => {
  try {
    const response = await axios.post('http://localhost:5001/search', {
      query,
      top_n: 5
    });
    return response.data;
  } catch (error) {
    console.error('Error performing semantic search:', error);
    throw error;
  }
}; 