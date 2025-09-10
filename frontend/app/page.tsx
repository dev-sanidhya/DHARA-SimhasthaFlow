"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Users,
  MapPin,
  AlertTriangle,
  Navigation,
  Activity,
  Shield,
  Clock,
  TrendingUp,
  Eye,
  Bell,
  User,
  Moon,
  Sun,
  Route,
  Accessibility,
  Play,
  Pause,
  RotateCcw,
  Thermometer,
  Droplets,
  Wind,
  UserCheck,
  Map,
  Navigation2,
  Ambulance,
  Radio,
  Timer,
} from "lucide-react"

interface CrowdData {
  zone_id: string
  zone_name: string
  current_occupancy: number
  max_capacity: number
  crowd_level: "low" | "medium" | "high" | "critical"
  safety_score: number
  accessibility_features: string[]
  last_updated: string
}

interface Emergency {
  id: string
  type: string
  location: string
  severity: "low" | "medium" | "high" | "critical"
  status: "active" | "resolved" | "responding"
  timestamp: string
  response_time?: number
  assigned_team?: string
}

interface WeatherData {
  temperature: number
  humidity: number
  wind_speed: number
  conditions: string
  impact_level: "low" | "medium" | "high"
  alerts: string[]
}

interface RouteData {
  id: string
  name: string
  type: "pilgrim" | "vip" | "emergency" | "accessibility"
  distance: number
  estimated_time: number
  safety_score: number
  features: string[]
  current_traffic: "low" | "medium" | "high"
}

interface SimulationScenario {
  id: string
  name: string
  type: "crowd_overflow" | "weather_emergency" | "vip_movement" | "accessibility_event"
  description: string
  duration: number
}

