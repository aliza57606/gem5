import m5
from m5.objects import *

# --------------------------------------------------
# Experiment Settings
# --------------------------------------------------

NUM_CPUS = 2
NUM_DAXPY_THREADS = 2

BINARY = "assignment6_part2/daxpy_x86"

# --------------------------------------------------
# System
# --------------------------------------------------

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "2GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]

# --------------------------------------------------
# Cache Classes
# --------------------------------------------------

class L1ICache(Cache):
    size = "32KiB"
    assoc = 2

    tag_latency = 2
    data_latency = 2
    response_latency = 2

    mshrs = 4
    tgts_per_mshr = 20

    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port

    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports


class L1DCache(Cache):
    size = "32KiB"
    assoc = 2

    tag_latency = 2
    data_latency = 2
    response_latency = 2

    mshrs = 4
    tgts_per_mshr = 20

    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port

    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports


# --------------------------------------------------
# Main Memory Bus
# --------------------------------------------------

system.membus = SystemXBar()

system.system_port = system.membus.cpu_side_ports

# --------------------------------------------------
# CPUs
# --------------------------------------------------

system.cpu = [
    X86MinorCPU(cpu_id=i)
    for i in range(NUM_CPUS)
]

# --------------------------------------------------
# Connect CPUs, Caches, and Interrupt Controllers
# --------------------------------------------------

for cpu in system.cpu:

    # X86 requires an interrupt controller.
    cpu.createInterruptController()

    # Private L1 instruction cache.
    cpu.icache = L1ICache()
    cpu.icache.connectCPU(cpu)
    cpu.icache.connectBus(system.membus)

    # Private L1 data cache.
    cpu.dcache = L1DCache()
    cpu.dcache.connectCPU(cpu)
    cpu.dcache.connectBus(system.membus)

    # X86 interrupt connections.
    cpu.interrupts[0].pio = system.membus.mem_side_ports
    cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# --------------------------------------------------
# Memory Controller
# --------------------------------------------------

system.mem_ctrl = MemCtrl()

system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]

system.mem_ctrl.port = system.membus.mem_side_ports

# --------------------------------------------------
# Workload
# --------------------------------------------------

system.workload = SEWorkload.init_compatible(BINARY)

process = Process()

process.cmd = [
    BINARY,
    str(NUM_DAXPY_THREADS)
]

# gem5 SE-mode multicore setup:
# Assign the same process to every CPU.
for cpu in system.cpu:
    cpu.workload = process
    cpu.createThreads()

# --------------------------------------------------
# Root
# --------------------------------------------------

root = Root(
    full_system=False,
    system=system
)

# --------------------------------------------------
# Instantiate Simulation
# --------------------------------------------------

m5.instantiate()

print("----------------------------------------")
print("DAXPY Thread-Level Parallelism Experiment")
print("----------------------------------------")
print("CPU Model: X86MinorCPU")
print("CPU Cores:", NUM_CPUS)
print("DAXPY Threads:", NUM_DAXPY_THREADS)
print("Clock: 2GHz")
print("L1 I-cache: 32KiB")
print("L1 D-cache: 32KiB")
print("")
print("FloatSimd configuration:")
print("opLat = 6")
print("issueLat = 1")
print("----------------------------------------")

# --------------------------------------------------
# Run
# --------------------------------------------------

exit_event = m5.simulate()

print("----------------------------------------")
print(
    "Exiting @ tick",
    m5.curTick(),
    "because",
    exit_event.getCause()
)
print("----------------------------------------")