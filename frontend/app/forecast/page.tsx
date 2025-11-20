"use client"

import { useState, useEffect } from "react"
import { Calendar, MapPin, AlertTriangle, Clock, Download } from "lucide-react"
import { api, ForecastResponse } from "@/lib/api"
import {
  getRiskColor,
  getRiskBgColor,
  getRiskLabel,
  getHazardIconComponent,
  getHazardName,
} from "@/lib/hazard-utils"

export default function ForecastPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number
    lon: number
    name: string
  } | null>(null)
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null)
  const [forecastHours, setForecastHours] = useState<120>(120)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [hiddenHazards, setHiddenHazards] = useState<Set<string>>(new Set())

  const toggleHazard = (hazardType: string) => {
    setHiddenHazards(prev => {
      const newSet = new Set(prev)
      if (newSet.has(hazardType)) {
        newSet.delete(hazardType)
      } else {
        newSet.add(hazardType)
      }
      return newSet
    })
  }

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
      const data = await api.getHazardForecast(lat, lon, name, forecastHours)
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

  const handlePrint = () => {
    window.print()
  }

  const groupByDay = () => {
    if (!forecastData) return []
    const days = new Map<string, any[]>()
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
            {/* Forecast Controls */}
            <div className="mb-8 pb-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <label className="text-sm font-medium text-gray-700">Forecast Range:</label>
                  <select
                    value={forecastHours}
                    onChange={(e) => setForecastHours(Number(e.target.value) as 120)}
                    className="px-4 py-2 border border-gray-200 focus:ring-2 focus:ring-accent/20 focus:border-accent outline-none text-sm transition-all"
                  >
                    <option value={24}>24 Hours (1 Day)</option>
                    <option value={72}>72 Hours (3 Days)</option>
                    <option value={120}>120 Hours (5 Days)</option>
                  </select>
                </div>
                <button
                  onClick={handlePrint}
                  className="inline-flex items-center gap-2 px-6 py-2 bg-navy text-white hover:bg-navy-secondary transition-all font-medium text-sm"
                >
                  <Download className="h-4 w-4" />
                  Print / Download
                </button>
              </div>
            </div>

            {/* Daily Peak Hazards */}
            <div className="mb-12">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-3xl font-semibold text-navy">Daily Peak Hazards</h3>
                <div className="text-sm text-gray-500 italic">Hover over any day to see all hazards</div>
              </div>
              <div className="flex gap-3 w-full">
                {dailyForecasts.map(({ date, points, hazardMaxRisks, overallMaxRisk }) => {
                  const dateObj = new Date(date)
                  const dayName = dateObj.toLocaleDateString("en-US", { weekday: "short" })
                  const dateStr = dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric" })

                  // Sort all hazards by risk score
                  const allHazards = Object.entries(hazardMaxRisks)
                    .sort(([, a], [, b]) => (b as number) - (a as number))

                  const topHazards = allHazards.slice(0, 3)

                  return (
                    <div key={date} className="group relative flex-1">
                      <div className={`bg-white border-2 ${getRiskColor(overallMaxRisk)} p-3 cursor-pointer transition-all hover:shadow-lg h-full`}>
                        <div className="text-center mb-2">
                          <div className="font-bold text-sm text-navy mb-1">{dayName}</div>
                          <div className="text-xs text-gray-600 mb-1.5">{dateStr}</div>
                          <div className={`text-3xl font-bold bg-gradient-to-br ${getRiskBgColor(overallMaxRisk)} bg-clip-text text-transparent mb-2`}>
                            {overallMaxRisk}
                          </div>
                        </div>

                        {/* Top 3 hazards preview */}
                        <div className="space-y-2 border-t border-gray-200 pt-2.5">
                          {topHazards.map(([hazardType, maxScore]) => {
                            const IconComponent = getHazardIconComponent(hazardType)
                            return (
                              <div key={hazardType} className="flex items-center gap-2">
                                <IconComponent className={`h-3.5 w-3.5 flex-shrink-0 ${
                                  maxScore >= 4 ? 'text-red-600' :
                                  maxScore === 3 ? 'text-amber-600' :
                                  maxScore === 2 ? 'text-yellow-600' :
                                  'text-green-600'
                                }`} strokeWidth={1.5} />
                                <span className="text-[11px] font-medium text-navy truncate flex-1 leading-tight">
                                  {getHazardName(hazardType)}
                                </span>
                                <span className={`text-sm font-bold flex-shrink-0 ${
                                  maxScore >= 4 ? 'text-red-600' :
                                  maxScore === 3 ? 'text-amber-600' :
                                  maxScore === 2 ? 'text-yellow-600' :
                                  'text-green-600'
                                }`}>
                                  {maxScore}
                                </span>
                              </div>
                            )
                          })}
                        </div>
                      </div>

                      {/* Expandable detail panel - hover to see all 8 */}
                      <div className="absolute top-full left-0 mt-2 w-64 bg-white border-2 border-gray-200 shadow-xl rounded-lg p-4 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                        <div className="font-bold text-navy mb-3 pb-2 border-b border-gray-200">
                          {dayName}, {dateStr}
                        </div>
                        <div className="space-y-2">
                          {allHazards.map(([hazardType, maxScore]) => {
                            const IconComponent = getHazardIconComponent(hazardType)
                            return (
                              <div key={hazardType} className="flex items-center gap-2">
                                <div className={`w-7 h-7 rounded flex items-center justify-center ${
                                  maxScore >= 4 ? 'bg-red-100' :
                                  maxScore === 3 ? 'bg-amber-100' :
                                  maxScore === 2 ? 'bg-yellow-100' :
                                  'bg-green-100'
                                }`}>
                                  <IconComponent className={`h-4 w-4 ${
                                    maxScore >= 4 ? 'text-red-600' :
                                    maxScore === 3 ? 'text-amber-600' :
                                    maxScore === 2 ? 'text-yellow-600' :
                                    'text-green-600'
                                  }`} strokeWidth={1.5} />
                                </div>
                                <span className="text-xs font-medium text-navy flex-1">{getHazardName(hazardType)}</span>
                                <span className={`text-base font-bold ${
                                  maxScore >= 4 ? 'text-red-600' :
                                  maxScore === 3 ? 'text-amber-600' :
                                  maxScore === 2 ? 'text-yellow-600' :
                                  'text-green-600'
                                }`}>
                                  {maxScore}
                                </span>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Time Series Chart */}
            <div className="mb-12">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-3xl font-semibold text-navy">Hazard Risk Timeline</h3>
                <div className="text-sm text-gray-500 italic">Click legend below to show/hide hazards</div>
              </div>
              <div className="bg-white border-2 border-gray-100 p-6">
                <div className="relative" style={{ height: '600px' }}>
                  <svg width="100%" height="100%" viewBox="0 0 1200 600" preserveAspectRatio="xMidYMid meet">
                    {/* Y-axis grid lines and labels */}
                    {[0, 1, 2, 3, 4, 5].map((level) => {
                      const y = 540 - (level * 100)
                      return (
                        <g key={level}>
                          <line x1="80" y1={y} x2="1160" y2={y} stroke="#e5e7eb" strokeWidth="1" strokeDasharray={level === 0 ? "0" : "4 2"} />
                          <text x="60" y={y + 5} fontSize="14" fill="#6b7280" fontWeight="600" textAnchor="end">{level}</text>
                        </g>
                      )
                    })}

                    {/* X-axis - time labels */}
                    {forecastData.forecasts.map((forecast, idx) => {
                      if (idx % 3 !== 0) return null // Show every 3rd label
                      const x = 80 + (idx / (forecastData.forecasts.length - 1)) * 1080
                      const time = new Date(forecast.dt_txt)
                      const label = time.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "numeric" })
                      return (
                        <text key={idx} x={x} y="570" fontSize="12" fill="#6b7280" textAnchor="middle">
                          {label}
                        </text>
                      )
                    })}

                    {/* Plot lines for each hazard with offset to reduce overlap */}
                    {Object.keys(forecastData.forecasts[0]?.hazards || {}).map((hazardType, hIdx) => {
                      const colors = [
                        "#ef4444", "#f97316", "#f59e0b", "#84cc16",
                        "#10b981", "#06b6d4", "#3b82f6", "#8b5cf6"
                      ]
                      const color = colors[hIdx % colors.length]
                      const offset = (hIdx - 3.5) * 1.5 // Slight horizontal offset to separate overlapping lines
                      const isHidden = hiddenHazards.has(hazardType)

                      return (
                        <g key={hazardType} opacity={isHidden ? 0.15 : 1}>
                          {/* Line */}
                          <path
                            d={forecastData.forecasts.map((forecast, idx) => {
                              const x = 80 + (idx / (forecastData.forecasts.length - 1)) * 1080 + offset
                              const score = forecast.hazards[hazardType]?.score || 0
                              const y = 540 - (score * 100)
                              return `${idx === 0 ? 'M' : 'L'} ${x} ${y}`
                            }).join(' ')}
                            fill="none"
                            stroke={color}
                            strokeWidth="3"
                            strokeLinejoin="round"
                            strokeLinecap="round"
                            opacity="0.85"
                          />
                          {/* Data points with hover effect */}
                          {forecastData.forecasts.map((forecast, idx) => {
                            const x = 80 + (idx / (forecastData.forecasts.length - 1)) * 1080 + offset
                            const score = forecast.hazards[hazardType]?.score || 0
                            const y = 540 - (score * 100)
                            return (
                              <g key={idx}>
                                <circle
                                  cx={x}
                                  cy={y}
                                  r="4"
                                  fill="white"
                                  stroke={color}
                                  strokeWidth="2.5"
                                  opacity="0.95"
                                />
                              </g>
                            )
                          })}
                        </g>
                      )
                    })}

                    {/* Y-axis label */}
                    <text x="25" y="300" fontSize="16" fill="#1f2937" fontWeight="600" textAnchor="middle" transform="rotate(-90, 25, 300)">
                      Risk Score (1-5)
                    </text>
                  </svg>
                </div>

                {/* Legend */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="text-xs text-gray-500">Legend</div>
                    <div className="text-xs text-gray-400">• Click any hazard to toggle visibility</div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.keys(forecastData.forecasts[0]?.hazards || {}).map((hazardType, hIdx) => {
                      const colors = [
                        "#ef4444", "#f97316", "#f59e0b", "#84cc16",
                        "#10b981", "#06b6d4", "#3b82f6", "#8b5cf6"
                      ]
                      const color = colors[hIdx % colors.length]
                      const IconComponent = getHazardIconComponent(hazardType)
                      const isHidden = hiddenHazards.has(hazardType)

                      return (
                        <button
                          key={hazardType}
                          onClick={() => toggleHazard(hazardType)}
                          className={`flex items-center gap-2 p-2 rounded hover:bg-gray-50 transition-all ${
                            isHidden ? 'opacity-40' : ''
                          }`}
                        >
                          <div
                            className="w-3 h-3 rounded-full border-2 border-white"
                            style={{
                              backgroundColor: isHidden ? '#d1d5db' : color,
                              boxShadow: '0 0 0 2px ' + (isHidden ? '#d1d5db' : color)
                            }}
                          ></div>
                          <IconComponent className={`h-4 w-4 ${isHidden ? 'text-gray-400' : 'text-gray-600'}`} strokeWidth={1.5} />
                          <span className={`text-sm font-medium ${isHidden ? 'text-gray-400 line-through' : 'text-navy'}`}>
                            {getHazardName(hazardType)}
                          </span>
                        </button>
                      )
                    })}
                  </div>
                </div>
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