export default function DHARADashboard() {
  const [crowdData, setCrowdData] = useState<CrowdData[]>([])
  const [emergencies, setEmergencies] = useState<Emergency[]>([])
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [routes, setRoutes] = useState<RouteData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [syncStatus, setSyncStatus] = useState<"online" | "partial" | "offline">("online")
  const [selectedScenario, setSelectedScenario] = useState<string>("")
  const [simulationProgress, setSimulationProgress] = useState(0)
  const [isSimulationRunning, setIsSimulationRunning] = useState(false)
  const [mapOverlay, setMapOverlay] = useState<"crowd" | "weather" | "routes" | "accessibility">("crowd")
  const [notifications, setNotifications] = useState(3)

  useEffect(() => {
    const mockCrowdData: CrowdData[] = [
      {
        zone_id: "1",
        zone_name: "Mahakaleshwar Temple",
        current_occupancy: 2850,
        max_capacity: 3000,
        crowd_level: "high",
        safety_score: 7.2,
        accessibility_features: ["Wheelchair Access", "Audio Guidance", "Rest Areas"],
        last_updated: new Date().toISOString(),
      },
      {
        zone_id: "2",
        zone_name: "Shipra Ghat",
        current_occupancy: 1450,
        max_capacity: 2000,
        crowd_level: "medium",
        safety_score: 8.5,
        accessibility_features: ["Ramp Access", "Portable Toilets", "Medical Station"],
        last_updated: new Date().toISOString(),
      },
      {
        zone_id: "3",
        zone_name: "VIP Parking Zone",
        current_occupancy: 320,
        max_capacity: 500,
        crowd_level: "medium",
        safety_score: 9.1,
        accessibility_features: ["Reserved Parking", "Security", "Direct Access"],
        last_updated: new Date().toISOString(),
      },
      {
        zone_id: "4",
        zone_name: "Medical Center Hub",
        current_occupancy: 45,
        max_capacity: 100,
        crowd_level: "low",
        safety_score: 9.8,
        accessibility_features: ["Emergency Access", "Ambulance Bay", "Helicopter Pad"],
        last_updated: new Date().toISOString(),
      },
      {
        zone_id: "5",
        zone_name: "Food Court Area",
        current_occupancy: 890,
        max_capacity: 1200,
        crowd_level: "medium",
        safety_score: 8.3,
        accessibility_features: ["Wheelchair Tables", "Water Stations", "Shade Covers"],
        last_updated: new Date().toISOString(),
      },
    ]

    const mockEmergencies: Emergency[] = [
      {
        id: "1",
        type: "Medical Emergency",
        location: "Mahakaleshwar Temple - Section B",
        severity: "high",
        status: "responding",
        timestamp: "2024-01-15T10:30:00Z",
        response_time: 4,
        assigned_team: "Medical Team Alpha",
      },
      {
        id: "2",
        type: "Crowd Congestion",
        location: "Shipra Ghat - Entry Point 2",
        severity: "medium",
        status: "active",
        timestamp: "2024-01-15T11:15:00Z",
        assigned_team: "Crowd Control Beta",
      },
    ]

    const mockWeather: WeatherData = {
      temperature: 32,
      humidity: 68,
      wind_speed: 12,
      conditions: "Partly Cloudy",
      impact_level: "medium",
      alerts: ["High Temperature Warning", "Increased Hydration Needed"],
    }

    const mockRoutes: RouteData[] = [
      {
        id: "1",
        name: "Main Pilgrim Route",
        type: "pilgrim",
        distance: 2.5,
        estimated_time: 15,
        safety_score: 8.5,
        features: ["Shade Coverage", "Water Points", "Rest Areas"],
        current_traffic: "high",
      },
      {
        id: "2",
        name: "VIP Corridor",
        type: "vip",
        distance: 1.8,
        estimated_time: 8,
        safety_score: 9.2,
        features: ["Security Escort", "Climate Control", "Direct Access"],
        current_traffic: "low",
      },
      {
        id: "3",
        name: "Emergency Access Route",
        type: "emergency",
        distance: 1.2,
        estimated_time: 5,
        safety_score: 9.8,
        features: ["Clear Path", "Emergency Lighting", "Communication Points"],
        current_traffic: "low",
      },
      {
        id: "4",
        name: "Accessibility Path",
        type: "accessibility",
        distance: 3.2,
        estimated_time: 25,
        safety_score: 9.0,
        features: ["Wheelchair Friendly", "Gentle Slopes", "Audio Guidance"],
        current_traffic: "medium",
      },
    ]

    setCrowdData(mockCrowdData)
    setEmergencies(mockEmergencies)
    setWeather(mockWeather)
    setRoutes(mockRoutes)
    setIsLoading(false)
  }, [])

  const getCrowdLevelColor = (level: string) => {
    switch (level) {
      case "low":
        return "bg-green-100 text-green-800 border-green-200"
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-200"
      case "critical":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low":
        return "bg-blue-100 text-blue-800"
      case "medium":
        return "bg-yellow-100 text-yellow-800"
      case "high":
        return "bg-orange-100 text-orange-800"
      case "critical":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getRouteTypeIcon = (type: string) => {
    switch (type) {
      case "pilgrim":
        return <Users className="h-4 w-4" />
      case "vip":
        return <Shield className="h-4 w-4" />
      case "emergency":
        return <Ambulance className="h-4 w-4" />
      case "accessibility":
        return <Accessibility className="h-4 w-4" />
      default:
        return <Route className="h-4 w-4" />
    }
  }

  const simulationScenarios: SimulationScenario[] = [
    {
      id: "1",
      name: "Crowd Overflow Scenario",
      type: "crowd_overflow",
      description: "Simulate high crowd density during peak hours",
      duration: 30,
    },
    {
      id: "2",
      name: "Weather Emergency",
      type: "weather_emergency",
      description: "Heavy rainfall impact on crowd movement",
      duration: 45,
    },
    {
      id: "3",
      name: "VIP Movement Protocol",
      type: "vip_movement",
      description: "Coordinate VIP arrival and route clearance",
      duration: 20,
    },
    {
      id: "4",
      name: "Accessibility Event",
      type: "accessibility_event",
      description: "Large group requiring accessibility assistance",
      duration: 35,
    },
  ]

  const startSimulation = () => {
    setIsSimulationRunning(true)
    setSimulationProgress(0)
    const interval = setInterval(() => {
      setSimulationProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsSimulationRunning(false)
          return 100
        }
        return prev + 2
      })
    }, 200)
  }

  const resetSimulation = () => {
    setIsSimulationRunning(false)
    setSimulationProgress(0)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading SimhasthaFlow Dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen bg-background ${isDarkMode ? "dark" : ""}`}>
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <Shield className="h-8 w-8 text-primary" />
                <div>
                  <h1 className="text-2xl font-bold text-foreground">SimhasthaFlow</h1>
                  <p className="text-sm text-muted-foreground">Real-Time Operations</p>
                </div>
              </div>
              <Badge variant="secondary" className="text-xs font-medium">
                Ujjain Pilgrimage Management
              </Badge>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>{new Date().toLocaleTimeString()}</span>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-sm text-muted-foreground">Sync:</span>
                <div className={`sync-indicator sync-${syncStatus} pulse-dot`} />
              </div>

              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="sm" onClick={() => setIsDarkMode(!isDarkMode)} className="h-8 w-8 p-0">
                  {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>

                <Button variant="ghost" size="sm" className="relative">
                  <Bell className="h-4 w-4" />
                  {notifications > 0 && (
                    <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs">{notifications}</Badge>
                  )}
                </Button>

                <Button variant="ghost" size="sm">
                  <User className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        {emergencies.filter((e) => e.status === "active" || e.status === "responding").length > 0 && (
          <div className="mb-6 space-y-3">
            {emergencies
              .filter((e) => e.status === "active" || e.status === "responding")
              .map((emergency) => (
                <Alert key={emergency.id} className="border-red-300 bg-white shadow-md">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <AlertTitle className="flex items-center justify-between">
                    <span className="text-red-900 font-semibold">
                      {emergency.type} - {emergency.severity.toUpperCase()}
                    </span>
                    <Badge
                      variant={emergency.status === "responding" ? "default" : "destructive"}
                      className="text-white font-medium"
                    >
                      {emergency.status}
                    </Badge>
                  </AlertTitle>
                  <AlertDescription className="mt-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-900 font-medium">Location: {emergency.location}</p>
                        <p className="text-xs text-gray-700">
                          Time: {new Date(emergency.timestamp).toLocaleTimeString()}
                          {emergency.assigned_team && ` | Team: ${emergency.assigned_team}`}
                          {emergency.response_time && ` | Response: ${emergency.response_time} min`}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="destructive">
                          <Radio className="h-4 w-4 mr-1" />
                          Contact Team
                        </Button>
                        <Button size="sm" variant="outline">
                          <Navigation2 className="h-4 w-4 mr-1" />
                          View Location
                        </Button>
                      </div>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
          </div>
        )}

        <Tabs defaultValue="map" className="space-y-6">
          <TabsList className="grid w-full grid-cols-7">
            <TabsTrigger value="map">Map View</TabsTrigger>
            <TabsTrigger value="routing">Routing Insights</TabsTrigger>
            <TabsTrigger value="accessibility">Accessibility</TabsTrigger>
            <TabsTrigger value="emergency">Emergency</TabsTrigger>
            <TabsTrigger value="volunteer">Volunteers</TabsTrigger>
            <TabsTrigger value="simulation">Simulation</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="map" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Real-time stats panel */}
              <div className="lg:col-span-1 space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Live Statistics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Total Pilgrims</span>
                        <span className="font-medium">
                          {crowdData.reduce((sum, zone) => sum + zone.current_occupancy, 0).toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Active Zones</span>
                        <span className="font-medium">{crowdData.length}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Emergencies</span>
                        <span className="font-medium text-destructive">
                          {emergencies.filter((e) => e.status === "active").length}
                        </span>
                      </div>
                    </div>

                    <div className="pt-4 border-t">
                      <h4 className="text-sm font-medium mb-2">Weather Conditions</h4>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-2">
                            <Thermometer className="h-4 w-4" />
                            <span>Temperature</span>
                          </div>
                          <span>{weather?.temperature}°C</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-2">
                            <Droplets className="h-4 w-4" />
                            <span>Humidity</span>
                          </div>
                          <span>{weather?.humidity}%</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center space-x-2">
                            <Wind className="h-4 w-4" />
                            <span>Wind Speed</span>
                          </div>
                          <span>{weather?.wind_speed} km/h</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Map Controls</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Overlay Type</label>
                      <Select value={mapOverlay} onValueChange={(value: any) => setMapOverlay(value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="crowd">Crowd Density</SelectItem>
                          <SelectItem value="weather">Weather Impact</SelectItem>
                          <SelectItem value="routes">Route Status</SelectItem>
                          <SelectItem value="accessibility">Accessibility</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Real-time Updates</span>
                        <Switch defaultChecked />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Show Alerts</span>
                        <Switch defaultChecked />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">VIP Routes</span>
                        <Switch />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Interactive map centerpiece */}
              <div className="lg:col-span-3">
                <Card className="h-[600px]">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>
                        Ujjain Pilgrimage Map - {mapOverlay.charAt(0).toUpperCase() + mapOverlay.slice(1)} View
                      </span>
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          Full Screen
                        </Button>
                        <Button variant="outline" size="sm">
                          <Map className="h-4 w-4 mr-2" />
                          Satellite
                        </Button>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="h-full p-0">
                    <div className="relative h-full bg-gradient-to-br from-green-50 to-blue-50 rounded-lg overflow-hidden">
                      <div className="map-overlay" />

                      {/* Map zones representation */}
                      <div className="absolute inset-4 grid grid-cols-3 gap-4">
                        {crowdData.slice(0, 6).map((zone, index) => (
                          <div
                            key={zone.zone_id}
                            className={`relative p-4 rounded-lg border-2 cursor-pointer transition-all hover:scale-105 ${
                              zone.crowd_level === "high"
                                ? "heatmap-high border-red-300"
                                : zone.crowd_level === "medium"
                                  ? "heatmap-medium border-yellow-300"
                                  : "heatmap-low border-green-300"
                            }`}
                          >
                            <div className="text-center">
                              <h4 className="font-medium text-sm mb-1">{zone.zone_name}</h4>
                              <p className="text-xs text-muted-foreground">
                                {zone.current_occupancy}/{zone.max_capacity}
                              </p>
                              <Badge className={`mt-1 ${getCrowdLevelColor(zone.crowd_level)}`} size="sm">
                                {zone.crowd_level}
                              </Badge>
                            </div>

                            {/* Animated pulse for high activity */}
                            {zone.crowd_level === "high" && (
                              <div className="absolute inset-0 rounded-lg border-2 border-red-400 animate-pulse" />
                            )}
                          </div>
                        ))}
                      </div>

                      {/* Legend */}
                      <div className="absolute bottom-4 left-4 bg-white/90 p-3 rounded-lg shadow-lg">
                        <h4 className="font-medium text-sm mb-2">Crowd Density</h4>
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2 text-xs">
                            <div className="w-3 h-3 bg-green-500/30 rounded" />
                            <span>Low</span>
                          </div>
                          <div className="flex items-center space-x-2 text-xs">
                            <div className="w-3 h-3 bg-yellow-500/30 rounded" />
                            <span>Medium</span>
                          </div>
                          <div className="flex items-center space-x-2 text-xs">
                            <div className="w-3 h-3 bg-red-500/30 rounded" />
                            <span>High</span>
                          </div>
                        </div>
                      </div>

                      {/* Zoom controls */}
                      <div className="absolute top-4 right-4 flex flex-col space-y-2">
                        <Button variant="outline" size="sm" className="w-8 h-8 p-0 bg-transparent">
                          +
                        </Button>
                        <Button variant="outline" size="sm" className="w-8 h-8 p-0 bg-transparent">
                          -
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Crowd Status */}
          <TabsContent value="crowd" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Crowd Monitoring</CardTitle>
                <CardDescription>Real-time crowd density and movement patterns</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Zone Occupancy</h4>
                    {crowdData.map((zone) => (
                      <div key={zone.zone_id} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>{zone.zone_name}</span>
                          <span>{Math.round((zone.current_occupancy / zone.max_capacity) * 100)}%</span>
                        </div>
                        <Progress value={(zone.current_occupancy / zone.max_capacity) * 100} />
                      </div>
                    ))}
                  </div>
                  <div className="bg-muted rounded-lg p-6 flex items-center justify-center">
                    <div className="text-center">
                      <MapPin className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">Interactive Map View</p>
                      <p className="text-sm text-muted-foreground mt-2">
                        Real-time crowd visualization would appear here
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Route Planning */}
          <TabsContent value="routing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Route Planning</CardTitle>
                <CardDescription>Optimize routes based on crowd levels and safety</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <Button className="w-full">
                      <Navigation className="h-4 w-4 mr-2" />
                      Generate Optimal Route
                    </Button>
                    <div className="space-y-2">
                      <h4 className="font-medium">Route Options</h4>
                      <div className="space-y-2">
                        {routes.map((route) => (
                          <div key={route.id} className="p-3 border border-border rounded-lg">
                            <div className="flex justify-between items-center">
                              <span className="font-medium">{route.name}</span>
                              {route.type === "vip" && <Badge variant="secondary">VIP</Badge>}
                              {route.type === "emergency" && <Badge variant="destructive">Emergency</Badge>}
                              {route.type === "accessibility" && <Badge variant="outline">Accessibility</Badge>}
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              Estimated time: {route.estimated_time} min | Safety score: {route.safety_score}/10
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="bg-muted rounded-lg p-6 flex items-center justify-center">
                    <div className="text-center">
                      <Navigation className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">Route Visualization</p>
                      <p className="text-sm text-muted-foreground mt-2">Interactive route map would appear here</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Accessibility */}
          <TabsContent value="accessibility" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Accessibility Management</CardTitle>
                <CardDescription>Ensure smooth movement for all pilgrims</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Accessibility Features</h4>
                    {crowdData.map((zone) => (
                      <div key={zone.zone_id} className="p-3 border border-border rounded-lg">
                        <h5 className="font-medium">{zone.zone_name}</h5>
                        <ul className="list-disc list-inside text-sm text-muted-foreground">
                          {zone.accessibility_features.map((feature, index) => (
                            <li key={index}>{feature}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                  <div className="bg-muted rounded-lg p-6 flex items-center justify-center">
                    <div className="text-center">
                      <Accessibility className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">Accessibility Map View</p>
                      <p className="text-sm text-muted-foreground mt-2">
                        Interactive accessibility map would appear here
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Emergency */}
          <TabsContent value="emergency" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Emergency Management</CardTitle>
                <CardDescription>Monitor and respond to emergency situations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button className="w-full" variant="destructive">
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Report New Emergency
                  </Button>
                  <div className="space-y-2">
                    <h4 className="font-medium">Active Emergencies</h4>
                    {emergencies
                      .filter((e) => e.status === "active")
                      .map((emergency) => (
                        <div key={emergency.id} className="p-4 border border-border rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <h5 className="font-medium">{emergency.type}</h5>
                              <p className="text-sm text-muted-foreground">{emergency.location}</p>
                              <p className="text-xs text-muted-foreground mt-1">
                                {new Date(emergency.timestamp).toLocaleString()}
                              </p>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge className={`${getSeverityColor(emergency.severity)} text-white font-medium`}>
                                {emergency.severity}
                              </Badge>
                              <Button size="sm">Respond</Button>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Volunteers */}
          <TabsContent value="volunteer" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Volunteer Coordination</CardTitle>
                <CardDescription>Manage and deploy volunteer teams</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Volunteer Teams</h4>
                    <div className="p-3 border border-border rounded-lg">
                      <h5 className="font-medium">Team Alpha</h5>
                      <p className="text-sm text-muted-foreground">Location: Mahakaleshwar Temple</p>
                    </div>
                    <div className="p-3 border border-border rounded-lg">
                      <h5 className="font-medium">Team Beta</h5>
                      <p className="text-sm text-muted-foreground">Location: Shipra Ghat</p>
                    </div>
                  </div>
                  <div className="bg-muted rounded-lg p-6 flex items-center justify-center">
                    <div className="text-center">
                      <UserCheck className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">Volunteer Deployment Map</p>
                      <p className="text-sm text-muted-foreground mt-2">
                        Interactive volunteer deployment map would appear here
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Simulation */}
          <TabsContent value="simulation" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Simulation Console - Command Center</CardTitle>
                <CardDescription>Test scenarios and analyze system responses for better preparedness</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">Select Scenario</label>
                      <Select value={selectedScenario} onValueChange={setSelectedScenario}>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose a simulation scenario" />
                        </SelectTrigger>
                        <SelectContent>
                          {simulationScenarios.map((scenario) => (
                            <SelectItem key={scenario.id} value={scenario.id}>
                              {scenario.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {selectedScenario && (
                      <div className="p-4 bg-muted rounded-lg">
                        <h4 className="font-medium mb-2">
                          {simulationScenarios.find((s) => s.id === selectedScenario)?.name}
                        </h4>
                        <p className="text-sm text-muted-foreground mb-3">
                          {simulationScenarios.find((s) => s.id === selectedScenario)?.description}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Duration: {simulationScenarios.find((s) => s.id === selectedScenario)?.duration} minutes
                        </p>
                      </div>
                    )}

                    <div className="flex space-x-2">
                      <Button
                        onClick={startSimulation}
                        disabled={!selectedScenario || isSimulationRunning}
                        className="flex-1"
                      >
                        {isSimulationRunning ? (
                          <>
                            <Pause className="h-4 w-4 mr-2" />
                            Running...
                          </>
                        ) : (
                          <>
                            <Play className="h-4 w-4 mr-2" />
                            Start Simulation
                          </>
                        )}
                      </Button>
                      <Button variant="outline" onClick={resetSimulation} disabled={simulationProgress === 0}>
                        <RotateCcw className="h-4 w-4" />
                      </Button>
                    </div>

                    {simulationProgress > 0 && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Progress</span>
                          <span>{simulationProgress}%</span>
                        </div>
                        <Progress value={simulationProgress} />
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-medium">Simulation Results</h4>
                    <div className="bg-muted rounded-lg p-6 flex items-center justify-center min-h-[200px]">
                      {simulationProgress > 0 ? (
                        <div className="text-center">
                          <Activity className="h-8 w-8 mx-auto mb-4 text-primary animate-spin" />
                          <p className="text-muted-foreground">Simulation in progress...</p>
                          <p className="text-sm text-muted-foreground mt-2">
                            Analyzing crowd patterns and system responses
                          </p>
                        </div>
                      ) : (
                        <div className="text-center">
                          <Timer className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
                          <p className="text-muted-foreground">Select and run a scenario</p>
                          <p className="text-sm text-muted-foreground mt-2">
                            Results will appear here during simulation
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics */}
          <TabsContent value="reports" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Analytics & Insights</CardTitle>
                <CardDescription>Historical data and predictive analytics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Key Insights</h4>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-green-600" />
                        <span className="text-sm">Peak hours: 10 AM - 2 PM</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                        <span className="text-sm">Average safety score: 8.4/10</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-orange-600" />
                        <span className="text-sm">Weather impact: Low to Medium</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-muted rounded-lg p-6 flex items-center justify-center">
                    <div className="text-center">
                      <Activity className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">Analytics Charts</p>
                      <p className="text-sm text-muted-foreground mt-2">
                        Historical trends and predictions would appear here
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
