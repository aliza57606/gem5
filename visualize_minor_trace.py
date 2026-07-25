import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Conceptual pipeline example showing instruction overlap.
# This is an explanatory pipeline diagram, not a direct MinorTrace reconstruction.

instructions = ["I1", "I2", "I3", "I4", "I5", "I6"]
stages = ["Fetch", "Decode", "Execute", "Commit"]

stage_offsets = {
    "Fetch": 0,
    "Decode": 1,
    "Execute": 2,
    "Commit": 3,
}

fig, ax = plt.subplots(figsize=(12, 6))

for instruction_index, instruction in enumerate(instructions):
    y = len(instructions) - 1 - instruction_index

    for stage in stages:
        cycle = instruction_index + stage_offsets[stage]

        rectangle = Rectangle(
            (cycle, y),
            width=1,
            height=0.75,
            edgecolor="black",
            linewidth=1
        )

        ax.add_patch(rectangle)

        ax.text(
            cycle + 0.5,
            y + 0.375,
            stage,
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=9
        )

# Number of displayed cycles
total_cycles = len(instructions) + len(stages) - 1

ax.set_xlim(0, total_cycles)
ax.set_ylim(-0.25, len(instructions))

ax.set_xticks(
    [cycle + 0.5 for cycle in range(total_cycles)],
    [str(cycle + 1) for cycle in range(total_cycles)]
)

ax.set_yticks(
    [index + 0.375 for index in range(len(instructions))],
    list(reversed(instructions))
)

ax.set_xlabel("Processor Cycle")
ax.set_ylabel("Instruction")
ax.set_title("Instruction-Level Parallelism Through Pipeline Overlap")

ax.grid(
    axis="x",
    linestyle="--",
    linewidth=0.6,
    alpha=0.5
)

# Add explanation under the diagram
fig.text(
    0.5,
    0.02,
    "Multiple instructions occupy different pipeline stages during the same "
    "processor cycle, demonstrating instruction-level parallelism.",
    horizontalalignment="center",
    fontsize=10
)

plt.tight_layout(rect=[0, 0.07, 1, 1])

output_file = "m5out_ilp_trace/ilp_pipeline_overlap.png"
plt.savefig(output_file, dpi=300, bbox_inches="tight")
plt.show()

print(f"Figure saved to: {output_file}")