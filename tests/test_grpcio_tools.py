import os
import subprocess
import sys
import tempfile
import unittest

PROTO_CONTENT = """\
syntax = "proto3";

package smoketest;

message PingRequest {
  string message = 1;
}

message PingReply {
  string message = 1;
}

service PingService {
  rpc Ping (PingRequest) returns (PingReply);
}
"""


class TestGrpcioTools(unittest.TestCase):
    def test_compile_proto(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            proto_path = os.path.join(tmpdir, "ping.proto")
            with open(proto_path, "w") as f:
                f.write(PROTO_CONTENT)

            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "grpc_tools.protoc",
                    f"--proto_path={tmpdir}",
                    f"--python_out={tmpdir}",
                    f"--grpc_python_out={tmpdir}",
                    f"--pyi_out={tmpdir}",
                    "ping.proto",
                ]
            )

            pb2_path = os.path.join(tmpdir, "ping_pb2.py")
            pb2_grpc_path = os.path.join(tmpdir, "ping_pb2_grpc.py")
            pyi_path = os.path.join(tmpdir, "ping_pb2.pyi")
            self.assertTrue(os.path.exists(pb2_path))
            self.assertTrue(os.path.exists(pb2_grpc_path))
            self.assertTrue(os.path.exists(pyi_path))

            sys.path.insert(0, tmpdir)
            import ping_pb2
            import ping_pb2_grpc

            req = ping_pb2.PingRequest(message="hello")
            self.assertEqual(req.message, "hello")
            self.assertTrue(hasattr(ping_pb2_grpc, "PingServiceStub"))
            self.assertTrue(hasattr(ping_pb2_grpc, "PingServiceServicer"))
