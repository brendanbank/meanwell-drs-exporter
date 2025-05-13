# PoC Prometheus exporter for the Meanwell DRS series

This is a proof of concept exporter based on the work Douglas Alden has done see https://github.com/CW3E/meanwell_modbus

To get the data from the Meanwell DRS (modbus version **not** the canbus version) you need to connect the DRS comms port 
to a USB to RS485 Converter (I pick [this one](https://www.amazon.com/Industrial-USB-RS485-Converter-Communication/dp/B081MB6PN2/ref=sr_1_3?crid=T1VCT52IO7YR&dib=eyJ2IjoiMSJ9.ue7ugxs7cv9FsPAs5BkL_HNUPyzndGUl1Sm5OmcjJEDY1-N-0l1tU0Fg9N4ZQtmhT0DDsjlaiaRnfCUt4V7dn3yG45IpUWxe0gWmVFnKOi0iAp2_btl_5SA5T10MWyPVz_RRuZkVL8G4uLQ0IsBq375X3QjavMUR31WCfMhmLZqM0ex0BBsRxpCxyVhIMop-MTC2eQdwoX0AkfDffZmO9ehdhm1x6xh-f15uI1g01cs.KJjZxG-rkSWEoYdd14MkollIT3nyOAVmlj5_uGhtsq4&dib_tag=se&keywords=Industrial+USB+to+RS485+Converter&qid=1747157820&sprefix=industrial+usb+to+rs485+converter%2Caps%2C164&sr=8-3) up from amazon for €15) and connect it to the usb port of you linux host. 

Start the script fetch http://localhost:9534/metrics 
  
    # HELP drs_chargeFULLM Fully charged mode status: 0: 'NOT fully charged', 1: 'Fully charged'
    # TYPE drs_chargeFULLM gauge
    drs_chargeFULLM 1.0
    # HELP drs_chargeCCM Constant current mode status, 0: 'The charger NOT in constant current mode', 1: 'The charger in constant current mode'
    # TYPE drs_chargeCCM gauge
    drs_chargeCCM 0.0
    # HELP drs_chargeCVM Constant voltage mode status, 0: 'The charger NOT in constant voltage mode', 1: 'The charger in constant voltage mode'
    # TYPE drs_chargeCVM gauge
    drs_chargeCVM 0.0
    # HELP drs_chargeFVM Float mode status, 0: 'The charger NOT in float mode', 1: 'The charger in float mode'
    # TYPE drs_chargeFVM gauge
    drs_chargeFVM 1.0
    # HELP drs_chargeDCM Battery discharge mode, 0: 'Charging', 1: 'Discharging'
    # TYPE drs_chargeDCM gauge
    drs_chargeDCM 0.0
    # HELP drs_chargeBTNC Battery detection, 0: 'Battery detected', 1: 'NO battery detected'
    # TYPE drs_chargeBTNC gauge
    drs_chargeBTNC 0.0
    # HELP drs_fail_OTP Over temperature protection, 0: 'Normal internal temperature', 1: 'Abnormal internal temperature'
    # TYPE drs_fail_OTP gauge
    drs_fail_OTP 0.0
    # HELP drs_fail_OVP Output over-voltage protection, 0: 'Normal output voltage', 1: 'Abnormal output voltage'
    # TYPE drs_fail_OVP gauge
    drs_fail_OVP 0.0
    # HELP drs_fail_OLP Output over current protection, 0: 'Normal output current', 1: 'Abnormal output current'
    # TYPE drs_fail_OLP gauge
    drs_fail_OLP 0.0
    # HELP drs_fail_SHORT Short circuit protection, 0: 'Shorted circuit does not exist', 1: 'Shorted circuit protected'
    # TYPE drs_fail_SHORT gauge
    drs_fail_SHORT 0.0
    # HELP drs_fail_AC_FAIL AC abnormal flag, 0: 'Normal AC range', 1: 'Abnormal AC range'
    # TYPE drs_fail_AC_FAIL gauge
    drs_fail_AC_FAIL 0.0
    # HELP drs_fail_OP_OFF DC status, 0: 'DC turned on', 1: 'DC turned off'
    # TYPE drs_fail_OP_OFF gauge
    drs_fail_OP_OFF 0.0
    # HELP drs_fail_HI_TEMP High ambient temperature protection, 0: 'Normal ambient temperature', 1: 'Abnormal ambient temperature'
    # TYPE drs_fail_HI_TEMP gauge
    drs_fail_HI_TEMP 0.0
    # HELP drs_metric_VOUT Output voltage
    # TYPE drs_metric_VOUT gauge
    drs_metric_VOUT 55.89
    # HELP drs_metric_VIN Input voltage
    # TYPE drs_metric_VIN gauge
    drs_metric_VIN 229.5
    # HELP drs_metric_IOUT Output current
    # TYPE drs_metric_IOUT gauge
    drs_metric_IOUT 1.98
    # HELP drs_metric_VBAT Voltage of battery
    # TYPE drs_metric_VBAT gauge
    drs_metric_VBAT 55.89
    # HELP drs_metric_IBAT Charging or discharging current of battery
    # TYPE drs_metric_IBAT gauge
    drs_metric_IBAT 0.0
    # HELP drs_metric_TEMPERATURE Internal ambient temperature
    # TYPE drs_metric_TEMPERATURE gauge
    drs_metric_TEMPERATURE 37.8

For all de modbus details see the Meanwell manual [here](https://www.meanwell.com/Upload/PDF/DRS-240,480.pdf)

This will allow you to graph and alert on events.

<img width="700" alt="grafana dashboard" src="https://github.com/user-attachments/assets/97e4a68d-83b9-47db-85a3-2219414af2ec" />
