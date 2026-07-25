from m5.objects import L2XBar

from gem5.components.cachehierarchies.classic.caches.l1dcache import (
    L1DCache,
)
from gem5.components.cachehierarchies.classic.caches.l1icache import (
    L1ICache,
)
from gem5.components.cachehierarchies.classic.caches.l2cache import (
    L2Cache,
)
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.isas import ISA


class CustomAssocCacheHierarchy(
    PrivateL1PrivateL2CacheHierarchy
):
    """
    A private L1/L2 cache hierarchy that allows
    cache associativity to be configured.
    """

    def __init__(
        self,
        l1d_size,
        l1i_size,
        l2_size,
        l1d_assoc,
        l1i_assoc,
        l2_assoc,
    ):
        super().__init__(
            l1d_size=l1d_size,
            l1i_size=l1i_size,
            l2_size=l2_size,
        )

        self._custom_l1d_assoc = l1d_assoc
        self._custom_l1i_assoc = l1i_assoc
        self._custom_l2_assoc = l2_assoc

    def incorporate_cache(self, board):
        # Connect the board's system port to the memory bus.
        board.connect_system_port(
            self.membus.cpu_side_ports
        )

        # Connect memory to the memory bus.
        for _, port in board.get_mem_ports():
            self.membus.mem_side_ports = port

        # Create one L2 bus for each processor core.
        self.l2buses = [
            L2XBar()
            for _ in range(
                board.get_processor().get_num_cores()
            )
        ]

        for i, cpu in enumerate(
            board.get_processor().get_cores()
        ):
            # Create the configurable private L2 cache.
            l2_node = self.add_root_child(
                f"l2-cache-{i}",
                L2Cache(
                    size=self._l2_size,
                    assoc=self._custom_l2_assoc,
                ),
            )

            # Create the configurable L1 instruction cache.
            l1i_node = l2_node.add_child(
                f"l1i-cache-{i}",
                L1ICache(
                    size=self._l1i_size,
                    assoc=self._custom_l1i_assoc,
                ),
            )

            # Create the configurable L1 data cache.
            l1d_node = l2_node.add_child(
                f"l1d-cache-{i}",
                L1DCache(
                    size=self._l1d_size,
                    assoc=self._custom_l1d_assoc,
                ),
            )

            # Connect L2 to its L2 bus and the memory bus.
            self.l2buses[i].mem_side_ports = (
                l2_node.cache.cpu_side
            )
            self.membus.cpu_side_ports = (
                l2_node.cache.mem_side
            )

            # Connect the L1 caches to the L2 bus.
            l1i_node.cache.mem_side = (
                self.l2buses[i].cpu_side_ports
            )
            l1d_node.cache.mem_side = (
                self.l2buses[i].cpu_side_ports
            )

            # Connect the CPU to the L1 caches.
            cpu.connect_icache(
                l1i_node.cache.cpu_side
            )
            cpu.connect_dcache(
                l1d_node.cache.cpu_side
            )

            # Connect the TLB page-table walkers.
            self._connect_table_walker(i, cpu)

            # Connect processor interrupts.
            if (
                board.get_processor().get_isa()
                == ISA.X86
            ):
                cpu.connect_interrupt(
                    self.membus.mem_side_ports,
                    self.membus.cpu_side_ports,
                )
            else:
                cpu.connect_interrupt()

        # Configure coherent I/O if required.
        if board.has_coherent_io():
            self._setup_io_cache(board)