licenses(["notice"])  # Apache 2.0

package(default_visibility = ["//visibility:public"])

cc_binary(
    name = "_gcs_config_ops.so",
    srcs = [
        "gcs_config_op_kernels.cc",
        "gcs_config_ops.cc",
    ],
    copts = [
        "-pthread",
        "-std=c++11",
        "-DNDEBUG",
    ],
    linkshared = 1,
    deps = [
        "@jsoncpp_git//:jsoncpp",
        "@local_config_tf//:libtensorflow_framework",
        "@local_config_tf//:tf_header_lib",
    ],
)
