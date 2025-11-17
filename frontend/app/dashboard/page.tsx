"use client"

import { useState, useEffect } from "react"
import { Database, MapPin, AlertTriangle, RefreshCw } from "lucide-react"
import { api, AllHazardsResponse, LocationSearchResult } from "@/lib/api"
import {
  getRiskColor,
  getRiskBgColor,
  getRiskLabel,
  getHazardIconComponent,
  getHazardName,
  sortHazardsByRisk,
  formatTimestamp,
  getRelativeTime,
} from "@/lib/hazard-utils"

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<LocationSearchResult[]>([])
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number
    lon: number
    name: string
  } | null>(null)
  const [hazardData, setHazardData] = useState<AllHazardsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSearching, setIsSearching] = useState(false)

  // Search for locations
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

  // Select a location and fetch hazards
  const handleSelectLocation = async (location: LocationSearchResult) => {
    setSelectedLocation({
      lat: location.latitude,
      lon: location.longitude,
      name: `${location.name}${location.state ? `, ${location.state}` : ""}, ${location.country}`,
    })
    setSearchResults([])
    setSearchQuery("")

    // Fetch hazard data for this location
    await fetchHazards(location.latitude, location.longitude, location.name)
  }

  // Fetch hazard data
  const fetchHazards = async (lat: number, lon: number, name: string) => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getHazardsByCoordinates(lat, lon, name)
      setHazardData(data)
    } catch (err: any) {
      setError(err.message || "Failed to fetch hazard data")
      setHazardData(null)
    } finally {
      setLoading(false)
    }
  }

  // Refresh hazard data
  const handleRefresh = async () => {
    if (!selectedLocation) return
    await fetchHazards(selectedLocation.lat, selectedLocation.lon, selectedLocation.name)
  }

  // Handle enter key in search
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch()
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-8 py-5">
          <div className="flex items-center justify-between">
            <a href="/" className="flex items-center space-x-4">
              <div className="text-navy text-2xl font-semibold tracking-tight">
                WIRE
              </div>
              <div className="hidden md:block text-gray-400 text-sm font-light">
                Weather Induced Risk Exposure
              </div>
            </a>
            <nav className="flex items-center space-x-8">
              <a href="/dashboard" className="text-navy font-medium text-[15px] border-b-2 border-accent pb-1">
                Dashboard
              </a>
              <a href="/forecast" className="text-gray-600 hover:text-navy text-[15px] font-medium transition-colors">
                Forecast
              </a>
              <a href="/methodology" className="text-gray-600 hover:text-navy text-[15px] font-medium transition-colors">
                Methodology
              </a>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-8 py-12">
        {/* Location Search */}
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
                className="px-8 py-3.5 bg-navy text-white hover:bg-navy-secondary transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium text-[15px]"
              >
                {isSearching ? "Searching..." : "Search"}
              </button>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="mt-4 border border-gray-200 divide-y max-h-60 overflow-y-auto">
                {searchResults.map((result, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSelectLocation(result)}
                    className="w-full px-5 py-4 text-left hover:bg-gray-50 transition-colors"
                  >
                    <div className="font-medium text-navy">{result.name}</div>
                    <div className="text-sm text-gray-500 mt-1">
                      {result.state && `${result.state}, `}{result.country} • {result.latitude.toFixed(4)}, {result.longitude.toFixed(4)}
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Selected Location Display */}
            {selectedLocation && (
              <div className="mt-6 p-5 bg-accent/5 border border-accent/20 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-navy text-lg">{selectedLocation.name}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    {selectedLocation.lat.toFixed(4)}, {selectedLocation.lon.toFixed(4)}
                  </div>
                </div>
                <button
                  onClick={handleRefresh}
                  disabled={loading}
                  className="p-3 hover:bg-accent/10 transition-colors disabled:opacity-50"
                  title="Refresh data"
                >
                  <RefreshCw className={`h-5 w-5 text-accent ${loading ? "animate-spin" : ""}`} />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Error Message */}
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

        {/* Loading State */}
        {loading && (
          <div className="max-w-3xl mx-auto text-center py-16">
            <RefreshCw className="h-12 w-12 text-accent animate-spin mx-auto mb-4" />
            <div className="text-lg text-gray-600">Loading hazard data</div>
          </div>
        )}

        {/* Hazard Data Display */}
        {!loading && hazardData && (
          <div className="max-w-7xl mx-auto">
            {/* Weather Summary */}
            <div className="mb-12">
              <div className="bg-gradient-to-br from-navy/[0.02] via-white to-accent/[0.02] border border-gray-100 p-6">
                <div className="text-sm text-gray-600 mb-4 uppercase tracking-wide font-medium">Current Weather Conditions</div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-3xl font-semibold text-navy">
                      {hazardData.weather_data?.temperature?.toFixed(1) ?? 'N/A'}°C
                    </div>
                    <div className="text-base text-gray-600 capitalize mt-1">
                      {hazardData.weather_data?.description ?? 'Unknown'}
                    </div>
                  </div>
                  <div className="text-right text-[15px] text-gray-600 space-y-1">
                    <div>Humidity: {hazardData.weather_data?.humidity ?? 'N/A'}%</div>
                    <div>Wind Speed: {hazardData.weather_data?.wind_speed?.toFixed(1) ?? 'N/A'} m/s</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Current Hazard Assessment Section */}
            <div className="mb-8">
              <div className="flex items-baseline justify-between mb-6">
                <h2 className="text-3xl font-semibold text-navy">Current Hazard Assessment</h2>
                <div className="text-sm text-gray-500 font-light">
                  Updated {formatTimestamp(hazardData.timestamp)}
                </div>
              </div>
            </div>

            {/* Hazard Cards Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {sortHazardsByRisk(Object.values(hazardData.hazards)).map((hazard) => (
                <div
                  key={hazard.hazard_type}
                  className={`bg-white border-2 ${getRiskColor(hazard.score)} p-6 hover:shadow-lg transition-all duration-200`}
                >
                  {/* Hazard Header */}
                  <div className="flex items-start justify-between mb-5">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded bg-navy/5 flex items-center justify-center">
                        {(() => {
                          const IconComponent = getHazardIconComponent(hazard.hazard_type)
                          return <IconComponent className="h-7 w-7 text-navy-light" strokeWidth={1.5} />
                        })()}
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg text-navy">{hazard.name}</h3>
                        <div className="text-sm text-gray-500 mt-0.5">{hazard.risk_level}</div>
                      </div>
                    </div>
                    <div className={`text-3xl font-bold bg-gradient-to-br ${getRiskBgColor(hazard.score)} bg-clip-text text-transparent`}>
                      {hazard.score}
                    </div>
                  </div>

                  {/* Key Factors */}
                  <div className="mb-5">
                    <div className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">Key Factors</div>
                    <div className="text-[15px] space-y-2">
                      {Object.entries(hazard.factors).slice(0, 3).map(([key, value]) => (
                        <div key={key} className="flex justify-between items-center">
                          <span className="text-gray-600 capitalize">{key.replace(/_/g, " ")}</span>
                          <span className="font-semibold text-navy">
                            {typeof value === "number" ? value.toFixed(1) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="border-t border-gray-100 pt-4">
                    <div className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">Recommendations</div>
                    <ul className="text-[15px] space-y-2 text-gray-700">
                      {hazard.recommendations.slice(0, 2).map((rec, idx) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-accent mr-2 flex-shrink-0">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !hazardData && !error && (
          <div className="max-w-3xl mx-auto text-center py-16">
            <Database className="h-16 w-16 text-gray-300 mx-auto mb-6" strokeWidth={1} />
            <h3 className="text-2xl font-semibold text-gray-700 mb-3">No Location Selected</h3>
            <p className="text-gray-500 text-lg font-light">
              Search for a location above to view current hazard assessments
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
