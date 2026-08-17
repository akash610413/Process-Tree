"""
Process Tree Visualizer using fork()
Operating Systems Mini Project - Streamlit Application
"""

import streamlit as st
import graphviz

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Process Tree Visualizer",
    page_icon="🌳",
    layout="wide",
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
        color: #2b2d42;
    }
    .footer {
        text-align: center;
        color: #666;
        padding-top: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# CORE LOGIC: PROCESS TREE GENERATION
# =========================================================
def generate_processes(number_of_forks: int, pattern: str):
    """
    Simulate process creation for repeated fork() calls.

    pattern = "all"    -> every currently-existing process executes each
                           fork() (the real fork() semantics: 2^n processes)
    pattern = "linear"  -> only the original process keeps forking
                           (creates n+1 processes total, a simple chain)

    Returns:
        processes: list of dicts {pid, ppid, level, fork}
        steps:     list of dicts describing what happened at each fork()
    """
    processes = [{"pid": "P0", "ppid": None, "level": 0, "fork": 0}]
    level_of = {"P0": 0}
    current_processes = ["P0"]
    pid_counter = 1
    steps = []

    for fork_number in range(1, number_of_forks + 1):
        new_processes = []

        if pattern == "all":
            forking_processes = current_processes
        else:  # "linear" — only the root process forks again
            forking_processes = ["P0"]

        for parent_pid in forking_processes:
            child_pid = f"P{pid_counter}"
            pid_counter += 1

            level_of[child_pid] = level_of[parent_pid] + 1
            processes.append(
                {
                    "pid": child_pid,
                    "ppid": parent_pid,
                    "level": level_of[child_pid],
                    "fork": fork_number,
                }
            )
            new_processes.append(child_pid)

        current_processes = current_processes + new_processes

        steps.append(
            {
                "fork": fork_number,
                "new_processes": len(new_processes),
                "total_after": len(current_processes),
            }
        )

    return processes, steps


def build_graph(processes):
    """Build a Graphviz Digraph from the simulated process list."""
    dot = graphviz.Digraph()
    dot.attr(bgcolor="transparent")
    dot.attr("node", shape="ellipse", style="filled", fontname="Helvetica")

    for p in processes:
        color = "#ffd166" if p["pid"] == "P0" else "#8ecae6"
        dot.node(p["pid"], f'{p["pid"]}\n(fork #{p["fork"]})', fillcolor=color)
        if p["ppid"] is not None:
            dot.edge(p["ppid"], p["pid"])

    return dot


# =========================================================
# SIDEBAR — SIMULATION SETTINGS
# =========================================================
st.sidebar.header("⚙️ Simulation Settings")

fork_count = st.sidebar.slider("Number of fork() calls", min_value=1, max_value=5, value=3)

pattern_label = st.sidebar.radio(
    "Fork pattern",
    options=["Every process forks (real fork() behavior)", "Only root process forks (linear chain)"],
)
pattern = "all" if pattern_label.startswith("Every") else "linear"

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **How it works**

    Each `fork()` creates a child process.
    In real fork() behavior, *every existing
    process* — parent and children alike —
    executes the next `fork()` it reaches.

    Total Processes = 2ⁿ  (for the standard pattern)
    """
)

# =========================================================
# GENERATE DATA
# =========================================================
processes, steps = generate_processes(fork_count, pattern)
expected_processes = 2 ** fork_count if pattern == "all" else fork_count + 1
total_processes = len(processes)
child_processes = total_processes - 1

# =========================================================
# HEADER
# =========================================================
st.title("🌳 Process Tree Visualizer")
st.caption("Visualizing Process Creation and Hierarchy using fork()")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Fork Calls", fork_count)
col2.metric("Total Processes", total_processes)
col3.metric("Child Processes", child_processes)
col4.metric("Expected (formula)", expected_processes)

if pattern == "all" and total_processes != expected_processes:
    st.error("Simulation mismatch — check generate_processes() logic.")

st.markdown("---")

# =========================================================
# TABS
# =========================================================
tab_tree, tab_steps, tab_code, tab_theory, tab_table = st.tabs(
    ["🌲 Process Tree", "🧮 Step-by-Step", "💻 C Program", "📖 Theory / Viva", "📋 Process Table"]
)

# ---------------------------------------------------------
# TAB 1: TREE
# ---------------------------------------------------------
with tab_tree:
    st.markdown('<div class="section-title">Process Hierarchy</div>', unsafe_allow_html=True)
    st.graphviz_chart(build_graph(processes), use_container_width=True)

    if pattern == "all":
        st.latex(r"\text{Total Processes} = 2^n")
        st.write(f"For **{fork_count} fork() calls:**")
        st.latex(rf"2^{{{fork_count}}} = {expected_processes}")
    else:
        st.latex(r"\text{Total Processes} = n + 1")
        st.write(f"For **{fork_count} fork() calls** (linear pattern): {expected_processes} processes.")

# ---------------------------------------------------------
# TAB 2: STEP BY STEP
# ---------------------------------------------------------
with tab_steps:
    st.markdown('<div class="section-title">Execution Walkthrough</div>', unsafe_allow_html=True)
    st.write("Before any fork(): **1 process** (P0)")

    for s in steps:
        st.write(
            f"**fork() call #{s['fork']}:** "
            f"{s['new_processes']} new process(es) created → "
            f"total = **{s['total_after']}** processes"
        )

    st.info(
        "Talking points for your demo:\n\n"
        "- Start with 1 fork and explain that the single parent process "
        "creates one child, so the count goes from 1 to 2.\n"
        "- Move the slider to 2 and explain that *both* existing processes "
        "now execute the second fork(), doubling the count to 4.\n"
        "- Move to 3 and explain that all 4 processes execute the third "
        "fork(), producing 8 processes.\n"
        "- Point at the tree and explain the parent-child (PID/PPID) "
        "relationships it represents."
    )

# ---------------------------------------------------------
# TAB 3: C CODE
# ---------------------------------------------------------
with tab_code:
    st.markdown('<div class="section-title">Equivalent C Program</div>', unsafe_allow_html=True)

    c_code = f"""#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {{
    int i;

    for (i = 0; i < {fork_count}; i++) {{
        pid_t pid = fork();

        if (pid < 0) {{
            perror("fork failed");
            return 1;
        }}
        // Both parent and child return from fork() here and
        // continue into the next loop iteration, so every
        // existing process executes every remaining fork().
    }}

    printf("PID: %d, Parent PID: %d\\n", getpid(), getppid());

    // Wait for children so we don't leave zombies (only meaningful
    // for direct parents, but harmless elsewhere).
    while (wait(NULL) > 0);

    return 0;
}}
"""
    st.code(c_code, language="c")
    st.caption(
        f"Compiling and running this with {fork_count} loop iterations on Linux "
        f"produces {2 ** fork_count} processes in total — matching the simulation above."
    )

# ---------------------------------------------------------
# TAB 4: THEORY
# ---------------------------------------------------------
with tab_theory:
    st.markdown('<div class="section-title">📖 What is fork()?</div>', unsafe_allow_html=True)
    st.info(
        """
