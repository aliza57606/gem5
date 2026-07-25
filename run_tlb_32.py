from pathlib import Path

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory.single_channel import (
    SingleChannelDDR3_1600,
)
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import (
    SimpleProcessor,
)
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator


cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32KiB",
    l1i_size="32KiB",
    l2_size="256KiB",
)

memory = SingleChannelDDR3_1600(
    size="512MiB"
)

processor = SimpleProcessor(
    cpu_type=CPUTypes.TIMING,
    isa=ISA.X86,
    num_cores=1,
)

# Access the simulated CPU core.
core = processor.get_cores()[0].get_simobject()

# Configure 32-entry data and instruction TLBs.
core.mmu.dtb.size = 32
core.mmu.itb.size = 32

board = SimpleBoard(
    clk_freq="1GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

benchmark_path = (
    Path(__file__).resolve().parent
    / "cache_benchmark"
)

if not benchmark_path.exists():
    raise FileNotFoundError(
        f"Cannot find executable: {benchmark_path}"
    )

board.set_se_binary_workload(
    BinaryResource(
        local_path=str(benchmark_path)
    )
)

simulator = Simulator(board=board)

print("Beginning 32-entry TLB simulation!")
simulator.run()
print("TLB simulation completed.")