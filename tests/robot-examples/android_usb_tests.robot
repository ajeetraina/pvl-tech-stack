*** Settings ***
Documentation     Android device connectivity tests via USB/IP
Library           AppiumLibrary
Library           Process
Library           OperatingSystem

*** Variables ***
${ANDROID_AUTOMATION_NAME}    UIAutomator2
${ANDROID_PLATFORM_NAME}      Android
${ANDROID_PLATFORM_VERSION}   10.0
${ANDROID_DEVICE_NAME}        Android Emulator
${ANDROID_APP}                /tests/android/EVControlApp.apk
${ANDROID_APP_PACKAGE}        com.example.evcontrol
${ANDROID_APP_ACTIVITY}       .MainActivity

*** Test Cases ***
Connect Android Device via USB/IP
    [Documentation]    Test USB/IP connectivity to Android device
    ${result}=    Run Process    usbip    list    -r    localhost
    Log    ${result.stdout}
    Should Not Contain    ${result.stderr}    Error
    
    ${device_id}=    Get Lines Containing String    ${result.stdout}    android
    ${busid}=    Get Regexp Matches    ${device_id}    ^\s*([0-9-]*):\s    1
    Run Keyword If    ${busid}    Connect USB Device    ${busid[0]}

Install and Launch App on Android Device
    [Documentation]    Install and launch test app on connected Android device
    Open Application    http://localhost:4723/wd/hub
        ...    automationName=${ANDROID_AUTOMATION_NAME}
        ...    platformName=${ANDROID_PLATFORM_NAME}
        ...    platformVersion=${ANDROID_PLATFORM_VERSION}
        ...    deviceName=${ANDROID_DEVICE_NAME}
        ...    app=${ANDROID_APP}
        ...    appPackage=${ANDROID_APP_PACKAGE}
        ...    appActivity=${ANDROID_APP_ACTIVITY}
    
    Wait Until Page Contains Element    id=com.example.evcontrol:id/connectButton
    Click Element    id=com.example.evcontrol:id/connectButton
    
    Wait Until Page Contains Text    Connected to scooter
    Page Should Contain Text    Connected to scooter
    
    [Teardown]    Close Application

Android App Control Test
    [Documentation]    Test controlling scooter functions via Android app
    Open Application    http://localhost:4723/wd/hub
        ...    automationName=${ANDROID_AUTOMATION_NAME}
        ...    platformName=${ANDROID_PLATFORM_NAME}
        ...    platformVersion=${ANDROID_PLATFORM_VERSION}
        ...    deviceName=${ANDROID_DEVICE_NAME}
        ...    appPackage=${ANDROID_APP_PACKAGE}
        ...    appActivity=${ANDROID_APP_ACTIVITY}
    
    # Connect to scooter
    Wait Until Page Contains Element    id=com.example.evcontrol:id/connectButton
    Click Element    id=com.example.evcontrol:id/connectButton
    Wait Until Page Contains Text    Connected to scooter
    
    # Toggle lights
    Click Element    id=com.example.evcontrol:id/lightToggleButton
    Wait Until Page Contains Text    Lights ON
    
    # Check battery status
    Click Element    id=com.example.evcontrol:id/batteryStatusButton
    Wait Until Page Contains Element    id=com.example.evcontrol:id/batteryLevelText
    Element Should Contain Text    id=com.example.evcontrol:id/batteryLevelText    %
    
    # Disconnect
    Click Element    id=com.example.evcontrol:id/disconnectButton
    Wait Until Page Contains Text    Disconnected
    
    [Teardown]    Close Application

*** Keywords ***
Connect USB Device
    [Arguments]    ${busid}
    ${result}=    Run Process    usbip    attach    -r    localhost    -b    ${busid}
    Log    ${result.stdout}
    Should Not Contain    ${result.stderr}    Error
    Sleep    5s
