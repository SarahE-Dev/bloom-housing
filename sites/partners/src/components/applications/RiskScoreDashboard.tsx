"use client"

import React, { useState, useMemo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart,
} from 'recharts'
import { useApplicationsData } from "../../lib/hooks"
import { useRouter } from "next/router"
import { ApplicationOrderByKeys, OrderByEnum } from "@bloom-housing/shared-helpers/src/types/backend-swagger"
import { TrendingUp, Users, AlertTriangle, Filter, Search, ChevronDown, DollarSign, ChevronLeft, ChevronRight, Home, Calendar, Award, Activity, BarChart3, PieChart as PieChartIcon } from "lucide-react"

const RISK_COLORS = {
  low: '#059669',    // Emerald-600 - brighter green
  medium: '#D97706', // Amber-600 - brighter orange
  high: '#DC2626',   // Red-600 - brighter red
}

const CHART_COLORS = ['#3B82F6', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444']

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg animate-fadeIn">
        <p className="font-semibold text-gray-900">{`${label}`}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {`${entry.dataKey}: ${entry.value}`}
          </p>
        ))}
      </div>
    )
  }
  return null
}

const PieTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    const total = data.total || payload[0].payload.value
    const percentage = total ? ((data.value / total) * 100).toFixed(1) : '0'
    return (
      <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
        <p className="font-medium text-gray-900">{`${data.name}: ${data.value}`}</p>
        <p className="text-sm text-gray-600">{`${percentage}%`}</p>
      </div>
    )
  }
  return null
}

const AnimatedCard = ({ children, className = "", delay = 0 }: { children: React.ReactNode, className?: string, delay?: number }) => (
  <div 
    className={`bg-white rounded-xl shadow-lg border border-gray-100 p-6 transform transition-all duration-700 hover:shadow-xl hover:-translate-y-1 ${className}`}
    style={{ animationDelay: `${delay}ms` }}
  >
    {children}
  </div>
)

