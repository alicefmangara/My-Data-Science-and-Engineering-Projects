import "influxdata/influxdb/monitor"
import "influxdata/influxdb/v1"

data =
    from(bucket: "tp2")
        |> range(start: -30s)
        |> filter(fn: (r) => r["_measurement"] == "air_quality")
        |> filter(fn: (r) => r["_field"] == "aqy")
        |> aggregateWindow(every: 30s, fn: mean, createEmpty: false)

option task = {name: "AirQuality", every: 30s, offset: 5s}

check = {_check_id: "0c3fd2257237b000", _check_name: "AirQuality", _type: "threshold", tags: {}}
crit = (r) => r["aqy"] > 151.0
ok = (r) => r["aqy"] < 50.0 and r["aqy"] > 0.0
info = (r) => r["aqy"] < 101.0 and r["aqy"] > 51.0
warn = (r) => r["aqy"] > 100.0
messageFn = (r) => "Check: ${r._check_name } is: ${ r._level }"

data
    |> v1["fieldsAsCols"]()
    |> monitor["check"](
        data: check,
        messageFn: messageFn,
        crit: crit,
        ok: ok,
        info: info,
        warn: warn,
    )
