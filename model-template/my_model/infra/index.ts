import * as k8s from "@pulumi/kubernetes";
import * as kx from "@pulumi/kubernetesx";
import * as pulumi from "@pulumi/pulumi";
import * as docker from "@pulumi/docker";

const config = new pulumi.Config()
const baseStack = new pulumi.StackReference(config.require("baseStackName"))
const dockerHub = "localhost:5000"

// connect to the kubernetes we created in mlplatform-infra
const provider = new k8s.Provider('provider', {
    kubeconfig: baseStack.requireOutput('kubeconfig'),
})

const image = new docker.Image("my-model-image", {
    build: "../",
    imageName: "localhost:5000/myapp",
    registry: {
        server: "localhost:5000",
        username: "sunxi1010",
        password: "123456sx"
    },
})

// const podBuilder = new kx.PodBuilder({
//     containers: [{
//         image: image.imageName,
//         ports: { http: 80},
//         env: {
//             'LISTEN_PORT': '80',
//             'MLFLOW_TRACKING_URI': 'http://traefik.localhost',
//             'MLFLOW_RUN_ID': config.require('runID'),
//         }
//     }]
// })

const appLabels = { app: "my-model-serving"}
const deployment = new k8s.apps.v1.Deployment('my-model-serving', {
    metadata: {
        labels: appLabels,
        namespace: "mlflow",
    },
    spec: {
        selector: {
            matchLabels: appLabels
        },
        replicas: 1,
        template: {
            metadata: { labels: appLabels },
            spec: {
                containers: [
                    {
                        name: "mlapi",
                        image: image.imageName,
                        ports: [
                            {
                                name: "http",
                                containerPort: 80
                            }
                        ],
                        env: [
                            { name: "LISTEN_PORT", value: "80"},
                            { name: 'MLFLOW_TRACKING_URI', value: 'http://mlflow:5000'},
                            { name: 'MLFLOW_RUN_ID', value: config.require('runID')}
                        ]
                    }
                ]
            }
        }
    }
})

const service = new k8s.core.v1.Service('my-model-serving',{
    metadata: {
        labels: deployment.spec.template.metadata.labels,
        namespace: "mlflow"
    },
    spec: {
        ports: [
            {
                port: 8880,
                targetPort: 80
            }
        ],
        selector: appLabels
    }
})

// export const imageName = image.imageName
