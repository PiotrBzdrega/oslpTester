from enum import StrEnum, auto

class OslpRequestType(StrEnum):
    startSelfTestRequest = "startSelfTestRequest"
    stopSelfTestRequest = "stopSelfTestRequest"
    setLightRequest = "setLightRequest"
    getStatusRequest = "getStatusRequest"
    resumeScheduleRequest = "resumeScheduleRequest"
    setEventNotificationsRequest = "setEventNotificationsRequest"
    setScheduleRequest = "setScheduleRequest"
    setRebootRequest = "setRebootRequest"
    setTransitionRequest = "setTransitionRequest"
    getConfigurationRequest = "getConfigurationRequest"
    setConfigurationRequest = "setConfigurationRequest"

# class OslpResponseType(StrEnum):
#     start_selftest_request = auto()
#     stop_selftest_request = auto()
#     set_light_request = auto()
#     get_status_request = auto()
#     resume_schedule_request = auto()
#     set_event_notifications_request = auto()
#     set_schedule_request = auto()
#     set_reboot_request = auto()
#     set_transition_request = auto()
