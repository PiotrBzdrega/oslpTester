from enum import StrEnum, auto

class custom_auto:
    def __get__(self, obj, objtype=None):
        return obj._name_

class OslpRequestType(StrEnum):
    startSelfTestRequest = custom_auto()
    stopSelfTestRequest = custom_auto()
    setLightRequest = custom_auto()
    getStatusRequest = custom_auto()
    resumeScheduleRequest = custom_auto()
    setEventNotificationsRequest = auto()
    setScheduleRequest = custom_auto()
    setRebootRequest = custom_auto()
    setTransitionRequest = custom_auto()

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
