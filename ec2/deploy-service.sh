#/bin/bash

cd $PROJECT_HOME/k8s

NAME_SPACE='asyncop-project'

# Apply Kubernetes resources from the 'namespace/' directory
kubectl apply -f namespace/

# Apply Kubernetes resources from the 'code' directory
kubectl apply -f code --namespace=$NAME_SPACE

# Apply MongoDB resources
kubectl apply -f mongo/ --namespace=$NAME_SPACE

# Apply Redis resources
kubectl apply -f redis/ --namespace=$NAME_SPACE

# Apply RabbitMQ resources
kubectl apply -f rabbitmq/  --namespace=$NAME_SPACE

# Apply Celery resources
kubectl apply -f celery/  --namespace=$NAME_SPACE

# Apply Nginx resources
kubectl apply -f nginx/  --namespace=$NAME_SPACE

# wait
echo "Wait for deployment complete"
sleep 30

# Get the URL of the nginx-service and extract the port
URL=$(minikube service nginx-service --url -n asyncop-project)
PORT=$(echo "$URL" | cut -d ':' -f 3)

kubectl port-forward --address 0.0.0.0 services/nginx-service ${PORT}:80

# Set up an SSH tunnel to access the service
ssh -i ~/.minikube/machines/minikube/id_rsa docker@$(minikube ip) -L *:${PORT}:0.0.0.0:${PORT}


