import argparse
from pathlib import Path

from m5.objects import (
    BranchPredictor,
    LocalBP,
    TournamentBP,
)
from m5.objects.X86CPU import X86MinorCPU

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import (
    PrivateL1CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator


parser = argparse.ArgumentParser()
parser.add_argument(
    "--predictor",
    choices=["local", "tournament"],
    required=True,
    help="Conditional branch predictor to use",
)
args = parser.parse_args()


binary_path = (
    Path(__file__).resolve().parent
    / "workloads"
    / "branch_test"
)

if not binary_path.exists():
    raise FileNotFoundError(
        f"Cannot find executable: {binary_path}"
    )


if args.predictor == "local":
    conditional_predictor = LocalBP()
else:
    conditional_predictor = TournamentBP()


cpu = X86MinorCPU()

cpu.branchPred = BranchPredictor(
    conditionalBranchPred=conditional_predictor
)

print("Outer predictor:", type(cpu.branchPred).__name__)
print(
    "Conditional predictor:",
    type(cpu.branchPred.conditionalBranchPred).__name__,
)

core = BaseCPUCore(
    core=cpu,
    isa=ISA.X86,
)

processor = BaseCPUProcessor(
    cores=[core]
)

cache_hierarchy = PrivateL1CacheHierarchy(
    l1d_size="16KiB",
    l1i_size="16KiB",
)

memory = SingleChannelDDR3_1600(
    size="512MiB"
)

board = SimpleBoard(
    clk_freq="1GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

board.set_se_binary_workload(
    BinaryResource(
        local_path=str(binary_path)
    )
)

print(f"Beginning simulation with {args.predictor} predictor.")

simulator = Simulator(board=board)
simulator.run()

print("Simulation completed.")