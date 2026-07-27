const API_BASE = 'https://attached-assets-0zuk.onrender.com';

export interface DiagnosedResponse {
  status: 'diagnosed';
  disease_name: string;
  crop_type: string;
  confidence: number;
  description: string;
  symptoms: string;
  is_healthy: boolean;
  recommendations: Array<{
    category: string;
    recommendation_text: string;
  }>;
}

export interface UncertainResponse {
  status: 'uncertain';
  predicted_class: string;
  confidence: number;
  message: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
}

export type PredictResponse = DiagnosedResponse | UncertainResponse | ErrorResponse;

export async function predictCropDisease(
  image: File,
  cropType: string
): Promise<PredictResponse> {
  const formData = new FormData();
  formData.append('image', image);
  formData.append('crop_type', cropType);

  const response = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();
  return data as PredictResponse;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/health`);
  const data = await response.json();
  return data as HealthResponse;
}
