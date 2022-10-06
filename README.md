# dcgm-stats

Alternative to `nvidia-smi`. Assumes `dcgm-exporter` is running and listening on `localhost:9400/metrics`.

Requires Python 3.8+.

Usage:
```
python -m dcgm_stats
```

Example output:
```
GPU |  GPU util |      temp. |      power |   mem util
  0 |     26.0% |        56C |    84.479W |      68.0%
  1 |     28.0% |        58C |   298.347W |      17.0%
  2 |     57.0% |        58C |    101.48W |      69.0%
  3 |     44.0% |        57C |    231.47W |      61.0%
```

To manually start dcgm-exporter:
```sh
dcgm-exporter &
```

The values are refreshed every 30 seconds, so if you want to watch it, do this:
```sh
watch -n 30 python -m dcgm_stats
```
