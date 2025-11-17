"use client"

import { ArrowRight, Database, Globe, Shield } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-8 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-navy text-2xl font-semibold tracking-tight">
                WIRE
              </div>
              <div className="hidden md:block text-gray-400 text-sm font-light">
                Weather-Induced Risk Exposure
              </div>
            </div>
            <nav className="flex items-center space-x-8">
              <a href="/dashboard" className="text-gray-600 hover:text-navy text-[15px] font-medium transition-colors">
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

      {/* Hero Section */}
      <section className="container mx-auto px-8 py-32">
        <div className="max-w-5xl">

          <h1 className="text-6xl font-semibold text-navy mb-8 leading-[1.1] tracking-tight max-w-4xl">
            Weather-induced risk assessment for care institutions
          </h1>

          <p className="text-xl text-gray-600 mb-12 max-w-3xl leading-relaxed font-light">
            Meteorological data processed and analysed to promote the safety of vulnerable populations.
            Eight evidence-based hazard modules provide institutional decision-makers
            with actionable risk intelligence.
          </p>

          <div className="flex items-center gap-4">
            <a
              href="/dashboard"
              className="inline-flex items-center px-8 py-4 bg-navy text-white text-base font-medium hover:bg-navy-secondary transition-all hover:shadow-lg hover:shadow-navy/20"
            >
              Access Dashboard
              <ArrowRight className="ml-2 h-5 w-5" />
            </a>
            <a
              href="/methodology"
              className="inline-flex items-center px-8 py-4 border border-gray-200 text-gray-700 text-base font-medium hover:border-gray-300 hover:bg-gray-50/50 transition-all"
            >
              View Hazard Module Methodologies
            </a>
          </div>
        </div>
      </section>

       {/* Use Cases */}
      <section className="container mx-auto px-8 py-24 border-t border-gray-100 bg-gradient-to-b from-white to-gray-50/30">
        <div className="mb-16">
          <h2 className="text-4xl font-semibold text-navy mb-4">
            Key Use Cases
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl font-light">
            {/* Comprehensive meteorological risk intelligence designed for institutions with a duty of care */}
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="group bg-white border border-gray-100 p-8 hover:border-navy-light/30 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 rounded bg-navy/5 flex items-center justify-center mb-6 group-hover:bg-navy-light/10 transition-colors">
              <Database className="h-6 w-6 text-navy-light" strokeWidth={1.5} />
            </div>
            <h3 className="text-xl font-semibold text-navy mb-3">
              Elderly Care Facilities
            </h3>
            <p className="text-gray-600 text-[15px] leading-relaxed">
              Helping staff assess risks for taking elderly residents off site and how to prepare residents for different weather scenarios (e.g., welfare check frequency, planning excursions, central heating schedules).
            </p>
          </div>

          <div className="group bg-white border border-gray-100 p-8 hover:border-navy-light/30 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 rounded bg-navy/5 flex items-center justify-center mb-6 group-hover:bg-navy-light/10 transition-colors">
              <Shield className="h-6 w-6 text-navy-light" strokeWidth={1.5} />
            </div>
            <h3 className="text-xl font-semibold text-navy mb-3">
              Schools
            </h3>
            <p className="text-gray-600 text-[15px] leading-relaxed">
              Aiding teachers in deciding whether outdoor activities are appropriate for children and when to take precations (e.g., gritting, suncream, warm clothes).
            </p>
          </div>

          <div className="group bg-white border border-gray-100 p-8 hover:border-navy-light/30 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 rounded bg-navy/5 flex items-center justify-center mb-6 group-hover:bg-navy-light/10 transition-colors">
              <Globe className="h-6 w-6 text-navy-light" strokeWidth={1.5} />
            </div>
            <h3 className="text-xl font-semibold text-navy mb-3">
              Hospitals and Emergency Departments
            </h3>
            <p className="text-gray-600 text-[15px] leading-relaxed">
              Preparing for surges in A&E visits (asthma attacks, slips and falls, heat exposure) as well as wider disruption to hospital services (e.g., ambulance delays from adverse road conditions).
            </p>
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section className="container mx-auto px-8 py-24 border-t border-gray-100 bg-gradient-to-b from-white to-gray-50/30">
        <div className="mb-16">
          <h2 className="text-4xl font-semibold text-navy mb-4">
            Capabilities
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl font-light">
            Comprehensive meteorological risk intelligence designed for institutions with a duty of care
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="group bg-white border border-gray-100 p-8 hover:border-navy-light/30 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 rounded bg-navy/5 flex items-center justify-center mb-6 group-hover:bg-navy-light/10 transition-colors">
              <Database className="h-6 w-6 text-navy-light" strokeWidth={1.5} />
            </div>
            <h3 className="text-xl font-semibold text-navy mb-3">
              Academic Foundation
            </h3>
            <p className="text-gray-600 text-[15px] leading-relaxed">
              Eight hazard modules, with analysis driven by cited academic and industry research including: NOAA Heat Index, EPA AQI, UK Met Office methodologies.
            </p>
          </div>

          <div className="group bg-white border border-gray-100 p-8 hover:border-navy-light/30 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 rounded bg-navy/5 flex items-center justify-center mb-6 group-hover:bg-navy-light/10 transition-colors">
              <Shield className="h-6 w-6 text-navy-light" strokeWidth={1.5} />
            </div>
            <h3 className="text-xl font-semibold text-navy mb-3">
              Vulnerable Population Calibration
            </h3>
            <p className="text-gray-600 text-[15px] leading-relaxed">
              Risk thresholds specifically designed for groups such as elderly residents, young children,
              and medically vulnerable individuals in institutional care.
            </p>
          </div>

          <div className="group bg-white border border-gray-100 p-8 hover:border-navy-light/30 hover:shadow-lg transition-all duration-200">
            <div className="w-12 h-12 rounded bg-navy/5 flex items-center justify-center mb-6 group-hover:bg-navy-light/10 transition-colors">
              <Globe className="h-6 w-6 text-navy-light" strokeWidth={1.5} />
            </div>
            <h3 className="text-xl font-semibold text-navy mb-3">
              Global Scope
            </h3>
            <p className="text-gray-600 text-[15px] leading-relaxed">
              120-hour global forecast capability.
              Real-time monitoring and predictive risk assessment worldwide.
            </p>
          </div>
        </div>
      </section>

      {/* Hazard Modules */}
      <section className="container mx-auto px-8 py-24 border-t border-gray-100">
        <div className="mb-16">
          <h2 className="text-4xl font-semibold text-navy mb-4">
            Monitored Hazards
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl font-light">
            Each module employs established meteorological methodologies with academic validation
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl">
          {[
            { name: "Heat Stress", methodology: "NOAA Heat Index", color: "accent" },
            { name: "Cold Exposure", methodology: "Wind Chill Index", color: "navy-light" },
            { name: "Respiratory Risk", methodology: "EPA AQI Standards", color: "accent" },
            { name: "Slip/Fall Risk", methodology: "Surface Temperature Analysis", color: "navy-light" },
            { name: "Storm Risk", methodology: "Composite Weather Assessment", color: "accent" },
            { name: "Flood Risk", methodology: "Precipitation Accumulation", color: "navy-light" },
            { name: "Dehydration Risk", methodology: "Geriatric Risk Model", color: "accent" },
            { name: "Travel Risk", methodology: "Visibility Safety Index", color: "navy-light" },
          ].map((hazard, i) => (
            <div key={i} className={`group border-l-3 ${hazard.color === 'accent' ? 'border-accent/40' : 'border-navy-light/40'} pl-5 py-3 hover:border-${hazard.color} hover:bg-${hazard.color}/5 transition-all duration-200 rounded-r`}>
              <h4 className="font-semibold text-navy text-base mb-2">
                {hazard.name}
              </h4>
              <p className="text-sm text-gray-500 font-light">
                {hazard.methodology}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Target Applications */}
      <section className="container mx-auto px-8 py-24 border-t border-gray-100 bg-gradient-to-b from-white to-navy/[0.02]">
        <div className="mb-16">
          <h2 className="text-4xl font-semibold text-navy mb-4">
            Institutional Applications
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl font-light">
            Designed for decision-makers with vulnerable population safety responsibilities
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl">
          <div className="group bg-white border border-gray-100 p-8 hover:border-accent/30 hover:shadow-lg transition-all duration-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-1.5 h-8 bg-accent rounded-full"></div>
              <h3 className="font-semibold text-navy text-lg">Care Homes & Nursing Facilities</h3>
            </div>
            <p className="text-[15px] text-gray-600 leading-relaxed">
              Manage measures to protect elderly residents from cold exposure, heat stress and fall risks.
              Advance planning for routine check-ins, facility operations and outdoor activity scheduling.
            </p>
          </div>

          <div className="group bg-white border border-gray-100 p-8 hover:border-navy-light/30 hover:shadow-lg transition-all duration-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-1.5 h-8 bg-navy-light rounded-full"></div>
              <h3 className="font-semibold text-navy text-lg">Hospitals & Medical Centers</h3>
            </div>
            <p className="text-[15px] text-gray-600 leading-relaxed">
              Patient transport safety, facility management, and operational planning.
            </p>
          </div>

          <div className="group bg-white border border-gray-100 p-8 hover:border-navy-light/30 hover:shadow-lg transition-all duration-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-1.5 h-8 bg-navy-light rounded-full"></div>
              <h3 className="font-semibold text-navy text-lg">Nurseries & Childcare</h3>
            </div>
            <p className="text-[15px] text-gray-600 leading-relaxed">
              Care for young children during outdoor activities. Data-driven
              decisions for play schedules and weather-dependent programming.
            </p>
          </div>

          <div className="group bg-white border border-gray-100 p-8 hover:border-accent/30 hover:shadow-lg transition-all duration-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-1.5 h-8 bg-accent rounded-full"></div>
              <h3 className="font-semibold text-navy text-lg">Local Government & Emergency Services</h3>
            </div>
            <p className="text-[15px] text-gray-600 leading-relaxed">
              Coordinate care facility support during adverse weather. Resource
              allocation, preventive action and mitigation planning.
            </p>
          </div>
        </div>
      </section>

      {/* Technical Details */}
      <section className="container mx-auto px-8 py-24 border-t border-gray-100 bg-gradient-to-br from-navy/[0.02] via-white to-accent/[0.02]">
        <div className="max-w-5xl">
          <h2 className="text-4xl font-semibold text-navy mb-12">
            Technical Implementation
          </h2>

          <div className="grid md:grid-cols-2 gap-12 mb-12">
            <div className="bg-white/80 backdrop-blur-sm border border-gray-100 p-6 rounded">
              <h3 className="font-semibold text-navy mb-4 text-sm uppercase tracking-wide flex items-center gap-2">
                <div className="w-1 h-4 bg-accent rounded-full"></div>
                Data Sources
              </h3>
              <ul className="space-y-3 text-[15px] text-gray-600">
                <li>• OpenWeather Current Weather API</li>
                <li>• 5-Day Forecast API (120-hour coverage)</li>
                <li>• Air Quality API (PM2.5, PM10, NO2, O3)</li>
                <li>• Geocoding API (global location search)</li>
              </ul>
            </div>

            <div className="bg-white/80 backdrop-blur-sm border border-gray-100 p-6 rounded">
              <h3 className="font-semibold text-navy mb-4 text-sm uppercase tracking-wide flex items-center gap-2">
                <div className="w-1 h-4 bg-navy-light rounded-full"></div>
                Technology Stack
              </h3>
              <ul className="space-y-3 text-[15px] text-gray-600">
                <li>• Next.js 14 frontend with TypeScript</li>
                <li>• FastAPI backend with Python 3.11</li>
                <li>• Github & Vercel for both frontend and stateless backend deployment</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 bg-white">
        <div className="container mx-auto px-8 py-10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <strong className="text-navy font-semibold text-base">WIRE</strong>
              <span className="text-gray-300">·</span>
              <span className="font-light">Weather-Induced Risk Exposure</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
