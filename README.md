# Example MLflow on k8s project
1. 使用minikube
安装minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

k8s版本v1.23.0
kubectl版本v1.23.0

启动minikube
minikube delete --all && \
minikube start --driver=docker --force \
--cache-images=true \
--insecure-registry='192.168.0.66:5001' \
--image-mirror-country='cn' \
--image-repository='registry.cn-hangzhou.aliyuncs.com/google_containers' \
--base-image='registry.cn-hangzhou.aliyuncs.com/google_containers/kicbase:v0.0.36' \
--registry-mirror=https://j128dokn.mirror.aliyuncs.com \
--kubernetes-version v1.23.0 \
--listen-address=0.0.0.0 \
--memory 8192 \
--apiserver-ips=192.168.0.66 && eval $(minikube docker-env)

在windows环境下启动minikube
minikube start --driver=docker --force --image-mirror-country=cn --image-repository=registry.cn-hangzhou.aliyuncs.com/google_containers --iso-url=https://kubernetes.oss-cn-hangzhou.aliyuncs.com/minikube/iso/minikube-v1.25.0.iso --registry-mirror=https://reg-mirror.qiniu.com --no-vtx-check --kubernetes-version v1.23.0

2. 搭建私有docker registry
构建私有docker仓库，用于集群访问
docker run -d -p 0.0.0.0:5001:5001 \
--restart=always \
--name registry registry:latest

docker run \
  	-d \
  	-e ENV_DOCKER_REGISTRY_HOST=192.168.0.66 \
  	-e ENV_DOCKER_REGISTRY_PORT=5001 \
  	-p 9011:80 \
	--name registry-view \
  	konradkleine/docker-registry-frontend:v2

3. 搭建私有git仓库，用于代码持续集成
docker run -d --name=gogs-server \
-p 10022:22 -p 10086:3000 \
-v /data/gogs:/data/gogs \
--restart=always \
gogs/gogs:latest


4. 在k8s环境中执行mlflow project
mlflow run mlflow-on-k8s -b kubernetes \
-c mlflow-on-k8s/kubernetes_config.json \
-P alpha=0.5


5. 使用postgresql数据存储和实时数据库
postgresql版本: v15
timescaledb

6. 使用devpi作为pip内部镜像  
docker run -d --name devpi-hub \
-p 7104:7104 \
--env DEVPISERVER_HOST=0.0.0.0 \
--env DEVPISERVER_PORT=7104 \
--env DEVPISERVER_ROOT_PASSWORD=devpiadmin \
--env DEVPISERVER_USER=devpiadmin \
--env DEVPISERVER_PASSWORD=devpiadmin \
--env DEVPISERVER_MIRROR_INDEX=pypi \
--env DEVPISERVER_LIB_INDEX=devpi \
--env SOURCE_MIRROR_URL=https://mirrors.aliyun.com/pypi/simple/ \
--restart always \
--volume docker-python-devpi-volume:/var/lib/devpi \
lowinli98/devpi:v0.1

7. traefit使用
在minikube中使用端口映射暴露服务访问dashboard
minikube service traefik --url
http://127.0.0.1:43627
http://127.0.0.1:38917
http://127.0.0.1:41409
http://127.0.0.1:43627/dashboard/#/


8. 使用iotdb
docker run --name iotdb \
-p 6667:6667 \
-v iotdb-data:/iotdb/data \
-v iotdb-logs:/iotdb/logs \
-d apache/iotdb:latest

9. 在wsl2开启systemctl
sudo apt-get install daemonize
sudo daemonize /usr/bin/unshare --fork --pid --mount-proc /lib/systemd/systemd --system-unit=basic.target
exec sudo nsenter -t $(pidof systemd) -a su - $LOGNAME

10. 在wsl中添加网卡
sudo ifconfig eth0:1 192.168.49.2 up
sudo ifconfig eth0:1 down

11. 使用kind构建集群
kind create cluster --image kindest/node:v1.25.2 --config /root/traefik-demo/kind-cluster-config.yaml

kubectl version: v1.25.2

启动dashboard
kubectl apply -f /root/recommended.yaml
kubectl apply -f /root/traefik-demo/create-service-account.yaml
kubectl apply -f /root/traefik-demo/create-ClusterRoleBinding.yaml
kubectl proxy
dashboard地址
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
获取登录token
kubectl -n kubernetes-dashboard create token admin-user