export interface Tweet {
  id: string;
  text: string;
  user: {
    name: string;
    username: string;
    avatar: string;
  };
  createdAt: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  engagement: {
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