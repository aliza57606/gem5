import m5
from m5.objects import *

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
# CPU
# --------------------------------------------------

system.cpu = X86MinorCPU()

# X86 requires an interrupt controller
system.cpu.createInterruptController()

# --------------------------------------------------
# L1 Instruction Cache
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


# --------------------------------------------------
# L1 Data Cache
# --------------------------------------------------

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
# Memory Bus
# --------------------------------------------------

system.membus = SystemXBar()

# --------------------------------------------------
# Connect CPU Caches
# --------------------------------------------------

system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)

# --------------------------------------------------
# Connect X86 Interrupt Controller
# --------------------------------------------------

system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# System port
system.system_port = system.membus.cpu_side_ports

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

binary = "assignment6_part2/daxpy_x86"

system.workload = SEWorkload.init_compatible(binary)

process = Process()

# "1" means run DAXPY with one software thread
process.cmd = [binary, "1"]

system.cpu.workload = process

system.cpu.createThreads()

# --------------------------------------------------
# Root
# --------------------------------------------------

root = Root(
    full_system=False,
    system=system
)

# --------------------------------------------------
# Instantiate and Run
# --------------------------------------------------

m5.instantiate()

print("----------------------------------------")
print("Beginning DAXPY simulation")
print("CPU Model: X86MinorCPU")
print("CPU Cores: 1")
print("DAXPY Threads: 1")
print("FloatSimd baseline:")
print("    opLat   = 6")
print("    issueLat = 1")
print("----------------------------------------")

exit_event = m5.simulate()

print("----------------------------------------")
print(
    "Exiting @ tick",
    m5.curTick(),
    "because",
    exit_event.getCause()
)
print("----------------------------------------")