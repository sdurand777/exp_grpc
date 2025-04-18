
grpc_tools_node_protoc --js_out=import_style=commonjs,binary:. \
                       --grpc_out=import_style=commonjs:. \
                       --plugin=protoc-gen-grpc=$(which grpc_tools_node_protoc_plugin) \
                       slam_service.proto
