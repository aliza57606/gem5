import time

import torch

MATRIX_SIZE = 2048
REPEATS = 5


def synchronize(device: torch.device) -> None:
    if device.type == "mps":
        torch.mps.synchronize()


def benchmark(
    a: torch.Tensor,
    b: torch.Tensor,
    device: torch.device,
) -> tuple[float, torch.Tensor]:
    device_a = a.to(device)
    device_b = b.to(device)

    # Warm-up run
    result = torch.matmul(device_a, device_b)
    synchronize(device)

    times = []

    for _ in range(REPEATS):
        start = time.perf_counter()

        result = torch.matmul(device_a, device_b)

        synchronize(device)
        end = time.perf_counter()

        times.append((end - start) * 1000)

    average_time = sum(times) / len(times)
    return average_time, result


def main() -> None:
    torch.manual_seed(42)

    # Create the inputs once so CPU and GPU use identical matrices.
    matrix_a = torch.rand(MATRIX_SIZE, MATRIX_SIZE)
    matrix_b = torch.rand(MATRIX_SIZE, MATRIX_SIZE)   

    cpu_device = torch.device("cpu")
    gpu_device = torch.device("mps")

    cpu_time, cpu_result = benchmark(
        matrix_a,
        matrix_b,
        cpu_device,
    )

    gpu_time, gpu_result = benchmark(
        matrix_a,
        matrix_b,
        gpu_device,
    )

    # Small floating-point differences are expected between devices.
    results_match = torch.allclose(
        cpu_result,
        gpu_result.cpu(),
        rtol=1e-3,
        atol=1e-3,
    )

    speedup = cpu_time / gpu_time

    print(f"PyTorch version: {torch.__version__}")
    print(f"Matrix size: {MATRIX_SIZE} x {MATRIX_SIZE}")
    print(f"Repetitions: {REPEATS}")
    print(f"CPU average time: {cpu_time:.2f} ms")
    print(f"GPU average time: {gpu_time:.2f} ms")
    print(f"GPU speedup: {speedup:.2f}x")
    print(f"Results match: {results_match}")


if __name__ == "__main__":
    main()