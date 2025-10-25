import "influxdata/influxdb/monitor"
import "influxdata/influxdb/v1"

data =
    from(bucket: "tp2")
        |> range(start: -30s)
        |> filter(fn: (r) => r["_measurement"] == "temperature")
        |> filter(fn: (r) => r["_field"] == "temperature1")
        |> aggregateWindow(every: 30s, fn: mean, createEmpty: false)

option task = {name: "Temperature", every: 30s, offset: 0s}

check = {_check_id: "0c3fd3324277b000", _check_name: "Temperature", _type: "threshold", tags: {}}
crit = (r) => r["temperature1"] < 10.0 or r["temperature1"] > 35.0
messageFn = (r) => "Check: ${ r._check_name } is: ${ r._level }"

data |> v1["fieldsAsCols"]() |> monitor["check"](data: check, messageFn: messageFn, crit: crit)
