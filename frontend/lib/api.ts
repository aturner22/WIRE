/**
 * WIRE API Client
 *
 * Handles all communication with the FastAPI backend
 */

import axios, { AxiosInstance } from 'axios'

// Types
export interface Location {
  id: string
  name: string
  address?: string
  latitude: number
  longitude: number
  timezone?: string
  created_at: string
  updated_at: string
}

export interface HazardFactor {
  [key: string]: any
}

export interface Citation {
  title: string
  authors?: string
  year?: number
  journal?: string
  publication?: string
  doi?: string
  url?: string
  methodology_location?: string
  additional?: string
}

export interface HazardResult {
  hazard_type: string
  name: string
  score: number // 1-5
  risk_level: string // "Low", "Moderate", "High", "Very High", "Extreme"
  factors: HazardFactor
  recommendations: string[]
  citation: Citation
  confidence?: number
}

export interface HazardSummary {
  highest_risk: number
  high_risk_count: number
  medium_risk_count: number
  low_risk_count: number
}

export interface AllHazardsResponse {
  location_id: string
  location_name: string
  timestamp: string
  hazards: HazardResult[]
  summary: HazardSummary
  weather_data: {
    temperature: number
    humidity: number
    wind_speed: number
    description: string
  }
}

export interface LocationSearchResult {
  name: string
  latitude: number
  longitude: number
  country: string
  state?: string
}

export interface HazardType {
  type: string
  name: string
  description: string
}

export interface Methodology {
  hazard_type: string
  name: string
  description: string
  citation: Citation
}

export interface ForecastPoint {
  timestamp: number
  dt_txt: string
  hazards: Record<string, any>
  summary: {
    highest_risk: number
    average_risk: number
    hazards_above_moderate: number
  }
}

export interface ForecastResponse {
  location: {
    latitude: number
    longitude: number
    name: string
  }
  forecast_hours: number
  forecasts: ForecastPoint[]
}

/**
 * API Client Class
 */
class WireAPI {
  private client: AxiosInstance
  private baseURL: string

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseURL = baseURL
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          // Server responded with error
          console.error('API Error:', error.response.data)
          throw new Error(error.response.data.detail || 'API request failed')
        } else if (error.request) {
          // Request made but no response
          console.error('Network Error:', error.request)
          throw new Error('Network error - please check backend is running')
        } else {
          // Something else went wrong
          console.error('Error:', error.message)
          throw error
        }
      }
    )
  }

  // ==================== LOCATIONS ====================

  /**
   * Search for locations using geocoding
   */
  async searchLocations(query: string): Promise<LocationSearchResult[]> {
    const response = await this.client.get('/locations/search', {
      params: { q: query },
    })
    return response.data
  }

  // ==================== HAZARDS ====================

  /**
   * Get hazards directly from coordinates
   */
  async getHazardsByCoordinates(
    lat: number,
    lon: number,
    name: string = "Unknown Location"
  ): Promise<AllHazardsResponse> {
    const response = await this.client.get(`/hazards`, {
      params: { lat, lon, name },
    })
    return response.data
  }

  /**
   * Get list of all hazard types
   */
  async getHazardTypes(): Promise<HazardType[]> {
    const response = await this.client.get('/types')
    return response.data
  }

  /**
   * Get all methodologies
   */
  async getMethodologies(): Promise<Methodology[]> {
    const response = await this.client.get('/methodologies')
    return response.data
  }

  /**
   * Get methodology for a specific hazard
   */
  async getMethodology(hazardType: string): Promise<Methodology> {
    const response = await this.client.get(`/methodologies/${hazardType}`)
    return response.data
  }

  /**
   * Get hazard forecast for a location
   */
  async getHazardForecast(
    lat: number,
    lon: number,
    name: string,
    hours: number = 120
  ): Promise<ForecastResponse> {
    const response = await this.client.get('/hazards/forecast', {
      params: { lat, lon, name, hours },
    })
    return response.data
  }

  // ==================== UTILITY ====================

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await axios.get(`${this.baseURL}/health`)
    return response.data
  }
}

// Export singleton instance
export const api = new WireAPI()

// Export class for custom instances
export default WireAPI
