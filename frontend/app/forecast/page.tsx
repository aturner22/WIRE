"use client"

import { useState, useEffect } from "react"
import { Calendar, MapPin, AlertTriangle, Clock } from "lucide-react"
import { api } from "@/lib/api"
import {
  getRiskColor,
  getRiskBgColor,
  getRiskLabel,
  getHazardIconComponent,
  getHazardName,
} from "@/lib/hazard-utils"

interface ForecastPoint {
  timestamp: number
  dt_txt: string
  hazards: Record<string, any>
  summary: {
    highest_risk: number
    average_risk: number
    hazards_above_moderate: number
  }
}

interface ForecastData {
  location: {
    latitude: number
    longitude: number
    name: string
  }
  forecast_hours: number
  forecasts: ForecastPoint[]
}

export default function ForecastPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number
    lon: number
    name: string
  } | null>(null)
  const [forecastData, setForecastData] = useState<ForecastData | null>(null)
  const [forecastHours, setForecastHours] = useState<120>(120)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setIsSearching(true)
    setError(null)
    try {
      const results = await api.searchLocations(searchQuery)
      setSearchResults(results)
    } catch (err: any) {
      setError(err.message || "Failed to search locations")
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleSelectLocation = async (location: any) => {
    const statePart = location.state ? `, ${location.state}` : ""
    setSelectedLocation({
      lat: location.latitude,
      lon: location.longitude,
      name: `${location.name}${statePart}, ${location.country}`,
    })
    setSearchResults([])
    setSearchQuery("")
    await fetchForecast(location.latitude, location.longitude, location.name)
  }

  const fetchForecast = async (lat: number, lon: number, name: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/hazards/forecast?lat=${lat}&lon=${lon}&name=${name}&hours=${forecastHours}`
      )
      if (!response.ok) throw new Error("Failed to fetch forecast")
      const data = await response.json()
      setForecastData(data)
    } catch (err: any) {
      setError(err.message || "Failed to fetch forecast data")
      setForecastData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedLocation) {
      fetchForecast(selectedLocation.lat, selectedLocation.lon, selectedLocation.name)
    }
  }, [forecastHours])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch()
  }

  const groupByDay = () => {
    if (!forecastData) return []
    const days = new Map<string, ForecastPoint[]>()
    forecastData.forecasts.forEach(f => {
      const date = f.dt_txt.split(" ")[0]
      if (!days.has(date)) days.set(date, [])
      days.get(date)!.push(f)
    })
    return Array.from(days.entries()).map(([date, points]) => {
      // Calculate max risk for each hazard type across the day
      const hazardMaxRisks: Record<string, number> = {}
      points.forEach(point => {
        Object.entries(point.hazards).forEach(([hazardType, hazard]: [string, any]) => {
          if (!hazardMaxRisks[hazardType] || hazard.score > hazardMaxRisks[hazardType]) {
            hazardMaxRisks[hazardType] = hazard.score
          }
        })
      })
      const overallMaxRisk = Math.max(...Object.values(hazardMaxRisks))
      return { date, points, hazardMaxRisks, overallMaxRisk }
    })
  }

  const dailyForecasts = groupByDay()

  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-8 py-5">
          <div className="flex items-center justify-between">
            <a href="/" className="flex items-center space-x-4">
              <div className="text-navy text-2xl font-semibold tracking-tight">WIRE</div>
              <div className="hidden md:block text-gray-400 text-sm font-light">Weather Induced Risk Exposure</div>
            </a>
            <nav className="flex items-center space-x-8">
              <a href="/dashboard" className="text-gray-600 hover:text-navy text-[15px] font-medium transition-colors">Dashboard</a>
              <a href="/forecast" className="text-navy font-medium text-[15px] border-b-2 border-accent pb-1">Forecast</a>
              <a href="/methodology" className="text-gray-600 hover:text-navy text-[15px] font-medium transition-colors">Methodology</a>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-8 py-12">
        <div className="max-w-3xl mx-auto mb-12">
          <div className="bg-white border border-gray-100 p-8">
            <h2 className="text-2xl font-semibold text-navy mb-6 flex items-center">
              <MapPin className="h-6 w-6 mr-3 text-accent" strokeWidth={1.5} />
              Location Selection
            </h2>
            <div className="flex gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter city name (e.g., London, UK)"
                className="flex-1 px-5 py-3.5 border border-gray-200 focus:ring-2 focus:ring-accent/20 focus:border-accent outline-none text-[15px] transition-all"
              />
              <button
                onClick={handleSearch}
                disabled={isSearching || !searchQuery.trim()}
                className="px-8 py-3.5 bg-navy text-white hover:bg-navy-secondary transition-all disabled:opacity-50 font-medium text-[15px]"
              >
                {isSearching ? "Searching..." : "Search"}
              </button>
            </div>

            {searchResults.length > 0 && (
              <div className="mt-4 border border-gray-200 divide-y max-h-60 overflow-y-auto">
                {searchResults.map((result, idx) => {
                  const stateText = result.state ? `${result.state}, ` : ""
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelectLocation(result)}
                      className="w-full px-5 py-4 text-left hover:bg-gray-50 transition-colors"
                    >
                      <div className="font-medium text-navy">{result.name}</div>
                      <div className="text-sm text-gray-500 mt-1">
                        {stateText}{result.country} • {result.latitude.toFixed(4)}, {result.longitude.toFixed(4)}
                      </div>
                    </button>
                  )
                })}
              </div>
            )}

            {selectedLocation && (
              <div className="mt-6">
                <div className="p-5 bg-accent/5 border border-accent/20">
                  <div className="font-semibold text-navy text-lg">{selectedLocation.name}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    {selectedLocation.lat.toFixed(4)}, {selectedLocation.lon.toFixed(4)}
                  </div>
                </div>
                <div className="mt-4">
                  <div className="px-5 py-3 bg-navy/5 border border-navy/20 text-navy font-medium text-center">
                    5-Day Forecast (120 Hours)
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="max-w-3xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 p-5 flex items-start">
              <AlertTriangle className="h-5 w-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold text-red-900">Error</div>
                <div className="text-sm text-red-700 mt-1">{error}</div>
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="max-w-3xl mx-auto text-center py-16">
            <Clock className="h-12 w-12 text-accent animate-spin mx-auto mb-4" />
            <div className="text-lg text-gray-600">Loading forecast data</div>
          </div>
        )}

        {!loading && forecastData && (
          <div className="max-w-7xl mx-auto">
            <div className="mb-12">
              <h3 className="text-3xl font-semibold text-navy mb-8">Daily Overview</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {dailyForecasts.map(({ date, points, hazardMaxRisks, overallMaxRisk }) => {
                  const dateObj = new Date(date)
                  const dayName = dateObj.toLocaleDateString("en-US", { weekday: "short" })
                  const dateStr = dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric" })
                  return (
                    <div key={date} className="bg-white border-2 border-gray-100 p-6 hover:shadow-lg transition-all">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <div className="font-semibold text-xl text-navy">{dayName}</div>
                          <div className="text-sm text-gray-600">{dateStr}</div>
                        </div>
                        <div className={`text-4xl font-bold bg-gradient-to-br ${getRiskBgColor(overallMaxRisk)} bg-clip-text text-transparent`}>
                          {overallMaxRisk}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 mt-4">
                        {Object.entries(hazardMaxRisks).map(([hazardType, maxScore]) => {
                          const IconComponent = getHazardIconComponent(hazardType)
                          return (
                            <div key={hazardType} className={`p-2 border-2 ${getRiskColor(maxScore)} bg-white`}>
                              <div className="flex items-center justify-between">
                                <div className="w-6 h-6 rounded bg-navy/5 flex items-center justify-center">
                                  <IconComponent className="h-4 w-4 text-navy-light" strokeWidth={1.5} />
                                </div>
                                <span className={`text-lg font-bold bg-gradient-to-br ${getRiskBgColor(maxScore)} bg-clip-text text-transparent`}>
                                  {maxScore}
                                </span>
                              </div>
                              <div className="text-xs font-medium text-navy mt-1">{getHazardName(hazardType)}</div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            <div>
              <h3 className="text-3xl font-semibold text-navy mb-8">Detailed Timeline</h3>
              <div className="space-y-6">
                {forecastData.forecasts.map((forecast, idx) => {
                  const time = new Date(forecast.dt_txt)
                  const timeStr = time.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })
                  const dateStr = time.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })
                  return (
                    <div key={idx} className={`bg-white border-2 ${getRiskColor(forecast.summary.highest_risk)} p-6 hover:shadow-lg transition-all`}>
                      <div className="flex items-center justify-between mb-5">
                        <div>
                          <div className="text-2xl font-semibold text-navy">{timeStr}</div>
                          <div className="text-sm text-gray-600 mt-0.5">{dateStr}</div>
                        </div>
                        <div className="text-right">
                          <div className={`text-5xl font-bold bg-gradient-to-br ${getRiskBgColor(forecast.summary.highest_risk)} bg-clip-text text-transparent`}>
                            {forecast.summary.highest_risk}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">{getRiskLabel(forecast.summary.highest_risk)}</div>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {Object.entries(forecast.hazards).map(([type, hazard]: [string, any]) => {
                          const IconComponent = getHazardIconComponent(type)
                          return (
                            <div key={type} className={`p-3 border-2 ${getRiskColor(hazard.score)} bg-white`}>
                              <div className="flex items-center justify-between mb-2">
                                <div className="w-8 h-8 rounded bg-navy/5 flex items-center justify-center">
                                  <IconComponent className="h-5 w-5 text-navy-light" strokeWidth={1.5} />
                                </div>
                                <span className={`text-2xl font-bold bg-gradient-to-br ${getRiskBgColor(hazard.score)} bg-clip-text text-transparent`}>
                                  {hazard.score}
                                </span>
                              </div>
                              <div className="font-semibold text-sm text-navy">{getHazardName(type)}</div>
                              <div className="text-xs text-gray-600 mt-0.5">{hazard.risk_level}</div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {!loading && !forecastData && !error && (
          <div className="max-w-3xl mx-auto text-center py-16">
            <Calendar className="h-16 w-16 text-gray-300 mx-auto mb-6" strokeWidth={1} />
            <h3 className="text-2xl font-semibold text-gray-700 mb-3">No Location Selected</h3>
            <p className="text-gray-500 text-lg font-light">
              Search for a location above to view forecast hazard assessments
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
