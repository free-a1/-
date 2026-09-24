#!/bin/bash
# FROM: 基础文件系统
rm -rf /opt/myroot-image.tar.gz
# COPY: 拷入服务代码
cat > /opt/myroot/tmp/infer_service.sh <<'INNER'
#!/bin/bash
while true; do echo "推理服务运行中 $(date +%T)"; sleep 5; done
INNER
chmod +x /opt/myroot/tmp/infer_service.sh
# CMD: 启动命令写入镜像说明
echo '启动命令: /bin/bash /tmp/infer_service.sh' > /opt/myroot/tmp/README
# 打包成镜像
tar -czf /opt/my-infer-v1.tar.gz -C /opt/myroot .
echo 镜像构建完成
