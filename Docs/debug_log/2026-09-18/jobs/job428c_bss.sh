#!/bin/bash
iw dev wlP1p1s0 scan dump 2>&1 | awk '/^BSS <MAC>/{p=1} /^BSS / && !/<MAC>/{p=0} p' | grep -aE 'BSS |freq|signal|SSID|last seen|HT operation|primary channel|secondary channel offset|STA channel width|VHT operation|channel width|center freq segment|HE (capabilities|operation)|Channel Switch|Power constraint|Country|DFS|Quiet|RSN|Authentication suites|Capabilities: ' | head -40
