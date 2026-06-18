# scripts/transform_user_data.py
"""Convert raw health JSON payload into a RichChatRequest model."""

from typing import Any, Dict, List, Optional

# Import the Pydantic models defined in schemas.py
from schemas import (
    RichChatRequest,
    MessageModel,
    UserModel,
    WheelchairModel,
    TripModel,
    DestinationModel,
    FloorModel,
    LocationCoordinates,
    CurrentLocationModel,
    HealthModel,
    HealthMetricModel,
    MpuMonitoringModel,
    NavigationEnvironmentModel,
    ObstacleDetectionModel,
    StairsDetectionModel,
    EmergencyModel,
    CaregiverModel,
    LastAiEventModel,
)


def _safe_get(mapping: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely fetch a value from a dict, returning ``default`` if the key is missing."""
    return mapping.get(key, default)


def _build_user(user_ctx: Dict[str, Any]) -> UserModel:
    if not isinstance(user_ctx, dict):
        return None
    return UserModel(
        id=_safe_get(user_ctx, "id"),
        full_name=_safe_get(user_ctx, "name"),
        gender=_safe_get(user_ctx, "gender"),
    )


def _build_wheelchair(wc_ctx: Dict[str, Any]) -> WheelchairModel:
    if not isinstance(wc_ctx, dict):
        return None
    return WheelchairModel(
        id=_safe_get(wc_ctx, "serial_number"),
        connection_status=_safe_get(wc_ctx, "connection"),
    )


def _build_destination(dest: Dict[str, Any]) -> DestinationModel:
    if not isinstance(dest, dict):
        return None
    floor = dest.get("floor")
    return DestinationModel(
        place_id=_safe_get(dest, "place_id"),
        name=_safe_get(dest, "name"),
        category=_safe_get(dest, "category"),
        floor=FloorModel(id=_safe_get(floor, "id"), name=_safe_get(floor, "name")) if isinstance(floor, dict) else None,
        coordinates=LocationCoordinates(
            x=_safe_get(dest.get("coordinates"), "x"),
            y=_safe_get(dest.get("coordinates"), "y"),
        ) if isinstance(dest.get("coordinates"), dict) else None,
    )


def _build_current_location(loc: Dict[str, Any]) -> CurrentLocationModel:
    if not isinstance(loc, dict):
        return None
    return CurrentLocationModel(
        floor_name=_safe_get(loc, "floor_name"),
        place_name=_safe_get(loc, "place_name"),
        coordinates=LocationCoordinates(
            x=_safe_get(loc.get("coordinates"), "x"),
            y=_safe_get(loc.get("coordinates"), "y"),
        ) if isinstance(loc.get("coordinates"), dict) else None,
    )


def _build_trip(trip_ctx: Dict[str, Any]) -> TripModel:
    if not isinstance(trip_ctx, dict):
        return None
    return TripModel(
        active_trip=_safe_get(trip_ctx, "is_active"),
        trip_id=_safe_get(trip_ctx, "trip_id"),
        trip_status=_safe_get(trip_ctx, "status"),
        destination=_build_destination(_safe_get(trip_ctx, "destination", {})),
        current_location=_build_current_location(_safe_get(trip_ctx, "current_location", {})),
    )


def _build_health_metric(metric: Dict[str, Any]) -> HealthMetricModel:
    if not isinstance(metric, dict):
        return None
    return HealthMetricModel(value=_safe_get(metric, "value"), status=_safe_get(metric, "status"))


def _build_health(health_ctx: Dict[str, Any]) -> HealthModel:
    if not isinstance(health_ctx, dict):
        return None
    return HealthModel(
        overall_health_state=_safe_get(health_ctx, "overall_health_state"),
        heart_rate=_build_health_metric(_safe_get(health_ctx, "heart_rate", {})),
        temperature=_build_health_metric(_safe_get(health_ctx, "temperature", {})),
        mpu_monitoring=MpuMonitoringModel(
            abnormal_posture_detected=_safe_get(_safe_get(health_ctx, "mpu_monitoring", {}), "abnormal_posture_detected"),
            fall_risk_detected=_safe_get(_safe_get(health_ctx, "mpu_monitoring", {}), "fall_risk_detected"),
            sudden_motion_detected=_safe_get(_safe_get(health_ctx, "mpu_monitoring", {}), "sudden_motion_detected"),
        ),
        recommendation=_safe_get(health_ctx, "recommendation"),
        reason=_safe_get(health_ctx, "reason"),
    )


def _build_navigation_env(env_ctx: Dict[str, Any]) -> NavigationEnvironmentModel:
    if not isinstance(env_ctx, dict):
        return None
    return NavigationEnvironmentModel(
        obstacle_detection=ObstacleDetectionModel(
            obstacle_detected=_safe_get(_safe_get(env_ctx, "obstacle_detection", {}), "obstacle_detected"),
            obstacle_distance_cm=_safe_get(_safe_get(env_ctx, "obstacle_detection", {}), "obstacle_distance_cm"),
        ),
        stairs_detection=StairsDetectionModel(
            stairs_detected=_safe_get(_safe_get(env_ctx, "stairs_detection", {}), "stairs_detected"),
        ),
    )


def _build_emergency(em_ctx: Dict[str, Any]) -> EmergencyModel:
    if not isinstance(em_ctx, dict):
        return None
    return EmergencyModel(
        active=_safe_get(em_ctx, "active"),
        emergency_type=_safe_get(em_ctx, "emergency_type"),
        severity=_safe_get(em_ctx, "severity"),
        emergency_message=_safe_get(em_ctx, "emergency_message"),
        auto_stop_triggered=_safe_get(em_ctx, "auto_stop_triggered"),
    )


def _build_caregivers(cg_list: List[Dict[str, Any]]) -> List[CaregiverModel]:
    if not isinstance(cg_list, list):
        return []
    caregivers = []
    for cg in cg_list:
        caregivers.append(
            CaregiverModel(
                caregiver_id=_safe_get(cg, "id"),
                name=_safe_get(cg, "name"),
                connected=_safe_get(cg, "connected"),
                permissions=_safe_get(cg, "permissions"),
            )
        )
    return caregivers


def _build_last_ai_event(event: Dict[str, Any]) -> LastAiEventModel:
    if not isinstance(event, dict):
        return None
    return LastAiEventModel(
        event_type=_safe_get(event, "event_type"),
        message=_safe_get(event, "message"),
        created_at=_safe_get(event, "created_at"),
    )


def transform_to_rich_request(payload: Dict[str, Any]) -> RichChatRequest:
    """Main entry point – converts the raw backend JSON into a RichChatRequest.

    The payload structure mirrors the example you posted in the conversation
    (user_profile, relations, wheelchair_status, current_health_state,
    current_trip, latest_alerts, ...). Only the fields required by the chatbot
    are mapped; everything else is safely ignored.
    """

    # Message – the user utterance (fallback to a generic prompt if missing)
    # The client might send it as "user_text" (new schema) or "message" (legacy schema)
    message_text = _safe_get(payload, "user_text", _safe_get(payload, "message", ""))
    
    if not message_text:
        message_text = " "  # Bypass Pydantic min_length=1 validation for empty requests
    message = MessageModel(text=message_text)

    # Extract context if the JSON wraps data in a 'context' key, else use payload directly
    ctx = payload.get("context", payload)

    # Simple user info (name, id, gender)
    profile = ctx.get("user_profile", {})
    user = UserModel(
        id=_safe_get(profile, "id"),  # not present in sample – will be None
        full_name=_safe_get(profile, "name"),
        gender=_safe_get(profile, "gender"),
    )

    # Wheelchair status
    wheelchair = _build_wheelchair(ctx.get("wheelchair_status", {}))

    # Trip information
    trip = _build_trip(ctx.get("current_trip", {}))

    # Health data
    health = _build_health(ctx.get("current_health_state", {}))

    # Navigation environment (obstacle & stairs)
    navigation_env = _build_navigation_env(ctx.get("latest_alerts", {}))

    # Emergency – look for an active SOS in latest_alerts
    emergency = None
    latest_alerts = ctx.get("latest_alerts", {})
    if isinstance(latest_alerts, dict):
        sos = latest_alerts.get("sos")
        if isinstance(sos, dict):
            emergency = _build_emergency(sos)

    # Caregivers – from relations.companions (if any)
    companions = ctx.get("relations", {}).get("companions", [])
    caregivers = _build_caregivers(companions)

    # Last AI event – not present in the sample, but we keep the field optional
    last_ai_event = None

    return RichChatRequest(
        message=message,
        user=user,
        wheelchair=wheelchair,
        trip=trip,
        health=health,
        navigation_environment=navigation_env,
        emergency=emergency,
        caregivers=caregivers if caregivers else None,
        last_ai_event=last_ai_event,
    )
