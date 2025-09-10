# SimhasthaFlow (DHARA) - Smart Crowd Management System 🏛️

## 🌟 **What is SimhasthaFlow (DHARA)?**

**SimhasthaFlow**, also known as **DHARA** (Digital Heritage and Religious Assembly), is an intelligent crowd management and navigation system specifically designed for large-scale religious gatherings, particularly the **Simhastha Kumbh Mela** in Ujjain, Madhya Pradesh.

### 🎯 **The Challenge We Solve**

Religious festivals like Simhastha Kumbh attract **millions of pilgrims** over several weeks, creating unprecedented crowd management challenges:

- **Massive Scale**: 75+ million devotees during Simhastha 2016
- **Safety Concerns**: Risk of stampedes, medical emergencies, and crowd crushes
- **Navigation Complexity**: Pilgrims struggle to find temples, ghats, facilities, and safe routes
- **Real-time Coordination**: Need for instant communication during emergencies
- **Resource Optimization**: Efficient distribution of security, medical, and logistical resources

### 🎨 **Our Vision: Technology Meets Devotion**

DHARA bridges the gap between **ancient spiritual traditions** and **modern digital solutions**, ensuring that:

- **Devotees** can focus on their spiritual journey without safety concerns
- **Organizers** have real-time insights for proactive crowd management
- **Emergency responders** can react swiftly to incidents
- **Sacred spaces** remain accessible while maintaining safety standards

### 🏗️ **System Overview**

SimhasthaFlow is a comprehensive **FastAPI-based backend system** that provides:

#### 🔐 **Smart Authentication & Access Control**

- Role-based access for pilgrims, volunteers, security, and administrators
- JWT-based secure authentication with granular permissions

#### 📍 **Intelligent Zone Management**

- **Temples**: Mahakaleshwar Jyotirlinga, Harsiddhi, Chintaman Ganesh
- **Sacred Ghats**: Ram Ghat, Triveni Ghat, Mangalnath Ghat (on Shipra River)
- **Facilities**: Parking areas, medical centers, community kitchens (Bhandara)
- **Infrastructure**: Sadhu camps, security posts, emergency stations

#### 🚨 **Real-time Emergency Response**

- **Instant Incident Reporting**: Medical emergencies, stampedes, fires, security threats
- **Automated Evacuation Routes**: AI-powered pathfinding for emergency scenarios
- **Medical Facility Locator**: Nearest hospitals, first-aid stations, ambulance dispatch
- **Crisis Communication**: Emergency alerts and safety instructions

#### 🌊 **Live Crowd Monitoring**

- **WebSocket-powered Updates**: Real-time crowd density every 30 seconds
- **Occupancy Tracking**: Live headcount for temples, ghats, and public areas
- **Crowd Level Analytics**: LOW → MEDIUM → HIGH → CRITICAL classifications
- **Predictive Patterns**: Peak hours analysis and crowd flow predictions

#### 🗺️ **Smart Navigation & Routing**

- **Crowd-Aware Pathfinding**: Routes that avoid congested areas
- **Multi-modal Navigation**: Walking paths, vehicle routes, boat access
- **Accessibility Support**: Wheelchair-friendly routes and facilities
- **Popular Route Recommendations**: Tested paths used by other pilgrims

#### 🌤️ **Weather-Aware Planning**

- **Real-time Weather Integration**: Temperature, humidity, rainfall, wind
- **Crowd Impact Analysis**: How weather affects gathering patterns
- **Safety Alerts**: Heat warnings, storm notifications, visibility issues
- **Adaptive Recommendations**: Route changes based on weather conditions

### 🎯 **Target Use Cases**

#### **For Pilgrims (Devotees)**

- Find the shortest, safest route to Mahakaleshwar Temple
- Check crowd levels before visiting Ram Ghat for morning Aarti
- Locate nearest medical facility or parking area
- Receive emergency evacuation instructions

#### **For Event Organizers**

- Monitor real-time crowd distribution across all zones
- Coordinate emergency response teams effectively
- Analyze crowd patterns for better resource allocation
- Track incident resolution and response times

#### **For Emergency Services**

