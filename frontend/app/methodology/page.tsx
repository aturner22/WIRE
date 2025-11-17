"use client"

import { useState, useEffect } from "react"
import { Database, Book, ExternalLink, ChevronDown, ChevronUp } from "lucide-react"
import { api, Methodology } from "@/lib/api"
import { getHazardIconComponent } from "@/lib/hazard-utils"

export default function MethodologyPage() {
  const [methodologies, setMethodologies] = useState<Methodology[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetchMethodologies()
  }, [])

  const fetchMethodologies = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getMethodologies()
      setMethodologies(data)
    } catch (err: any) {
      setError(err.message || "Failed to load methodologies")
    } finally {
      setLoading(false)
    }
  }

  const toggleSection = (hazardType: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(hazardType)) {
      newExpanded.delete(hazardType)
    } else {
      newExpanded.add(hazardType)
    }
    setExpandedSections(newExpanded)
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
              <a href="/dashboard" className="text-gray-600 hover:text-navy text-[15px] font-medium transition-colors">
                Dashboard
              </a>
              <a href="/forecast" className="text-gray-600 hover:text-navy text-[15px] font-medium transition-colors">
                Forecast
              </a>
              <a href="/methodology" className="text-navy font-medium text-[15px] border-b-2 border-accent pb-1">
                Methodology
              </a>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-8 py-16">
        {/* Hero Section */}
        <div className="max-w-4xl mx-auto mb-16 text-center">
          <div className="inline-flex items-center space-x-3 bg-accent/10 text-accent px-5 py-2.5 rounded mb-8 border border-accent/20">
            <Book className="h-4 w-4" strokeWidth={2} />
            <span className="text-sm font-medium">Academic Research & Methodologies</span>
          </div>

          <h2 className="text-6xl font-semibold text-navy mb-6 leading-tight">
            Hazard Assessment Methodology
          </h2>

          <p className="text-xl text-gray-600 max-w-2xl mx-auto font-light leading-relaxed">
            The hazard calculations used in the WIRE dashboard are drawn from cited academic research
            and established meteorological standards.
          </p>
          
          {/* Vulnerable Populations Note */}
          <div className="mt-12 max-w-3xl mx-auto">
            <div className="bg-gradient-to-br from-navy/5 via-white to-accent/5 border border-navy/10 p-8 hover:shadow-lg transition-all duration-200">
              <div className="flex items-start space-x-4">
                <div>
                  <div className="font-semibold text-navy text-xl mb-3">
                    Calibrated for Vulnerable Populations
                  </div>
                  <div className="text-base text-gray-700 leading-relaxed">
                    Risk thresholds have been adjusted to protect groups such as the elderly,
                    young children, and those with medical vulnerabilities and in care. The provided assessments are more conservative than the standards applicable to the general population to ensure maximum safety.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        

        {/* Loading State */}
        {loading && (
          <div className="max-w-4xl mx-auto text-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
            <div className="text-lg text-gray-600">Loading methodologies</div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="max-w-4xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 p-5">
              <div className="font-semibold text-red-900">Error</div>
              <div className="text-sm text-red-700 mt-1">{error}</div>
            </div>
          </div>
        )}

        {/* Methodologies List */}
        {!loading && !error && methodologies.length > 0 && (
          <div className="max-w-5xl mx-auto space-y-6">
            {methodologies.map((methodology) => {
              const isExpanded = expandedSections.has(methodology.hazard_type)

              return (
                <div
                  key={methodology.hazard_type}
                  className="bg-white border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow"
                >
                  {/* Header */}
                  <button
                    onClick={() => toggleSection(methodology.hazard_type)}
                    className="w-full px-8 py-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 rounded bg-navy/5 flex items-center justify-center">
                        {(() => {
                          const IconComponent = getHazardIconComponent(methodology.hazard_type)
                          return <IconComponent className="h-7 w-7 text-navy-light" strokeWidth={1.5} />
                        })()}
                      </div>
                      <div className="text-left">
                        <h3 className="text-xl font-semibold text-navy">
                          {methodology.name}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1.5 font-light">
                          {methodology.description}
                        </p>
                      </div>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="h-5 w-5 text-gray-400 flex-shrink-0" />
                    ) : (
                      <ChevronDown className="h-5 w-5 text-gray-400 flex-shrink-0" />
                    )}
                  </button>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="px-8 pb-8 border-t border-gray-100 bg-gradient-to-b from-white to-gray-50/30">
                      <div className="mt-8 space-y-8">
                        {/* Citation */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
                            Citation
                          </h4>
                          <div className="bg-accent/5 border border-accent/20 p-6">
                            <div className="font-semibold text-navy text-lg mb-3">
                              {methodology.citation.title}
                            </div>
                            <div className="text-[15px] text-gray-700 space-y-2">
                              {methodology.citation.authors && (
                                <div>
                                  <span className="font-medium">Authors:</span> {methodology.citation.authors}
                                </div>
                              )}
                              {methodology.citation.year && (
                                <div>
                                  <span className="font-medium">Year:</span> {methodology.citation.year}
                                </div>
                              )}
                              {methodology.citation.journal && (
                                <div>
                                  <span className="font-medium">Journal:</span> {methodology.citation.journal}
                                </div>
                              )}
                              {methodology.citation.publication && (
                                <div>
                                  <span className="font-medium">Publication:</span> {methodology.citation.publication}
                                </div>
                              )}
                              {methodology.citation.doi && (
                                <div className="flex items-center space-x-2 mt-3">
                                  <span className="font-medium">DOI:</span>
                                  <a
                                    href={`https://doi.org/${methodology.citation.doi}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-accent hover:underline flex items-center"
                                  >
                                    {methodology.citation.doi}
                                    <ExternalLink className="h-3 w-3 ml-1" />
                                  </a>
                                </div>
                              )}
                              {methodology.citation.url && (
                                <div className="flex items-center space-x-2 mt-3">
                                  <span className="font-medium">URL:</span>
                                  <a
                                    href={methodology.citation.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-accent hover:underline flex items-center break-all"
                                  >
                                    View Source
                                    <ExternalLink className="h-3 w-3 ml-1 flex-shrink-0" />
                                  </a>
                                </div>
                              )}
                              {methodology.citation.additional && (
                                <div className="mt-3">
                                  <span className="font-medium">Additional Sources:</span>
                                  <div className="text-gray-600 mt-1">{methodology.citation.additional}</div>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Risk Scale */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
                            Risk Scale (1-5)
                          </h4>
                          <div className="grid grid-cols-5 gap-3">
                            {[
                              { level: 1, label: "Low", color: "bg-risk-1/10 text-risk-1 border-risk-1/30" },
                              { level: 2, label: "Moderate", color: "bg-risk-2/10 text-risk-2 border-risk-2/30" },
                              { level: 3, label: "High", color: "bg-risk-3/10 text-risk-3 border-risk-3/30" },
                              { level: 4, label: "Very High", color: "bg-risk-4/10 text-risk-4 border-risk-4/30" },
                              { level: 5, label: "Extreme", color: "bg-risk-5/10 text-risk-5 border-risk-5/30" },
                            ].map((risk) => (
                              <div
                                key={risk.level}
                                className={`${risk.color} border-2 p-4 text-center`}
                              >
                                <div className="text-3xl font-bold">{risk.level}</div>
                                <div className="text-xs font-medium mt-2">{risk.label}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* Footer CTA */}
        <div className="max-w-5xl mx-auto mt-16 text-center">
          <div className="bg-gradient-to-br from-navy via-navy-secondary to-accent p-12 text-white">
            <h3 className="text-3xl font-semibold mb-4">Ready to Use WIRE?</h3>
            <p className="text-white/80 mb-8 max-w-2xl mx-auto text-lg font-light">
              Start monitoring weather hazards for your care facility with evidence-based assessments.
            </p>
            <a
              href="/dashboard"
              className="inline-flex items-center px-8 py-4 bg-white text-navy hover:bg-gray-50 transition-colors font-medium text-base"
            >
              Access Dashboard
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
