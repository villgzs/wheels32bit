## Musllinux wheels (armv7l) (UTC 2026-Oct-10 22:08:18)  
### Last build from https://github.com/home-assistant/core: 2026.10.1  
  
  During the last build - armv7 - core: 104  
  Number of wheels: 2002  
- [musllinux wheels packages](https://villgzs.github.io/musllinux/)  
- [musllinux-index - Simple package repository](https://villgzs.github.io/musllinux-index/)  

2026.07.0

- Ha reprodukálható / pinelt build kell, a pontos verziót érdemes használni, pl.:
- ghcr.io/home-assistant/amd64-base-python:3.14-alpine3.24-2026.06.x (ami a 2026.júniusi release idején aktuális volt).
- https://github.com/home-assistant/wheels/actions/runs/28389244836
-   https://github.com/home-assistant/docker-base/pkgs/container/amd64-base-python/1149340342?tag=3.14-alpine3.24-2026.08.0
- docker pull ghcr.io/home-assistant/amd64-base-python:3.14-alpine3.24-2026.08.0

**A dockerbuilder a wheel gyártásakor már a legfrissebb base-alpine és base-python szinten kell legyen!** Például az av==19.0.0 csomag fordításához már ffmpeg 9 kell, ami nincs benne a 2026.05.0/2026.06.1 csomagokban.

