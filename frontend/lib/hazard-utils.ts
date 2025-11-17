/**
 * Hazard Utilities
 *
 * Helper functions for working with hazard data
 */

import {
  Thermometer,
  Snowflake,
  Wind,
  AlertTriangle,
  CloudLightning,
  Droplets,
  Droplet,
  Car,
  LucideIcon
} from 'lucide-react'

/**
 * Get color class for risk level (WIRE design system)
 */
export function getRiskColor(score: number): string {
  if (score >= 5) return 'border-risk-5/30'
  if (score >= 4) return 'border-risk-4/30'
  if (score >= 3) return 'border-risk-3/30'
  if (score >= 2) return 'border-risk-2/30'
  return 'border-risk-1/30'
}

/**
 * Get text color for risk level (WIRE design system)
 */
export function getRiskTextColor(score: number): string {
  if (score >= 5) return 'text-risk-5'
  if (score >= 4) return 'text-risk-4'
  if (score >= 3) return 'text-risk-3'
  if (score >= 2) return 'text-risk-2'
  return 'text-risk-1'
}

/**
 * Get background gradient for risk level (WIRE design system)
 */
export function getRiskBgColor(score: number): string {
  if (score >= 5) return 'from-risk-5 to-risk-4'
  if (score >= 4) return 'from-risk-4 to-risk-3'
  if (score >= 3) return 'from-risk-3 to-risk-2'
  if (score >= 2) return 'from-risk-2 to-risk-1'
  return 'from-risk-1 to-green-400'
}

/**
 * Get risk level label
 */
export function getRiskLabel(score: number): string {
  if (score >= 5) return 'Extreme'
  if (score >= 4) return 'Very High'
  if (score >= 3) return 'High'
  if (score >= 2) return 'Moderate'
  return 'Low'
}

/**
 * Get Lucide icon component for hazard type
 */
export function getHazardIconComponent(hazardType: string): LucideIcon {
  const icons: Record<string, LucideIcon> = {
    heat_stress: Thermometer,
    cold_exposure: Snowflake,
    respiratory: Wind,
    slip_fall: AlertTriangle,
    storm: CloudLightning,
    flood: Droplets,
    dehydration: Droplet,
    travel: Car,
  }
  return icons[hazardType] || AlertTriangle
}

/**
 * Get icon for hazard type (legacy - returns emoji-like representation)
 * @deprecated Use getHazardIconComponent() for React components
 */
export function getHazardIcon(hazardType: string): string {
  // Return simple text representation for non-React contexts
  const icons: Record<string, string> = {
    heat_stress: '🌡',
    cold_exposure: '❄',
    respiratory: '💨',
    slip_fall: '⚠',
    storm: '⚡',
    flood: '💧',
    dehydration: '💧',
    travel: '🚗',
  }
  return icons[hazardType] || '⚠'
}

/**
 * Get display name for hazard type
 */
export function getHazardName(hazardType: string): string {
  const names: Record<string, string> = {
    heat_stress: 'Heat Stress',
    cold_exposure: 'Cold Exposure',
    respiratory: 'Respiratory Risk',
    slip_fall: 'Slip/Fall Risk',
    storm: 'Storm Risk',
    flood: 'Flood Risk',
    dehydration: 'Dehydration Risk',
    travel: 'Travel Risk',
  }
  return names[hazardType] || hazardType
}

/**
 * Sort hazards by risk score (highest first)
 */
export function sortHazardsByRisk<T extends { score: number }>(hazards: T[]): T[] {
  return [...hazards].sort((a, b) => b.score - a.score)
}

/**
 * Format timestamp to readable date
 */
export function formatTimestamp(timestamp: string | number): string {
  // Handle Unix timestamp (seconds) or ISO string
  const date = typeof timestamp === 'number'
    ? new Date(timestamp * 1000)  // Convert Unix seconds to milliseconds
    : new Date(timestamp)

  return date.toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Get relative time (e.g., "2 hours ago")
 */
export function getRelativeTime(timestamp: string | number): string {
  // Handle Unix timestamp (seconds) or ISO string
  const date = typeof timestamp === 'number'
    ? new Date(timestamp * 1000)  // Convert Unix seconds to milliseconds
    : new Date(timestamp)

  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
}
