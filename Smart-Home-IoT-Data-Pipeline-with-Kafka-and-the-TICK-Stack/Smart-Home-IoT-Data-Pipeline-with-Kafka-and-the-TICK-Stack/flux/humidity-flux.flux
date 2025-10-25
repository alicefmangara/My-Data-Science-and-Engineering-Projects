import "influxdata/influxdb/monitor"
import "influxdata/influxdb/v1"

data =
    from(bucket: "tp2")
        |> range(start: -30s)
        |> filter(fn: (r) => r["_measurement"] == "humidity")
        |> filter(fn: (r) => r["_field"] == "Hum")
        |> aggregateWindow(every: 30s, fn: mean, createEmpty: false)

option task = {name: "Humidity", every: 30s, offset: 5s}

check = {_check_id: "0c3fd2a471b7b000", _check_name: "Humidity", _type: "threshold", tags: {}}
crit = (r) => r["Hum"] > 70.0
warn = (r) => r["Hum"] > 60.0
ok = (r) => r["Hum"] < 59.0 and r["Hum"] > 30.0
messageFn = (r) => "Check: ${ r._check_name } is: ${ r._level }"

data
    |> v1["fieldsAsCols"]()
    |> monitor["check"](
        data: check,
        messageFn: messageFn,
        crit: crit,
        warn: warn,
        ok: ok,
    )
