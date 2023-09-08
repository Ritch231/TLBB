# TLBB

```bash
docker pull ritch231/tlbb:v02
docker run -d -v /root/tlbb/app:/workfolder/app -e TZ=Asia/Shanghai --restart=always --name tlbb2 ritch231/tlbb:v02
```