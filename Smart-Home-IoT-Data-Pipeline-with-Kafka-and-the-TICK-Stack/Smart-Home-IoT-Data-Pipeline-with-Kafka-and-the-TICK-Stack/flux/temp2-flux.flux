import "influxdata/influxdb/monitor"
import "influxdata/influxdb/v1"

data =
    from(bucket: "tp2")
        |> range(start: -1m)
        |> filter(fn: (r) => r["_measurement"] == "temperature")
        |> filter(fn: (r) => r["_field"] == "temperature2")
        |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)

option task = {name: "Temperature2", every: 1m, offset: 0s}

check = {_check_id: "0c3fd4321177b000", _check_name: "Temperature2", _type: "threshold", tags: {}}
crit = (r) => r["temperature2"] < 10.0 or r["temperature2"] > 35.0
messageFn = (r) => "Check: ${ r._check_name } is: ${ r._level }"

data |> v1["fieldsAsCols"]() |> monitor["check"](data: check, messageFn: messageFn, crit: crit)
