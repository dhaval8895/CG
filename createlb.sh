export BACKEND_PORT=30033

echo "Creating firewall rules..."
gcloud compute firewall-rules create gke-dashboard-cluster-lb7-fw --target-tags dashboard-cluster-node --allow "tcp:${BACKEND_PORT}" --source-ranges 130.211.0.0/22,35.191.0.0/16

echo "Creating health checks..."
gcloud compute health-checks create http dashboard-cluster-basic-check --port $BACKEND_PORT --healthy-threshold 1 --unhealthy-threshold 10 --check-interval 60 --timeout 60

echo "Creating an instance group..."
export INSTANCE_GROUP=$(gcloud container clusters describe dashboard-cluster-cluster --format="value(instanceGroupUrls)" | awk -F/ '{print $NF}')

echo "Creating named ports..."
gcloud compute instance-groups managed set-named-ports $INSTANCE_GROUP --named-ports "port${BACKEND_PORT}:${BACKEND_PORT}"

echo "Creating the backend service..."
gcloud compute backend-services create dashboard-cluster-service --protocol HTTP --health-checks dashboard-cluster-basic-check --port-name "port${BACKEND_PORT}" --global

echo "Connecting instance group to backend service..."
export INSTANCE_GROUP_ZONE=$(gcloud config get-value compute/zone)
gcloud compute backend-services add-backend dashboard-cluster-service --instance-group $INSTANCE_GROUP --instance-group-zone $INSTANCE_GROUP_ZONE --global

echo "Creating URL map..."
gcloud compute url-maps create dashboard-cluster-urlmap --default-service dashboard-cluster-service

echo "Uploading SSL certificates..."
gcloud compute ssl-certificates create dashboard-cluster-ssl-cert --certificate /tmp/dashboard-cluster-ssl/ssl.crt --private-key /tmp/dashboard-cluster-ssl/ssl.key

echo "Creating HTTPS target proxy..."
gcloud compute target-https-proxies create dashboard-cluster-https-proxy --url-map dashboard-cluster-urlmap --ssl-certificates dashboard-cluster-ssl-cert

echo "Creating global forwarding rule..."
gcloud compute forwarding-rules create dashboard-cluster-gfr --address $STATIC_IP --global --target-https-proxy dashboard-cluster-https-proxy --ports 443
