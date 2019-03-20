# Build new Tensorflow wheels

```
./build
```

# Push the new wheels (Kaggle Engineers only)

1. Add an entry in the [CHANGELOG](CHANGELOG.md) with an appropriate `LABEL`.
2. Push the new image using the `LABEL` you picked above.

    ```
    ./push LABEL
    ```

# Use the new wheels

Update the line below in the [CPU Dockerfile](../Dockerfile) and the [GPU Dockerfile](../gpu.Dockerfile) to use the new `LABEL`.

To use wheels built locally:
```
FROM kaggle/python-tensorflow-whl as tensorflow_whl
```

To use our pre-built wheels:
```
FROM gcr.io/kaggle-images/python-tensorflow-whl:<LABEL> as tensorflow_whl
```
