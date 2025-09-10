"""
Weather API router for weather data and forecasts
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import random

from app.database.database import get_db
from app.models.database_models import WeatherData as DBWeatherData
from app.models.schemas import WeatherResponse, WeatherData, WeatherForecast, WeatherCondition

router = APIRouter()

def calculate_crowd_impact_score(weather: WeatherData) -> float:
    """Calculate how weather affects crowd behavior (0-10 scale)"""
    base_score = 5.0
    
    # Temperature impact
    if weather.temperature_celsius < 15 or weather.temperature_celsius > 35:
        base_score += 2  # Extreme temperatures increase crowd avoidance
    elif 20 <= weather.temperature_celsius <= 30:
        base_score -= 1  # Comfortable temperatures encourage crowds
    
    # Weather condition impact
    condition_impacts = {
        "clear": -1.5,  # Clear weather encourages crowds
        "cloudy": 0,    # Neutral
        "rainy": 3,     # Rain disperses crowds
        "stormy": 5     # Storms heavily disperse crowds
    }
    base_score += condition_impacts.get(weather.condition.value, 0)
    
    # Visibility impact
    if weather.visibility_km < 5:
        base_score += 1.5  # Poor visibility affects movement
    
    # Wind impact
    if weather.wind_speed_kmh > 25:
        base_score += 1  # Strong winds affect outdoor activities
    
    return max(0, min(10, base_score))

def generate_forecast_weather() -> List[WeatherData]:
    """Generate mock weather forecast for next 5 days"""
    forecast_data = []
    base_temp = 28.0
    
    conditions = ["clear", "clear", "cloudy", "rainy", "cloudy"]
    
    for i in range(5):
        # Simulate temperature variation
        temp_variation = random.uniform(-3, 3)
        temperature = base_temp + temp_variation
        
        # Weather condition for the day
        condition = conditions[i]
        
        # Adjust other parameters based on condition
        if condition == "rainy":
            humidity = random.uniform(80, 95)
            wind_speed = random.uniform(15, 25)
            visibility = random.uniform(3, 7)
            uv_index = random.randint(1, 3)
        elif condition == "stormy":
            humidity = random.uniform(85, 95)
            wind_speed = random.uniform(25, 40)
            visibility = random.uniform(1, 4)
            uv_index = random.randint(0, 2)
        elif condition == "cloudy":
            humidity = random.uniform(60, 80)
            wind_speed = random.uniform(8, 15)
            visibility = random.uniform(6, 9)
            uv_index = random.randint(3, 6)
        else:  # clear
            humidity = random.uniform(40, 65)
            wind_speed = random.uniform(5, 12)
            visibility = random.uniform(8, 12)
            uv_index = random.randint(6, 9)
        
        weather_data = WeatherData(
            temperature_celsius=round(temperature, 1),
            humidity_percent=round(humidity, 1),
            wind_speed_kmh=round(wind_speed, 1),
            condition=WeatherCondition(condition),
            visibility_km=round(visibility, 1),
            uv_index=uv_index,
            last_updated=datetime.utcnow()
        )
        
        forecast_data.append(weather_data)
    
    return forecast_data

@router.get("/weather", response_model=WeatherResponse)
async def get_weather(db: Session = Depends(get_db)):
    """Get current weather and forecast"""
    
    # Get latest weather data from database
    latest_weather = db.query(DBWeatherData).order_by(
        DBWeatherData.timestamp.desc()
    ).first()
    
    if not latest_weather:
        # Generate mock current weather if no data exists
        current_weather_data = WeatherData(
            temperature_celsius=28.5,
            humidity_percent=65.0,
            wind_speed_kmh=12.0,
            condition=WeatherCondition.clear,
            visibility_km=10.0,
            uv_index=6,
            last_updated=datetime.utcnow()
        )
    else:
        current_weather_data = WeatherData(
            temperature_celsius=latest_weather.temperature_celsius,
            humidity_percent=latest_weather.humidity_percent,
            wind_speed_kmh=latest_weather.wind_speed_kmh,
            condition=WeatherCondition(latest_weather.condition),
            visibility_km=latest_weather.visibility_km,
            uv_index=latest_weather.uv_index,
            last_updated=latest_weather.timestamp
        )
    
    # Generate forecast
    forecast_weather = generate_forecast_weather()
    forecast = []
    
    for i, weather_data in enumerate(forecast_weather):
        forecast_date = datetime.utcnow() + timedelta(days=i+1)
        crowd_impact = calculate_crowd_impact_score(weather_data)
        
        forecast.append(WeatherForecast(
            date=forecast_date,
            weather=weather_data,
            crowd_impact_score=crowd_impact
        ))
    
    # Generate weather alerts
    alerts = []
    current_impact = calculate_crowd_impact_score(current_weather_data)
    
    if current_weather_data.condition in [WeatherCondition.rainy, WeatherCondition.stormy]:
        alerts.append("Weather conditions may affect crowd movement and safety")
    
    if current_weather_data.temperature_celsius > 35:
        alerts.append("High temperature alert - Stay hydrated and seek shade")
    elif current_weather_data.temperature_celsius < 15:
        alerts.append("Low temperature alert - Dress warmly")
    
    if current_weather_data.wind_speed_kmh > 25:
        alerts.append("Strong wind alert - Exercise caution near water bodies")
    
    if current_weather_data.visibility_km < 5:
        alerts.append("Reduced visibility - Exercise extra caution while moving")
    
    if current_weather_data.uv_index >= 8:
        alerts.append("High UV levels - Use sun protection")
    
    return WeatherResponse(
        current=current_weather_data,
        forecast=forecast,
        alerts=alerts
    )

@router.get("/weather/current", response_model=WeatherData)
async def get_current_weather(db: Session = Depends(get_db)):
    """Get only current weather data"""
    
    latest_weather = db.query(DBWeatherData).order_by(
        DBWeatherData.timestamp.desc()
    ).first()
    
    if not latest_weather:
        # Return mock data if no database entry
        return WeatherData(
            temperature_celsius=28.5,
            humidity_percent=65.0,
            wind_speed_kmh=12.0,
            condition=WeatherCondition.clear,
            visibility_km=10.0,
            uv_index=6,
            last_updated=datetime.utcnow()
        )
    
    return WeatherData(
        temperature_celsius=latest_weather.temperature_celsius,
        humidity_percent=latest_weather.humidity_percent,
        wind_speed_kmh=latest_weather.wind_speed_kmh,
        condition=WeatherCondition(latest_weather.condition),
        visibility_km=latest_weather.visibility_km,
        uv_index=latest_weather.uv_index,
        last_updated=latest_weather.timestamp
    )

@router.get("/weather/forecast", response_model=List[WeatherForecast])
async def get_weather_forecast():
    """Get weather forecast for next 5 days"""
    
    forecast_weather = generate_forecast_weather()
    forecast = []
    
    for i, weather_data in enumerate(forecast_weather):
        forecast_date = datetime.utcnow() + timedelta(days=i+1)
        crowd_impact = calculate_crowd_impact_score(weather_data)
        
        forecast.append(WeatherForecast(
            date=forecast_date,
            weather=weather_data,
            crowd_impact_score=crowd_impact
        ))
    
    return forecast

@router.get("/weather/impact", response_model=dict)
async def get_weather_crowd_impact(db: Session = Depends(get_db)):
    """Get weather impact on crowd behavior"""
    
    latest_weather = db.query(DBWeatherData).order_by(
        DBWeatherData.timestamp.desc()
    ).first()
    
    if not latest_weather:
        current_weather_data = WeatherData(
            temperature_celsius=28.5,
            humidity_percent=65.0,
            wind_speed_kmh=12.0,
            condition=WeatherCondition.clear,
            visibility_km=10.0,
            uv_index=6,
            last_updated=datetime.utcnow()
        )
    else:
        current_weather_data = WeatherData(
            temperature_celsius=latest_weather.temperature_celsius,
            humidity_percent=latest_weather.humidity_percent,
            wind_speed_kmh=latest_weather.wind_speed_kmh,
            condition=WeatherCondition(latest_weather.condition),
            visibility_km=latest_weather.visibility_km,
            uv_index=latest_weather.uv_index,
            last_updated=latest_weather.timestamp
        )
    
    impact_score = calculate_crowd_impact_score(current_weather_data)
    
    # Determine impact level
    if impact_score >= 7:
        impact_level = "high"
        description = "Weather conditions significantly discourage crowds"
    elif impact_score >= 4:
        impact_level = "medium" 
        description = "Weather conditions moderately affect crowd behavior"
    else:
        impact_level = "low"
        description = "Weather conditions encourage outdoor activities"
    
    return {
        "impact_score": impact_score,
        "impact_level": impact_level,
        "description": description,
        "current_weather": current_weather_data,
        "recommendations": [
            "Monitor weather alerts for crowd safety",
            "Adjust crowd management strategies based on weather",
            "Ensure adequate shelter and safety measures"
        ]
    }