- Receive instant notifications of medical emergencies
- Access optimal evacuation routes during crowd control
- Coordinate with police, medical, and fire departments
- Maintain communication during crisis situations

#### **For Security Personnel**

- Track suspicious activities and security incidents
- Monitor unauthorized access to restricted areas
- Coordinate crowd control measures
- Ensure VIP area security and protocol compliance

### 🏛️ **Cultural Significance of Simhastha**

The **Simhastha Kumbh Mela** is one of the four sacred Kumbh Melas, rotating every 12 years:

- **Location**: Ujjain, on the banks of the sacred Shipra River
- **Spiritual Importance**: Bathing in Shipra is believed to wash away sins
- **Astronomical Timing**: Based on celestial positions of Jupiter, Sun, and Moon
- **Cultural Heritage**: UNESCO-recognized Intangible Cultural Heritage of Humanity
- **Economic Impact**: Massive boost to local economy, infrastructure, and tourism

### 💻 **Technical Architecture**

Built with modern, scalable technologies for reliability and performance:

- **Backend**: FastAPI (Python) with async capabilities
- **Database**: SQLite for development, easily scalable to PostgreSQL/MySQL
- **Real-time**: WebSocket connections for live updates
- **Authentication**: JWT tokens with role-based access control
- **API Design**: RESTful endpoints with comprehensive OpenAPI documentation
- **Data Modeling**: SQLAlchemy ORM with realistic Ujjain geographic data

---

## 🚀 **Getting Started**

A comprehensive crowd management and navigation system for religious gatherings, built with FastAPI and SQLite.

## 🚀 **Core Features**

### 🔐 **Authentication & Security**

- **JWT-based Authentication**: Secure token-based access control
- **Role-based Permissions**: Admin, Security, Medical, Pilgrim access levels
- **Session Management**: Secure login/logout with token expiration

### 📊 **Real-time Crowd Intelligence**

- **Live Crowd Monitoring**: WebSocket-powered density updates every 30 seconds
- **Occupancy Tracking**: Real-time headcount for 15+ zones (temples, ghats, facilities)
- **Crowd Level Classification**: Automatic LOW/MEDIUM/HIGH/CRITICAL categorization
- **Peak Hours Analytics**: Historical patterns and prediction algorithms

### 🗺️ **Smart Navigation System**

- **Crowd-Aware Routing**: AI-powered pathfinding that avoids congested areas
- **Multi-destination Planning**: Optimal routes covering multiple temples/ghats
- **Accessibility Support**: Wheelchair-friendly and elderly-accessible routes
- **Popular Route Recommendations**: Community-tested navigation paths

### 🌤️ **Weather-Integrated Planning**

- **Real-time Weather Data**: Temperature, humidity, rainfall, wind speed, UV index
- **Crowd Impact Analysis**: How weather conditions affect gathering patterns
- **Safety Alerts**: Heat warnings, storm notifications, visibility advisories
- **Adaptive Route Planning**: Weather-based route modifications

### 🏛️ **Comprehensive Zone Management**

- **Sacred Temples**: Mahakaleshwar Jyotirlinga, Harsiddhi, Chintaman Ganesh
- **Holy Ghats**: Ram Ghat, Triveni Ghat, Mangalnath Ghat on Shipra River
- **Essential Facilities**: Parking areas, medical centers, community kitchens
- **Support Infrastructure**: Sadhu camps, security posts, accommodation areas

### 🚨 **Advanced Emergency Response**

- **Multi-type Incident Management**: Medical, Stampede, Fire, Security, Natural disasters
- **Automated Evacuation Planning**: AI-generated escape routes based on incident type
- **Medical Facility Locator**: Instant access to nearest hospitals and first-aid stations
- **Emergency Communication**: Real-time alerts and safety instructions
- **Status Tracking**: Complete incident lifecycle management

### 📱 **Developer-Friendly API**

- **RESTful Architecture**: Clean, intuitive endpoint design
- **Comprehensive Documentation**: Auto-generated Swagger/OpenAPI specs
- **Real-time WebSocket**: Bidirectional communication for live updates
- **Mock Data Integration**: 55+ realistic emergency scenarios, crowd patterns
- **Easy Local Setup**: No Docker required, SQLite-based development

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🛠️ Installation & Setup

