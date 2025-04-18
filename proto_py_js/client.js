
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

// Charger le fichier .proto
const PROTO_PATH = './slam_service.proto';
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

// Charger le service à partir du fichier .proto
const pointcloudProto = grpc.loadPackageDefinition(packageDefinition).IVM.slam;

// Créer le client gRPC
const client = new pointcloudProto.SlamService('localhost:50051', grpc.credentials.createInsecure());

// Appel du service GetPointCloud (streaming)
const call = client.GetPointCloud({});

call.on('data', (pointCloud) => {
  console.log('Points reçus:');
  pointCloud.points.forEach((point) => {
    console.log(`x: ${point.x}, y: ${point.y}, z: ${point.z}`);
  });
});

call.on('end', () => {
  console.log('Fin de la transmission des points');
});

call.on('error', (err) => {
  console.error('Erreur de transmission:', err);
});

call.on('status', (status) => {
  console.log('Statut:', status);
});
