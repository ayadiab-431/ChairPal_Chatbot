from pydantic import BaseModel, Field
from typing import Optional, Dict, Union, List, Literal

class SensorData(BaseModel):
    heart_rate: Optional[float] = Field(default=None, ge=20.0, le=250.0)
    temperature: Optional[float] = Field(default=None, ge=30.0, le=45.0)
    movement: Optional[Literal["low", "medium", "active"]] = None
    mpu_status: Optional[Literal["normal", "fainting_detected"]] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: str = Field(..., min_length=1, max_length=128)
    user_name: Optional[str] = Field(default=None, max_length=120)
    sensor_data: Optional[SensorData] = None

class MessageModel(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    timestamp: Optional[str] = None

class UserModel(BaseModel):
    id: Optional[int] = None
    full_name: Optional[str] = Field(default=None, max_length=120)
    gender: Optional[str] = None

class WheelchairModel(BaseModel):
    id: Optional[int] = None
    connection_status: Optional[str] = None
    movement_mode: Optional[str] = None
    movement_status: Optional[str] = None
    speed_kmh: Optional[float] = Field(default=None, ge=0.0, le=25.0)

class LocationCoordinates(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None

class FloorModel(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

class DestinationModel(BaseModel):
    place_id: Optional[int] = None
    name: Optional[str] = None
    category: Optional[str] = None
    floor: Optional[FloorModel] = None
    coordinates: Optional[LocationCoordinates] = None

class CurrentLocationModel(BaseModel):
    floor_name: Optional[str] = None
    place_name: Optional[str] = None
    coordinates: Optional[LocationCoordinates] = None

class TripModel(BaseModel):
    active_trip: Optional[bool] = None
    trip_id: Optional[int] = None
    trip_status: Optional[str] = None
    destination: Optional[DestinationModel] = None
    current_location: Optional[CurrentLocationModel] = None

class HealthMetricModel(BaseModel):
    value: Optional[float] = None
    status: Optional[str] = None

class MpuMonitoringModel(BaseModel):
    abnormal_posture_detected: Optional[bool] = None
    fall_risk_detected: Optional[bool] = None
    sudden_motion_detected: Optional[bool] = None

class HealthModel(BaseModel):
    overall_health_state: Optional[str] = None
    heart_rate: Optional[HealthMetricModel] = None
    temperature: Optional[HealthMetricModel] = None
    mpu_monitoring: Optional[MpuMonitoringModel] = None
    recommendation: Optional[str] = None
    reason: Optional[str] = None

class ObstacleDetectionModel(BaseModel):
    obstacle_detected: Optional[bool] = None
    obstacle_distance_cm: Optional[float] = Field(default=None, ge=0.0, le=1000.0)

class StairsDetectionModel(BaseModel):
    stairs_detected: Optional[bool] = None

class NavigationEnvironmentModel(BaseModel):
    obstacle_detection: Optional[ObstacleDetectionModel] = None
    stairs_detection: Optional[StairsDetectionModel] = None

class EmergencyModel(BaseModel):
    active: Optional[bool] = None
    emergency_type: Optional[str] = None
    severity: Optional[str] = None
    emergency_message: Optional[str] = None
    auto_stop_triggered: Optional[bool] = None

class CaregiverModel(BaseModel):
    caregiver_id: Optional[int] = None
    name: Optional[str] = None
    connected: Optional[bool] = None
    permissions: Optional[Dict[str, bool]] = None

class LastAiEventModel(BaseModel):
    event_type: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[str] = None

class RichChatRequest(BaseModel):
    message: MessageModel
    user: Optional[UserModel] = None
    wheelchair: Optional[WheelchairModel] = None
    trip: Optional[TripModel] = None
    health: Optional[HealthModel] = None
    navigation_environment: Optional[NavigationEnvironmentModel] = None
    emergency: Optional[EmergencyModel] = None
    caregivers: Optional[List[CaregiverModel]] = None
    last_ai_event: Optional[LastAiEventModel] = None