### 1. Clone or Download the Project

Make sure you have the project files in your desired directory.

### 2. Create a Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the Application

```powershell
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python module
python -m app.main

# Option 3: Direct Python execution
python app/main.py
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## 🔑 Authentication

### Default Admin Account

The system creates a default admin account for testing:

- **Username**: `admin`
- **Password**: `admin123`

### Getting Access Token

1. Go to http://localhost:8000/docs
2. Click on "Authorize" button
3. Use the login endpoint `/api/v1/auth/login` with admin credentials
4. Copy the `access_token` from the response
5. Click "Authorize" and enter: `Bearer <your_access_token>`

## 🌐 API Endpoints

### Authentication

- `POST /api/v1/auth/login` - User login and token generation
- `GET /api/v1/auth/me` - Get current user information

### Routes & Navigation

- `POST /api/v1/routes/calculate` - Calculate optimal route between points
- `GET /api/v1/routes/popular` - Get popular routes
- `POST /api/v1/routes/crowd-aware` - Get crowd-aware route recommendations

### Weather

- `GET /api/v1/weather/current` - Current weather conditions
- `GET /api/v1/weather/forecast` - Weather forecast
- `GET /api/v1/weather/crowd-impact` - Weather impact on crowd behavior

### Crowd Management

- `GET /api/v1/crowd/status` - Real-time crowd status across all zones
- `GET /api/v1/crowd/analytics` - Crowd analytics and trends
- `GET /api/v1/crowd/recommendations` - Crowd management recommendations
- `GET /api/v1/crowd/peak-hours` - Peak hours analysis

### Zone Management

- `GET /api/v1/zones` - List all zones with filtering options
- `GET /api/v1/zones/{zone_id}` - Get specific zone details
- `GET /api/v1/zones/search` - Search zones by name or location
- `GET /api/v1/zones/nearby` - Find zones near coordinates

### Emergency Management

- `POST /api/v1/emergency/report` - Report emergency incident
- `GET /api/v1/emergency/evacuation-routes` - Get evacuation routes
- `GET /api/v1/emergency/medical-facilities` - Find nearest medical facilities
- `GET /api/v1/emergency/contacts` - Emergency contact information
- `PUT /api/v1/emergency/{emergency_id}/resolve` - Resolve emergency (Admin only)

## 🔌 WebSocket Endpoints

### Real-time Crowd Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8000/ws/crowd-updates");

// Listen for crowd updates
ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Crowd update:", data);
};

// Send ping to keep connection alive
ws.send(JSON.stringify({ type: "ping" }));
```

### Emergency Alerts

```javascript
const emergencyWs = new WebSocket("ws://localhost:8000/ws/emergency-alerts");
```

## 🗄️ Database

The application uses SQLite database which will be automatically created as `simhasthaflow.db` in the project root directory on first run.

### Database Schema

- **Users**: Authentication and user management
- **Zones**: Temple, ghat, parking, and facility information
- **Routes**: Navigation routes and road networks
- **CrowdData**: Real-time and historical crowd density data
- **WeatherData**: Weather conditions and forecasts
- **Emergencies**: Emergency incidents and responses

### Sample Data

The database is automatically populated with realistic mock data including:

- Ujjain Mahakumbh temples and ghats (Mahakaleshwar Jyotirlinga, Ram Ghat, etc.)
- Parking areas, community kitchens, and sadhu camps
- Historical crowd patterns for religious festivals
- Weather data for different scenarios
- Road network for Shipra river area navigation

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Authenticate using admin credentials
3. Test any endpoint directly from the browser

### Using curl

```powershell
# Get access token
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"username": "admin", "password": "admin123"}'
$token = $response.access_token

# Test crowd status endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/crowd/status" -Headers @{Authorization = "Bearer $token"}

# Test route calculation
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/routes/calculate" -Method POST -ContentType "application/json" -Headers @{Authorization = "Bearer $token"} -Body '{"start": {"lat": 25.3176, "lng": 82.9739}, "end": {"lat": 25.3105, "lng": 82.9751}}'
```

