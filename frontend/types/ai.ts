export interface AISummary {
  summary: string;
  strengths: string[];
  risks: string[];
  recommendations: string[];
  source: string;
  based_on: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  source: string;
}
