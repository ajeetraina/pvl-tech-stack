*** Settings ***
Documentation     Battery validation tests for electric scooters
Library           OperatingSystem
Library           RequestsLibrary
Library           SerialLibrary
Library           Collections

*** Variables ***
${SCOOTER_CAN_PORT}    /dev/ttyUSB0
${BATTERY_REST_API}    http://bms-service:8080/api
${MIN_VOLTAGE}         3.2
${MAX_VOLTAGE}         4.2
${CELL_COUNT}          20

*** Test Cases ***
Battery Cell Voltage Test
    [Documentation]    Verifies all battery cells are within voltage limits
    Connect To Scooter
    ${cell_voltages}=    Get Battery Cell Voltages
    FOR    ${voltage}    IN    @{cell_voltages}
        Should Be True    ${voltage} >= ${MIN_VOLTAGE}    Cell voltage below minimum threshold
        Should Be True    ${voltage} <= ${MAX_VOLTAGE}    Cell voltage above maximum threshold
    END
    [Teardown]    Disconnect From Scooter

Battery Temperature Test
    [Documentation]    Verifies battery temperature remains within safe limits during charging
    Connect To Scooter
    Start Battery Charging
    @{temperatures}=    Create List
    FOR    ${i}    IN RANGE    10
        ${temp}=    Get Battery Temperature
        Append To List    ${temperatures}    ${temp}
        Sleep    30s
    END
    Stop Battery Charging
    ${max_temp}=    Evaluate    max($temperatures)
    Should Be True    ${max_temp} < 45.0    Battery temperature exceeded safety threshold
    [Teardown]    Disconnect From Scooter

*** Keywords ***
Connect To Scooter
    Open Serial Port    ${SCOOTER_CAN_PORT}    115200
    Sleep    2s
    ${status}=    Write Data    CONNECT\r\n
    ${response}=    Read Until    OK
    Should Contain    ${response}    OK

Disconnect From Scooter
    Write Data    DISCONNECT\r\n
    ${response}=    Read Until    OK
    Close Serial Port

Get Battery Cell Voltages
    Write Data    GET_CELL_VOLTAGES\r\n
    ${response}=    Read Until    END
    @{lines}=    Split To Lines    ${response}
    @{voltages}=    Create List
    FOR    ${line}    IN    @{lines}
        ${match}=    Get Regexp Matches    ${line}    ^CELL_(\d+):(\d+\.\d+)V$    2
        Run Keyword If    ${match}    Append To List    ${voltages}    ${match[0]}
    END
    Return From Keyword    ${voltages}

Get Battery Temperature
    Write Data    GET_BATTERY_TEMP\r\n
    ${response}=    Read Until    \r\n
    ${temp}=    Get Regexp Matches    ${response}    TEMP:(\d+\.\d+)C    1
    Return From Keyword    ${temp[0]}

Start Battery Charging
    Write Data    START_CHARGING\r\n
    ${response}=    Read Until    OK
    Should Contain    ${response}    OK

Stop Battery Charging
    Write Data    STOP_CHARGING\r\n

    ${response}=    Read Until    OK
    Should Contain    ${response}    OK
