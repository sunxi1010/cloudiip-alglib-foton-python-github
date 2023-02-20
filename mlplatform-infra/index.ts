import * as k8s from "@pulumi/kubernetes";
import * as kx from "@pulumi/kubernetesx";
import * as pulumi from '@pulumi/pulumi';
import * as minio from '@pulumi/minio';
import * as postgresql from '@pulumi/postgresql';
import TraefikRoute from './TraefikRoute';


// Create minikube cluster
const config = new pulumi.Config();
const isMinikube = config.requireBoolean('isMinikube');

const appName = "mlplatform-k8s";
const appLabels = { app: appName };

const mlflowNamespace = new k8s.core.v1.Namespace('mlflow-namespace', {
    metadata: { name: 'mlflow' },
});

// install traefik
const traefik = new k8s.helm.v3.Chart('traefik', {
    chart: 'traefik',
    namespace: mlflowNamespace.metadata.name,
    fetchOpts: { repo: 'https://traefik.github.io/charts'},
    values: {
        "service": {
            "type": "NodePort"
        }
    }
})

// Create Postgres database for MLFlow
const db = new k8s.helm.v3.Chart("postgresql", {
    chart: "postgresql",
    namespace: mlflowNamespace.metadata.name,
    fetchOpts: { repo: "https://charts.bitnami.com/bitnami" },
    values: {
        "auth": {
            "postgreslPassword": "root",
            "username": "sunxi",
            "password": "123456sx",
            "database": "mlflow"
        }
    }
})

// install minio
const mlflowBucket = new k8s.helm.v3.Chart("mlflow-bucket", {
    chart: "minio",
    namespace: mlflowNamespace.metadata.name,
    fetchOpts: { repo: "https://charts.bitnami.com/bitnami" },
    values: {
        "auth": {
            "rootUser": "root",
            "rootPassword": "123456sx"
        }
    }    
})

// install mlflow
const mlflow = new k8s.helm.v3.Chart("mlflow", {
    chart: "mlflow",
    namespace: mlflowNamespace.metadata.name,
    fetchOpts: { repo: "https://community-charts.github.io/helm-charts"},
    values: {
        "backendStore": {
            "databaseMigration": true,
            "postgres": {
                "enabled": true,
                "host": "postgresql",
                "port": "5432",
                "database": "mlflow",
                "user": "sunxi",
                "password": "123456sx"
            }
        },
        "artifactRoot": {
            "s3": {
                "enabled": true,
                "bucket": "mlflow",
                "awsAccessKeyId": "icjibbSM6vICcaTF",
                "awsSecretAccessKey": "kPcqelJMs3Ma6qVnN2LY3RXMKgpzbSDf"
            }
        },
        "extraEnvVars": {
            "MLFLOW_S3_ENDPOINT_URL": "http://mlflow-bucket-minio:9000"
        },
        "serviceMonitor": {
            "enabled": true
        }
    }
});

// expose mlflow in traefik as mlflow
new TraefikRoute('mlflow', {
    prefix: 'mlflow',
    service: mlflow.getResource('v1/Service', 'mlflow', 'mlflow'),
    namespace: mlflowNamespace.metadata.name
}, {dependsOn: [mlflow]})


export const databaseName = db.getResourceProperty("v1/Service", "mlflow", "postgresql", "spec")
export const mlflowBucketURI = mlflowBucket.getResourceProperty("v1/Service", "mlflow", "mlflow-bucket-minio", "spec")
