import m5
from m5.objects import *

NUM_CPUS = 8
N = 10000

BINARY = "assignment6_part2/daxpy_worker_x86"

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "2GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]


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


system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

system.cpu = [
    X86MinorCPU(cpu_id=i)
    for i in range(NUM_CPUS)
]

for cpu in system.cpu:
    cpu.createInterruptController()

    cpu.icache = L1ICache()
    cpu.dcache = L1DCache()

    cpu.icache.connectCPU(cpu)
    cpu.dcache.connectCPU(cpu)

    cpu.icache.connectBus(system.membus)
    cpu.dcache.connectBus(system.membus)

    cpu.interrupts[0].pio = system.membus.mem_side_ports
    cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    cpu.interrupts[0].int_responder = system.membus.mem_side_ports


system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.workload = SEWorkload.init_compatible(BINARY)

chunk = N // NUM_CPUS

for i, cpu in enumerate(system.cpu):

    start = i * chunk

    if i == NUM_CPUS - 1:
        end = N
    else:
        end = start + chunk

    process = Process()

    # Each simulated process must have a unique PID
    process.pid = 100 + i

    process.cmd = [
        BINARY,
        str(start),
        str(end)
    ]

    cpu.workload = process
    cpu.createThreads()


root = Root(
    full_system=False,
    system=system
)

m5.instantiate()

print("----------------------------------------")
print("Core-Partitioned DAXPY Experiment")
print("CPU Model: X86MinorCPU")
print("CPU Cores:", NUM_CPUS)
print("Vector Size:", N)
# print("FloatSimd baseline: opLat=6, issueLat=1")
# print("FloatSimd configuration: opLat=1, issueLat=6")
print("FloatSimd configuration: opLat=3, issueLat=4")
print("----------------------------------------")

exit_event = m5.simulate()

print(
    "Exiting @ tick",
    m5.curTick(),
    "because",
    exit_event.getCause()
)