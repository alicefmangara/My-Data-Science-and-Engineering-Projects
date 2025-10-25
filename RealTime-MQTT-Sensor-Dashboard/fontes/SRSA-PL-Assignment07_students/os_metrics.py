#!/usr/bin/env python3

import psutil


# % of system-wide CPU utilization - calling psutil.cpu_precent() measured in 5 seconds intervals
print('The CPU usage is: ', psutil.cpu_percent(3))

# Getting usage of virtual_memory in GB (4th field)
print('RAM Used (MB):', psutil.virtual_memory()[3]/1000000)

