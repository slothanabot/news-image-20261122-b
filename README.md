# news-image-20261122-b

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/slothanabot/news-image-20261122-b/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/slothanabot/news-image-20261122-b/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

The World in One Map: 34 stories from Sunday 22 November 2026 pinned to a hand-drawn world map, plus a sport and markets ticker. A pure-stdlib Python program draws a deterministic 1024x1024 PNG: a large simplified world map with 34 numbered location pins, 34 numbered story callouts below it, a masthead naming the day, and a bottom ticker of the day's sport scores and Friday market moves. No third-party libraries, no network at run time.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program writes `entry.png` (1024x1024, under 1 MiB) to `$MAKEFUN_OUTPUT_DIR`, or `/output/entry.png` when that variable is unset. Running it twice produces byte-identical output.

---

<sub>Entered on [make.fun](https://make.fun/?ref=x15bjha9&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
