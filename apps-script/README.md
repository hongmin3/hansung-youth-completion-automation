# Google Apps Script automation

This directory stores the source of the three container-bound Apps Script projects used by the newcomer attendance workflow.

## Projects

| Directory | Spreadsheet | Apps Script project |
| --- | --- | --- |
| `01-attendance-webapp` | `1PKQY3wVgSpk6SqJa9dCyCAV54CIzZF03d-ePReFGwxs` | `1JPi6GfNS1UR_iWic0h9yZRr-NhEYnxAV_l-YM7_huZwVceBhnDX7m5s6` |
| `02-education-management` | `1EEIAL39SgRtO1JTe8zpZ4qDMCf_qF-bfrtxn6jfpLgg` | `1FkpwxV8uFORcOMqTO19rrMB2ifEfFAmK7aXu1pI8p5eT0_HMX-o4brJc` |
| `03-registration-reporting` | `1dBO4rhCCadxO-KVBX_Jmg4aDcV9zim_sqM95JKd4Snk` | `1ZUvqTsXt0HwODX0Byi7GYWnNa75uTJ0ViKxP2vBUYl7KyM9-VriLQjK9` |

## Original trigger inventory

- Attendance web app: no installable triggers.
- Education management: two time-driven `processPendingAttendanceTrigger` triggers and one time-driven `sendNewcomerNotificationsTrigger` trigger.
- Registration reporting: one time-driven `runRegistrationMaintenanceTrigger` trigger and one time-driven `runRegistrationReportingTrigger` trigger.

The first commit containing this directory is the pre-hardening production snapshot.
