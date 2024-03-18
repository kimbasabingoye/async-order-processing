#/bin/bash

cd $PROJECT_HOME/k8s

# Apply Kubernetes resources from the 'namespace/' directory
kubectl apply -f namespace/

# Apply Kubernetes resources from the 'code' directory
kubectl apply -f code --namespace=asyncop-project

# Apply MongoDB resources
kubectl apply -f mongo/ --namespace=asyncop-project

# Apply Redis resources
kubectl apply -f redis/ --namespace=asyncop-project

# Apply RabbitMQ resources
kubectl apply -f rabbitmq/  --namespace=asyncop-project

# Apply Celery resources
kubectl apply -f celery/  --namespace=asyncop-project

# Apply Nginx resources
kubectl apply -f nginx/  --namespace=asyncop-project

# wait
echo "Wait for deployment complete"
sleep 30

# Get the URL of the nginx-service and extract the port
URL=$(minikube service nginx-service --url -n asyncop-project)
PORT=$(echo "$URL" | cut -d ':' -f 3)

# Set up an SSH tunnel to access the service
ssh -i ~/.minikube/machines/minikube/id_rsa docker@$(minikube ip) -L *:${PORT}:0.0.0.0:${PORT}