const StatCard = ({ title, value, subtitle, color = "blue", delay = 0, icon }: { 
  title: string, 
  value: string | number, 
  subtitle?: string, 
  color?: string,
  delay?: number,
  icon?: React.ReactNode
}) => (
  <AnimatedCard delay={delay} className="text-center animate-slideInUp">
    <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full bg-${color}-100 mb-4`}>
      {icon || <div className={`w-6 h-6 rounded-full bg-${color}-500`}></div>}
    </div>
    <h3 className="text-2xl font-bold text-gray-900 mb-1">{value}</h3>
    <p className="text-sm font-medium text-gray-700 uppercase tracking-wide">{title}</p>
    {subtitle && <p className="text-xs text-gray-700 mt-1">{subtitle}</p>}
  </AnimatedCard>
)

const RiskScoreDashboard = () => {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState("overview")
  const [selectedListing, setSelectedListing] = useState<string>("all")
  const [selectedState, setSelectedState] = useState<string>("all")
  const [searchTerm, setSearchTerm] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [sortField, setSortField] = useState("riskScore")
  const [sortDirection, setSortDirection] = useState("desc")
  const [showTabDropdown, setShowTabDropdown] = useState(false)
  const itemsPerPage = 20

  // Fetch applications with proper parameters
  const { applications, appsMeta, appsLoading, appsError } = useApplicationsData(
    1, // page
    "", // no search filter
    1000, // large limit to get all applications
    undefined, // no listing ID filter to get all applications
    ApplicationOrderByKeys.submissionDate, // order by submission date
    OrderByEnum.desc // most recent first
  )

  // Extract unique values for filters
  const filterOptions = useMemo(() => {
    if (!applications?.length) {
      return { listings: [], states: [] }
    }

    const listings = new Set<string>()
    const states = new Set<string>()

    console.log('=== FILTER OPTIONS DEBUG ===')
    console.log('Total applications:', applications.length)
    
    // Track missing data for debugging
    let missingListingCount = 0
    let missingStateCount = 0
    
    applications.forEach((app: any, index: number) => {
      // Add listing name if available
      if (app.listings?.name) {
        listings.add(app.listings.name)
      } else {
        missingListingCount++
      }
      
      // Add state if available
      if (app.applicant?.applicantAddress?.state) {
        states.add(app.applicant.applicantAddress.state)
      } else {
        missingStateCount++
      }
      
      // Log detailed info for first few applications
      if (index < 3) {
        console.log(`App ${index}:`, {
          id: app.id,
          confirmationCode: app.confirmationCode,
          listingName: app.listings?.name || 'MISSING',
          state: app.applicant?.applicantAddress?.state || 'MISSING',
          listingId: app.listings?.id,
        })
      }
    })

    console.log('Missing data counts:', {
      missingListings: missingListingCount,
      missingStates: missingStateCount
    })

    console.log('Filter options found:', {
      listings: Array.from(listings),
      states: Array.from(states)
    })

    return {
      listings: Array.from(listings).sort(),
      states: Array.from(states).sort()
    }
  }, [applications])

  // Filter applications based on selected filters AND only include those with risk data
  const filteredApplications = useMemo(() => {
    if (!applications?.length) return []

    return applications.filter((app: any) => {
      // First check if application has risk data
      const risk = app.risk || {
        riskProbability: app.riskProbability,
        riskPrediction: app.riskPrediction,
      }
      
      const hasRiskData = risk?.riskProbability !== undefined && risk?.riskProbability !== null
      
      if (!hasRiskData) return false // Exclude applications without risk data
      
      // Check if listing matches filter
      const matchesListing = selectedListing === "all" || 
        (app.listings?.name && app.listings.name === selectedListing)
      
      // Check if state matches filter
      const matchesState = selectedState === "all" || 
        (app.applicant?.applicantAddress?.state && app.applicant.applicantAddress.state === selectedState)
      
      // Check if search term matches
      const matchesSearch = !searchTerm || 
        `${app.applicant?.firstName || ''} ${app.applicant?.lastName || ''}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
        app.confirmationCode?.toLowerCase().includes(searchTerm.toLowerCase())

      return matchesListing && matchesState && matchesSearch
    })
  }, [applications, selectedListing, selectedState, searchTerm])

  // Process risk data for analytics
  const riskAnalytics = useMemo(() => {
    console.log('Computing risk analytics...')
    
    let lowRisk = 0, mediumRisk = 0, highRisk = 0
    let totalIncome = 0, incomeCount = 0
    let veteranCount = 0, disabledCount = 0, benefitsCount = 0
    const ageGroups = { '18-30': 0, '31-50': 0, '51-65': 0, '65+': 0 }
    const householdSizes = { '1': 0, '2': 0, '3': 0, '4': 0, '5+': 0 }
    const incomeRanges = { 
      '0-25k': 0, 
      '25k-50k': 0, 
      '50k-75k': 0, 
      '75k-100k': 0, 
      '100k+': 0 
    }

    // Risk factor analysis
    const riskFactors = {
      veteran: { low: 0, medium: 0, high: 0 },
      disabled: { low: 0, medium: 0, high: 0 },
      benefits: { low: 0, medium: 0, high: 0 },
      lowIncome: { low: 0, medium: 0, high: 0 },
      largeHousehold: { low: 0, medium: 0, high: 0 },
      youngAge: { low: 0, medium: 0, high: 0 },
      oldAge: { low: 0, medium: 0, high: 0 }
    }

    filteredApplications.forEach((app: any) => {
      // Handle both nested risk object and individual fields for backward compatibility
      const risk = app.risk || {
        riskProbability: app.riskProbability,
        riskPrediction: app.riskPrediction,
        veteran: app.veteran,
        income: app.income,
        disabled: app.disabled,
        age: app.age,
        benefits: app.benefits,
        numPeople: app.numPeople,
      }

      // Determine risk level
      let riskLevel = 'low'
      if (risk?.riskProbability !== undefined && risk?.riskProbability !== null) {
        if (risk.riskProbability < 0.4) {
          lowRisk++
          riskLevel = 'low'
        } else if (risk.riskProbability < 0.7) {
          mediumRisk++
          riskLevel = 'medium'
        } else {
          highRisk++
          riskLevel = 'high'
        }
      } else if (risk?.riskPrediction !== undefined) {
        // Fallback to boolean prediction
        if (risk.riskPrediction) {
          highRisk++
          riskLevel = 'high'
        } else {
          lowRisk++
          riskLevel = 'low'
        }
      }

      // Demographics
      if (risk?.veteran) {
        veteranCount++
        riskFactors.veteran[riskLevel as keyof typeof riskFactors.veteran]++
      }
      if (risk?.disabled) {
        disabledCount++
        riskFactors.disabled[riskLevel as keyof typeof riskFactors.disabled]++
      }
      if (risk?.benefits) {
        benefitsCount++
        riskFactors.benefits[riskLevel as keyof typeof riskFactors.benefits]++
      }

      // Risk factor analysis
      if (risk?.income && risk.income < 30000) {
        riskFactors.lowIncome[riskLevel as keyof typeof riskFactors.lowIncome]++
      }
      if (risk?.numPeople && risk.numPeople >= 5) {
        riskFactors.largeHousehold[riskLevel as keyof typeof riskFactors.largeHousehold]++
      }
      if (risk?.age && risk.age <= 25) {
        riskFactors.youngAge[riskLevel as keyof typeof riskFactors.youngAge]++
      }
      if (risk?.age && risk.age >= 65) {
        riskFactors.oldAge[riskLevel as keyof typeof riskFactors.oldAge]++
      }

      // Income analysis (cap at 100k for better distribution)
      if (risk?.income && risk.income > 0) {
        const cappedIncome = Math.min(risk.income, 100000)
        totalIncome += cappedIncome
        incomeCount++

        if (cappedIncome <= 25000) incomeRanges['0-25k']++
        else if (cappedIncome <= 50000) incomeRanges['25k-50k']++
        else if (cappedIncome <= 75000) incomeRanges['50k-75k']++
        else if (cappedIncome <= 100000) incomeRanges['75k-100k']++
        else incomeRanges['100k+']++
      }

      // Age groups
      if (risk?.age) {
        if (risk.age <= 30) ageGroups['18-30']++
        else if (risk.age <= 50) ageGroups['31-50']++
        else if (risk.age <= 65) ageGroups['51-65']++
        else ageGroups['65+']++
      }

      // Household sizes
      const size = risk?.numPeople || app.householdSize || 1
      if (size <= 4) householdSizes[size.toString()]++
      else householdSizes['5+']++
    })

    const totalWithRisk = lowRisk + mediumRisk + highRisk
    const avgIncome = incomeCount > 0 ? Math.round(totalIncome / incomeCount) : 0

    return {
      riskDistribution: [
        { name: 'Low Risk', value: lowRisk, color: RISK_COLORS.low, total: totalWithRisk },
        { name: 'Medium Risk', value: mediumRisk, color: RISK_COLORS.medium, total: totalWithRisk },
        { name: 'High Risk', value: highRisk, color: RISK_COLORS.high, total: totalWithRisk },
      ],
      demographics: {
        veteran: veteranCount,
        disabled: disabledCount,
        benefits: benefitsCount,
        avgIncome,
        totalWithRisk,
      },
      ageDistribution: Object.entries(ageGroups).map(([range, count]) => ({
        age: range,
        count,
      })),
      householdDistribution: Object.entries(householdSizes).map(([size, count]) => ({
        size: size === '5+' ? '5+' : `${size} person${size === '1' ? '' : 's'}`,
        count,
      })),
      incomeDistribution: Object.entries(incomeRanges).map(([range, count]) => ({
        range,
        count,
      })),
      riskFactors,
    }
  }, [filteredApplications])

  // Process individual applications for table view
  const processedApplications = useMemo(() => {
    const processed = filteredApplications
      .map((app: any) => {
        const risk = app.risk || {
          riskProbability: app.riskProbability,
          riskPrediction: app.riskPrediction,
          veteran: app.veteran,
          income: app.income,
          disabled: app.disabled,
          age: app.age,
          benefits: app.benefits,
          numPeople: app.numPeople,
        }

        const riskLevel = risk?.riskProbability ? 
          (risk.riskProbability < 0.4 ? "low" : risk.riskProbability < 0.7 ? "medium" : "high") : null

        return {
          id: app.id,
          name: `${app.applicant?.firstName || ''} ${app.applicant?.lastName || ''}`.trim() || 'N/A',
          confirmationCode: app.confirmationCode || 'N/A',
          listingName: app.listings?.name || 'Unknown Listing',
          state: app.applicant?.applicantAddress?.state || 'N/A',
          riskScore: risk?.riskProbability ? Math.round(risk.riskProbability * 100) : null,
          riskLevel,
          submissionDate: new Date(app.createdAt).toLocaleDateString(),
          income: risk?.income || 0,
          age: risk?.age || 0,
          veteran: risk?.veteran || false,
          disabled: risk?.disabled || false,
          benefits: risk?.benefits || false,
          householdSize: risk?.numPeople || app.householdSize || 1,
        }
      })
      .sort((a, b) => {
        const aVal = a[sortField as keyof typeof a]
        const bVal = b[sortField as keyof typeof b]
        const direction = sortDirection === 'asc' ? 1 : -1
        
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return (aVal - bVal) * direction
        }
        return String(aVal).localeCompare(String(bVal)) * direction
      })

    // Debug: Log risk levels being generated
    const riskLevelCounts = processed.reduce((acc, app) => {
      acc[app.riskLevel || 'null'] = (acc[app.riskLevel || 'null'] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    console.log('=== RISK LEVELS DEBUG ===')
    console.log('Risk level distribution in processed apps:', riskLevelCounts)
    console.log('First 3 processed apps:', processed.slice(0, 3).map(app => ({
      name: app.name,
      riskScore: app.riskScore,
      riskLevel: app.riskLevel
    })))

    return processed
  }, [filteredApplications, sortField, sortDirection])

  const paginatedApplications = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return processedApplications.slice(startIndex, startIndex + itemsPerPage)
  }, [processedApplications, currentPage, itemsPerPage])

  const totalPages = Math.ceil(processedApplications.length / itemsPerPage)

  const getRiskBadge = (level: string | null) => {
    console.log('getRiskBadge called with:', level, 'type:', typeof level)
    
    if (!level) return <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">N/A</span>
    
    // Normalize the level to lowercase for comparison
    const normalizedLevel = level.toLowerCase().trim()
    
    // Use explicit conditional rendering with inline styles as backup
    if (normalizedLevel === 'low') {
      return (
        <span 
          className="px-3 py-1 text-xs rounded-full font-bold uppercase tracking-wide text-white shadow-md"
          style={{ backgroundColor: '#059669' }}
        >
          LOW
        </span>
      )
    }
    
    if (normalizedLevel === 'medium') {
      return (
        <span 
          className="px-3 py-1 text-xs rounded-full font-bold uppercase tracking-wide text-white shadow-md"
          style={{ backgroundColor: '#EAB308' }}
        >
          MEDIUM
        </span>
      )
    }
    
    if (normalizedLevel === 'high') {
      return (
        <span 
          className="px-3 py-1 text-xs rounded-full font-bold uppercase tracking-wide text-white shadow-md"
          style={{ backgroundColor: '#DC2626' }}
        >
          HIGH
        </span>
      )
    }
    
    // Fallback for any other value - show what we got for debugging
    console.warn('Unknown risk level:', level, 'normalized:', normalizedLevel)
    return (
      <span className="px-3 py-1 text-xs rounded-full font-bold uppercase tracking-wide bg-gray-500 text-white shadow-md">
        {level}
      </span>
    )
  }

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const { riskDistribution, demographics, ageDistribution, householdDistribution, incomeDistribution, riskFactors } = riskAnalytics

  console.log('=== RISK DASHBOARD DEBUG ===')
  console.log('Total applications received:', applications?.length || 0)
  console.log('Applications with risk data:', demographics.totalWithRisk)
  console.log('Filtered applications (after filters):', filteredApplications.length)
  
  // Handle loading and empty states AFTER all hooks are defined
  if (appsLoading) {
    return (
      <div className="w-full max-w-full mx-auto p-6 pt-12">
        <div className="text-center py-12">
          <div className="animate-pulse">
            <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4"></div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Loading Applications...</h3>
            <p className="text-gray-500">Please wait while we fetch the risk analytics data.</p>
          </div>
        </div>
      </div>
    )
  }

  if (!applications?.length) {
    return (
      <div className="w-full max-w-full mx-auto p-6 pt-12">
        <div className="text-center py-12">
          <div className="animate-pulse">
            <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4"></div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Applications Found</h3>
            <p className="text-gray-500">There are no applications to display risk analytics for.</p>
          </div>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: TrendingUp },
    { id: 'breakdown', name: 'Breakdown', icon: Users },
    { id: 'factors', name: 'Risk Factors', icon: BarChart3 },
    { id: 'applications', name: 'Applications', icon: AlertTriangle }
  ]

  return (
    <div className="w-full max-w-full mx-auto p-4 sm:p-6 pt-8 sm:pt-12 bg-gray-50 min-h-screen">
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideInUp {
          from { 
            opacity: 0; 
            transform: translateY(20px); 
          }
          to { 
            opacity: 1; 
            transform: translateY(0); 
          }
        }
        @keyframes slideInLeft {
          from { 
            opacity: 0; 
            transform: translateX(-20px); 
          }
          to { 
            opacity: 1; 
            transform: translateX(0); 
          }
        }
        @keyframes slideInRight {
          from { 
            opacity: 0; 
            transform: translateX(20px); 
          }
          to { 
            opacity: 1; 
            transform: translateX(0); 
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
        .animate-slideInUp {
          animation: slideInUp 0.6s ease-out;
        }
        .animate-slideInLeft {
          animation: slideInLeft 0.7s ease-out;
        }
        .animate-slideInRight {
          animation: slideInRight 0.7s ease-out;
        }
      `}</style>

      {/* Header */}
      <div className="mb-2 text-center animate-slideInUp">
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
          Risk Score Analytics
        </h1>
        <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto">
          Comprehensive analysis of application risk factors and demographic patterns
        </p>
      </div>

      {/* Filters */}
      <div className="mb-8">
        <AnimatedCard className="animate-slideInUp" delay={100}>
          <div className="flex items-center gap-4 mb-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="w-full">
              <label className="block text-sm font-medium text-gray-700 mb-2">Listing</label>
              <select
                value={selectedListing}
                onChange={(e) => setSelectedListing(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Listings</option>
                {filterOptions.listings.map(listing => (
                  <option key={listing} value={listing}>{listing}</option>
                ))}
              </select>
            </div>
            <div className="w-full">
              <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All States</option>
                {filterOptions.states.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>
            <div className="w-full">
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Name or confirmation code..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </AnimatedCard>
      </div>

      {/* Responsive Navigation Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          {/* Desktop tabs */}
          <nav className="hidden lg:flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors duration-200`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.name}
                </button>
              )
            })}
          </nav>

          {/* Mobile/Tablet dropdown */}
          <div className="lg:hidden relative">
            <button
              onClick={() => setShowTabDropdown(!showTabDropdown)}
              className="w-full flex items-center justify-between py-4 px-4 bg-white border border-gray-300 rounded-lg text-left"
            >
              <div className="flex items-center gap-2">
                {React.createElement(tabs.find(tab => tab.id === activeTab)?.icon || TrendingUp, { className: "w-4 h-4" })}
                <span className="font-medium">{tabs.find(tab => tab.id === activeTab)?.name}</span>
              </div>
              <ChevronDown className={`w-4 h-4 transition-transform ${showTabDropdown ? 'rotate-180' : ''}`} />
            </button>
            
            {showTabDropdown && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-10">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => {
                        setActiveTab(tab.id)
                        setShowTabDropdown(false)
                      }}
                      className={`${
                        activeTab === tab.id
                          ? 'bg-blue-50 text-blue-600'
                          : 'text-gray-700 hover:bg-gray-50'
                      } w-full flex items-center gap-2 px-4 py-3 text-left transition-colors duration-200 first:rounded-t-lg last:rounded-b-lg`}
                    >
                      <Icon className="w-4 h-4" />
                      {tab.name}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
            <StatCard 
              title="Total Applications" 
              value={applications?.length || 0} 
              color="blue"
              delay={100}
              icon={<Users className="w-6 h-6 text-blue-500" />}
            />
            <StatCard 
              title="With Risk Data" 
              value={demographics.totalWithRisk} 
              subtitle={`${Math.round((demographics.totalWithRisk / Math.max(applications?.length || 1, 1)) * 100)}% coverage`}
              color="yellow"
              delay={200}
              icon={<TrendingUp className="w-6 h-6 text-yellow-500" />}
            />
            <StatCard 
              title="Average Income" 
              value={demographics.avgIncome > 0 ? `$${demographics.avgIncome.toLocaleString()}` : 'N/A'} 
              color="green"
              delay={300}
              icon={<DollarSign className="w-6 h-6 text-green-500" />}
            />
            <StatCard 
              title="High Risk" 
              value={riskDistribution[2]?.value || 0} 
              subtitle={`${Math.round(((riskDistribution[2]?.value || 0) / Math.max(demographics.totalWithRisk, 1)) * 100)}% of total`}
              color="red"
              delay={400}
              icon={<AlertTriangle className="w-6 h-6 text-red-500" />}
            />
          </div>

          {/* Risk Distribution Pie Chart */}
          <AnimatedCard delay={500} className="animate-slideInUp">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 text-center">
              Risk Level Distribution
            </h2>
            <div className="h-64 sm:h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    animationBegin={500}
                    animationDuration={1000}
                  >
                    {riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<PieTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap justify-center gap-4 mt-4">
              {riskDistribution.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-sm font-medium text-gray-700">
                    {item.name}: {item.value}
                  </span>
                </div>
              ))}
            </div>
          </AnimatedCard>
        </div>
      )}

      {activeTab === 'breakdown' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          {/* Age Distribution */}
          <AnimatedCard delay={100} className="animate-slideInLeft">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 text-center">
              Age Distribution
            </h2>
            <div className="h-64 sm:h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={ageDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="age" 
                    tick={{ fontSize: 12 }}
                    className="text-gray-600"
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    className="text-gray-600"
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke={CHART_COLORS[1]}
                    fill={CHART_COLORS[1]}
                    fillOpacity={0.3}
                    animationBegin={100}
                    animationDuration={1200}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </AnimatedCard>

          {/* Income Distribution */}
          <AnimatedCard delay={200} className="animate-slideInRight">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 text-center">
              Income Distribution
            </h2>
            <div className="h-64 sm:h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={incomeDistribution} margin={{ bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="range" 
                    tick={{ fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                    className="text-gray-600"
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    className="text-gray-600"
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar 
                    dataKey="count" 
                    fill={CHART_COLORS[4]}
                    radius={[4, 4, 0, 0]}
                    animationBegin={200}
                    animationDuration={1000}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </AnimatedCard>

          {/* Household Size Distribution */}
          <AnimatedCard delay={300} className="animate-slideInLeft">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 text-center">
              Household Size Distribution
            </h2>
            <div className="h-64 sm:h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={householdDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="size" 
                    tick={{ fontSize: 12 }}
                    className="text-gray-600"
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    className="text-gray-600"
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke={CHART_COLORS[2]}
                    strokeWidth={3}
                    dot={{ fill: CHART_COLORS[2], strokeWidth: 2, r: 6 }}
                    activeDot={{ r: 8, stroke: CHART_COLORS[2], strokeWidth: 2 }}
                    animationBegin={300}
                    animationDuration={1200}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </AnimatedCard>

          {/* Demographics Summary */}
          <AnimatedCard delay={400} className="animate-slideInRight">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 text-center">
              Demographic Highlights
            </h2>
            <div className="space-y-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl sm:text-3xl font-bold text-blue-600 mb-2">
                  {demographics.veteran}
                </div>
                <div className="text-sm font-medium text-blue-800 uppercase tracking-wide">
                  Veterans
                </div>
                <div className="text-xs text-blue-600 mt-1">
                  {Math.round((demographics.veteran / Math.max(filteredApplications.length, 1)) * 100)}% of applications
                </div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl sm:text-3xl font-bold text-purple-600 mb-2">
                  {demographics.disabled}
                </div>
                <div className="text-sm font-medium text-purple-800 uppercase tracking-wide">
                  Disabled
                </div>
                <div className="text-xs text-purple-600 mt-1">
                  {Math.round((demographics.disabled / Math.max(filteredApplications.length, 1)) * 100)}% of applications
                </div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl sm:text-3xl font-bold text-green-600 mb-2">
                  {demographics.benefits}
                </div>
                <div className="text-sm font-medium text-green-800 uppercase tracking-wide">
                  Receiving Benefits
                </div>
                <div className="text-xs text-green-600 mt-1">
                  {Math.round((demographics.benefits / Math.max(filteredApplications.length, 1)) * 100)}% of applications
                </div>
              </div>
            </div>
          </AnimatedCard>
        </div>
      )}

      {activeTab === 'factors' && (
        <div className="space-y-6">
          {/* Risk Factors Analysis */}
          <AnimatedCard className="animate-slideInUp" delay={100}>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 text-center">
              Risk Factors Analysis
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
              {/* Risk Factors Bar Chart */}
              <AnimatedCard delay={100} className="animate-slideInLeft">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
                  Risk Factors by Category
                </h3>
                <div className="h-64 sm:h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[
                      { name: 'Veteran', low: riskFactors.veteran.low, medium: riskFactors.veteran.medium, high: riskFactors.veteran.high },
                      { name: 'Disabled', low: riskFactors.disabled.low, medium: riskFactors.disabled.medium, high: riskFactors.disabled.high },
                      { name: 'Benefits', low: riskFactors.benefits.low, medium: riskFactors.benefits.medium, high: riskFactors.benefits.high },
                      { name: 'Low Income', low: riskFactors.lowIncome.low, medium: riskFactors.lowIncome.medium, high: riskFactors.lowIncome.high },
                      { name: 'Large HH', low: riskFactors.largeHousehold.low, medium: riskFactors.largeHousehold.medium, high: riskFactors.largeHousehold.high },
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="name" 
                        tick={{ fontSize: 12 }}
                        className="text-gray-600"
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                        className="text-gray-600"
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="low" stackId="a" fill={RISK_COLORS.low} />
                      <Bar dataKey="medium" stackId="a" fill={RISK_COLORS.medium} />
                      <Bar dataKey="high" stackId="a" fill={RISK_COLORS.high} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </AnimatedCard>

              {/* Risk Factors Summary */}
              <AnimatedCard delay={200} className="animate-slideInRight">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
                  High Risk Factor Summary
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg border-l-4 border-red-500">
                    <div className="flex items-center gap-2">
                      <Award className="w-4 h-4 text-red-600" />
                      <span className="text-sm font-medium text-red-800">Veterans</span>
                    </div>
                    <span className="text-lg font-bold text-red-600">{riskFactors.veteran.high}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg border-l-4 border-purple-500">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-medium text-purple-800">Disabled</span>
                    </div>
                    <span className="text-lg font-bold text-purple-600">{riskFactors.disabled.high}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-800">Receiving Benefits</span>
                    </div>
                    <span className="text-lg font-bold text-blue-600">{riskFactors.benefits.high}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg border-l-4 border-orange-500">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-orange-600" />
                      <span className="text-sm font-medium text-orange-800">Low Income (&lt;$30k)</span>
                    </div>
                    <span className="text-lg font-bold text-orange-600">{riskFactors.lowIncome.high}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                    <div className="flex items-center gap-2">
                      <Home className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-800">Large Household (5+)</span>
                    </div>
                    <span className="text-lg font-bold text-green-600">{riskFactors.largeHousehold.high}</span>
                  </div>
                </div>
              </AnimatedCard>
            </div>
          </AnimatedCard>
        </div>
      )}

      {activeTab === 'applications' && (
        <div className="space-y-6">
          {/* Applications Table */}
          <AnimatedCard className="animate-slideInUp" delay={100}>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900">
                Individual Applications ({processedApplications.length})
              </h2>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {[
                      { key: 'name', label: 'Name' },
                      { key: 'confirmationCode', label: 'Confirmation' },
                      { key: 'listingName', label: 'Listing' },
                      { key: 'state', label: 'State' },
                      { key: 'riskScore', label: 'Risk Score' },
                      { key: 'riskLevel', label: 'Risk Level' },
                      { key: 'submissionDate', label: 'Submitted' },
                      { key: 'income', label: 'Income' },
                      { key: 'householdSize', label: 'Household' },
                    ].map((column) => (
                      <th
                        key={column.key}
                        onClick={() => handleSort(column.key)}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center gap-1">
                          {column.label}
                          {sortField === column.key && (
                            <ChevronDown className={`w-4 h-4 transition-transform ${sortDirection === 'asc' ? 'rotate-180' : ''}`} />
                          )}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paginatedApplications.map((app, index) => (
                    <tr key={app.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {app.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono">
                        {app.confirmationCode}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {app.listingName}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {app.state}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                        {app.riskScore !== null ? `${app.riskScore}%` : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getRiskBadge(app.riskLevel)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {app.submissionDate}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {app.income > 0 ? `$${app.income.toLocaleString()}` : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {app.householdSize}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-gray-700">
                  Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, processedApplications.length)} of {processedApplications.length} results
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-2 text-sm border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
                  >
                    Previous
                  </button>
                  <span className="px-3 py-2 text-sm text-gray-700">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-2 text-sm border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </AnimatedCard>
        </div>
      )}
    </div>
  )
}

export default RiskScoreDashboard 