`fork()` is a Unix/Linux system call used to create a new process.

The process that calls `fork()` is called the **parent process**,
and the newly created process is called the **child process**.

After a successful `fork()`, **both** the parent and the child continue
executing from the instruction immediately after the `fork()` call —
this is the key idea behind the doubling pattern.

- 1 fork → 2 processes
- 2 forks → 4 processes
- 3 forks → 8 processes
- 4 forks → 16 processes
- 5 forks → 32 processes

`fork()` returns:
- `0` in the child process
- the child's PID in the parent process
- a negative value if fork() fails

This produces a binary process hierarchy: **Total Processes = 2ⁿ**.
        """
    )

    st.markdown('<div class="section-title">⚠️ Important note</div>', unsafe_allow_html=True)
    st.warning(
        """
This Streamlit application **simulates and visualizes** process creation —
it does not call the real `fork()` system call, because `fork()` is
Unix/Linux-specific and is not available the same way on Windows.

The actual OS behavior is demonstrated by the equivalent C program shown
in the "C Program" tab. If asked in a viva:

> "The Streamlit application simulates the process creation and hierarchy.
> The actual fork() behavior is demonstrated through the corresponding C
> program, while the Python application provides a safe, visual
> representation of the parent-child relationships."
        """
    )

    st.markdown('<div class="section-title">Likely viva questions</div>', unsafe_allow_html=True)
    st.markdown(
        """
- **Q: What does fork() return to the parent vs the child?**
  The child's PID to the parent, and 0 to the child.
- **Q: What is a PPID?**
  The Parent Process ID — identifies which process created a given process.
- **Q: Why do we see 2ⁿ and not n+1 processes?**
  Because every existing process (not just the original) executes each
  subsequent fork() call — this is why the "every process forks" pattern
  in the sidebar doubles the count each time, unlike the linear pattern.
- **Q: What is a zombie process, and why do we call wait()?**
  A child that has finished but whose exit status hasn't been read by
  the parent yet; `wait()` reaps it and frees its process table entry.
        """
    )

# ---------------------------------------------------------
# TAB 5: PROCESS TABLE
# ---------------------------------------------------------
with tab_table:
    st.markdown('<div class="section-title">Raw Process List (PID / PPID)</div>', unsafe_allow_html=True)
    st.dataframe(
        [{"PID": p["pid"], "PPID": p["ppid"] or "—", "Level": p["level"], "Created at fork #": p["fork"]} for p in processes],
        use_container_width=True,
        hide_index=True,
    )

    report_lines = [
        "Process Tree Visualizer — Report",
        f"Pattern: {pattern_label}",
        f"Fork calls: {fork_count}",
        f"Total processes: {total_processes}",
        "",
        "PID | PPID | Level | Created at fork #",
    ]
    for p in processes:
        report_lines.append(f"{p['pid']} | {p['ppid'] or '-'} | {p['level']} | {p['fork']}")

    st.download_button(
        "📥 Download report (.txt)",
        data="\n".join(report_lines),
        file_name="process_tree_report.txt",
        mime="text/plain",
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    """
    <div class="footer">
        <b>Operating Systems Mini Project</b><br>
        Process Tree Visualizer using fork()
    </div>
    """,
    unsafe_allow_html=True,
)