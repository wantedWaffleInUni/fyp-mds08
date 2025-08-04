export interface EncryptResponse {
    image_url: string;
    permutation: number[];
    key_stream: number[];
  }
  
  export interface DecryptResponse {
    image_url: string;
  }
  
  export interface AnalysisResponse {
    npcr: number;
    uaci: number;
  }
  