export interface Tweet {
  id: string; // Mapeado desde 'id_post'
  text: string; // Mapeado desde 'texto'
  user: {
    name: string;     // El nuevo JSON tiene 'usuario' (ej: @EcuavisaInforma)
    username: string; // Podemos usar el mismo valor para ambos si no hay nombre completo
    avatar: string;   // Podríamos generar uno genérico si no viene en el JSON
  };
  createdAt: string; // Mapeado desde 'fecha'
  sentiment: 'POS' | 'NEG' | 'NEU'; // El backend devuelve POS/NEG/NEU, no 'positive'/'negative'
  confidence: number;
  // engagement: En el nuevo JSON no veo likes/retweets en el nivel superior, 
  // si no existen, hazlos opcionales:
  engagement?: {
    likes: number;
    retweets: number;
    replies: number;
  };
  platform: 'twitter' | 'facebook' | 'instagram';
}

export interface SentimentAnalysis {
  id: string;
  query: string;
  createdAt: string;
  tweets: Tweet[];
  summary: {
    total: number;
    positive: number;
    negative: number;
    neutral: number;
    uniqueUsers: {
      positive: number;
      negative: number;
      neutral: number;
    };
  };
  wordClouds: {
    positive: WordCloudItem[];
    negative: WordCloudItem[];
    neutral: WordCloudItem[];
  };
  comments?: string[];
  conclusion?: string;
}

export interface WordCloudItem {
  word: string;
  frequency: number;
}

export interface SearchFilters {
  query: string;
  dateFrom?: string;
  dateTo?: string;
  platforms: ('twitter' | 'facebook' | 'instagram')[];
  minEngagement?: number;
}


export type ViewType = 'home' | 'how-it-works' | 'compare';