## 📊 Monitoring Real-time Updates

The system automatically generates realistic crowd updates every 30 seconds when WebSocket clients are connected. This simulates:

- Time-based crowd patterns (peak hours at temples: 5-9 AM, 5-8 PM)
- Different behavior for temples, ghats, parking areas, and food courts
- Realistic crowd fluctuations based on time of day
- Emergency scenarios and their impact on crowd distribution

## 🔧 Configuration

Edit `app/core/config.py` to modify:

- Database URL
- JWT secret key and expiration
- API configuration parameters

## 📁 Project Structure

```
DHARA/
├── app/
│   ├── core/
│   │   └── config.py              # Configuration settings
│   ├── database/
│   │   ├── database.py            # Database connection
│   │   └── seed_data.py           # Mock data generation
│   ├── models/
│   │   ├── database_models.py     # SQLAlchemy models
│   │   └── schemas.py             # Pydantic schemas
│   ├── routers/
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── routes.py              # Navigation endpoints
│   │   ├── weather.py             # Weather endpoints
│   │   ├── crowd.py               # Crowd management endpoints
│   │   ├── zones.py               # Zone management endpoints
│   │   └── emergency.py           # Emergency management endpoints
│   ├── websocket/
│   │   └── crowd_updates.py       # WebSocket implementation
│   └── main.py                    # FastAPI application
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚨 Emergency Testing

The system includes comprehensive emergency management:

1. **Report Emergency**: Use the `/api/v1/emergency/report` endpoint
2. **Get Evacuation Routes**: System automatically calculates optimal evacuation paths
3. **Medical Facilities**: Locate nearest medical facilities based on emergency type
4. **Real-time Updates**: Emergency status tracking and resolution

## 🔍 Troubleshooting

### Common Issues

1. **Port 8000 already in use**:

   ```powershell
   uvicorn app.main:app --reload --port 8001
   ```

2. **Permission issues with virtual environment**:

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Module not found errors**:

   ```powershell
   # Make sure you're in the project root directory
   # and virtual environment is activated
   pip install -r requirements.txt
   ```

4. **Database issues**:
   - Delete `simhasthaflow.db` file and restart the application
   - The database will be recreated with fresh mock data

### Logs

The application logs important information to the console. Watch for:

- Database initialization messages
- WebSocket connection status
- API request logs
- Error messages

## 🎯 Use Cases

This system is designed for:

- **Crowd Management**: Real-time monitoring of pilgrims at religious sites
- **Navigation**: Helping visitors find optimal routes avoiding crowded areas
- **Emergency Response**: Quick evacuation and emergency management
- **Weather Monitoring**: Understanding weather impact on crowd behavior
- **Resource Planning**: Analyzing crowd patterns for better facility management

## 🌍 **Project Impact & Vision**

### 🎯 **Real-World Applications**

SimhasthaFlow (DHARA) represents the future of **Digital Heritage Management**, where technology serves spirituality:

#### **Immediate Impact**

- **Save Lives**: Prevent stampedes and ensure rapid emergency response
- **Enhance Experience**: Pilgrims can focus on devotion, not navigation
- **Optimize Resources**: Data-driven deployment of security and medical personnel
- **Preserve Heritage**: Protect sacred spaces while accommodating millions

#### **Broader Vision**

- **Scalable Model**: Template for managing all major religious festivals in India
- **Cultural Preservation**: Digital documentation and management of heritage sites
- **Smart Cities Integration**: Urban planning for religious tourism infrastructure
- **International Recognition**: Showcase India's technological leadership in heritage management

### 🚀 **Technology Roadmap**

#### **Phase 1: Foundation** ✅ **(Current)**

- Core API development with realistic mock data
- Real-time crowd monitoring and emergency response
- Local development environment and documentation

#### **Phase 2: Integration** 🔄 **(Next 6 months)**

- **IoT Sensor Integration**: Real crowd counting via cameras and sensors
- **Weather API Integration**: Live meteorological data from IMD
- **Mobile Application**: Native Android/iOS apps for pilgrims
- **Machine Learning**: Predictive crowd modeling and pattern recognition

#### **Phase 3: Intelligence** 🎯 **(6-12 months)**

- **AI-Powered Predictions**: Advanced crowd flow forecasting
- **Multi-language Support**: Hindi, English, Gujarati, Marathi, Sanskrit
- **Accessibility Features**: Voice navigation, visual impairment support
- **Advanced Analytics**: Heat maps, trend analysis, resource optimization

#### **Phase 4: Scale** 🌟 **(1-2 years)**

- **Multi-Festival Platform**: Kumbh Mela (Prayagraj, Nashik, Haridwar)
- **International Deployment**: Hajj, Vatican events, other religious gatherings
- **Government Integration**: National disaster management and tourism systems
- **Commercial Platform**: SaaS solution for event organizers worldwide

### 🏛️ **Cultural & Social Impact**

#### **Preserving Tradition Through Innovation**

- **Spiritual Accessibility**: Technology removes barriers to devotion
- **Heritage Documentation**: Digital preservation of rituals and practices
- **Community Building**: Connected pilgrims sharing experiences safely
- **Educational Value**: Learning platform about Indian culture and traditions

#### **Economic Benefits**

- **Tourism Growth**: Safer events attract more domestic and international visitors
- **Local Economy**: Efficient crowd management supports vendor businesses
- **Employment**: Technology jobs in heritage and tourism sector
- **Infrastructure**: Smart city development around religious centers

### 🤝 **Partnership Opportunities**

#### **Government Collaboration**

- **Ministry of Tourism**: National heritage site management
- **Ministry of Electronics & IT**: Digital India initiatives
- **State Governments**: Tourism development and infrastructure
- **Police & Emergency Services**: Public safety and crowd control

#### **Technology Partners**

- **Cloud Providers**: AWS, Azure, Google Cloud for scalability
- **IoT Companies**: Sensor networks and real-time data collection
- **Mobile Platforms**: Android, iOS native app development
- **AI/ML Partners**: Predictive analytics and intelligent automation

#### **Cultural Institutions**

- **UNESCO**: World Heritage site management systems
- **Archaeological Survey of India**: Heritage preservation technology
- **Religious Trusts**: Temple and shrine management systems
- **Universities**: Research partnerships and academic validation

## 🔮 **Future Enhancements**

### **Technical Roadmap**

- **IoT Sensor Integration**: Real crowd counting cameras and occupancy sensors
- **Machine Learning Models**: Predictive crowd pattern analysis
- **Mobile Applications**: Native iOS/Android apps for pilgrims
- **Real-time API Integration**: Live weather, traffic, and transportation data
- **Advanced Analytics Dashboard**: Administrative insights and trend analysis
- **Multi-language Support**: Hindi, English, and regional language interfaces

### **Feature Expansion**

- **Blockchain Integration**: Secure digital identity for pilgrims
- **AR/VR Experiences**: Virtual darshan and temple exploration
- **Social Features**: Pilgrim community and experience sharing
- **Payment Integration**: Digital donations and service payments
- **Transport Coordination**: Bus, train, and taxi booking integration

## 📞 **Support & Community**

### **Documentation & Resources**

- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Technical Support**: GitHub Issues and community discussions
- **Developer Guide**: Comprehensive setup and customization instructions
- **Cultural Context**: Educational content about Simhastha and Kumbh traditions

### **Contributing to the Project**

- **Open Source**: Community-driven development and improvement
- **Cultural Sensitivity**: Respectful technology that honors traditions
- **Accessibility**: Inclusive design for all devotees and visitors
- **Sustainability**: Environmentally conscious event management

---

## 🙏 **Acknowledgments**

**SimhasthaFlow (DHARA)** is built with deep respect for India's rich spiritual heritage and the millions of devotees who participate in these sacred gatherings. This project aims to serve both tradition and innovation, ensuring that technology enhances rather than replaces the profound spiritual experience of pilgrimage.

_"Technology should serve humanity, and humanity includes our deepest spiritual aspirations."_

---

**Note**: This is a demonstration system with comprehensive mock data modeling real-world scenarios. For production deployment, the system integrates with live IoT sensors, weather APIs, and real-time crowd monitoring infrastructure.
