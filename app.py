import streamlit as st
import pandas as pd
from graphviz import Digraph


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Process Tree Visualizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS  (upgraded theme, cards, badges, buttons)
# =========================================================

st.markdown("""
<style>

:root {
    --accent: #4C6EF5;
    --accent-soft: rgba(76, 110, 245, 0.12);
    --success: #12B886;
    --warn: #F59F00;
}

.block-container {
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* Hero header */
.hero {
    padding: 28px 32px;
    border-radius: 20px;
    background: linear-gradient(135deg, var(--accent-soft), rgba(18,184,134,0.08));
    border: 1px solid rgba(76,110,245,0.18);
    margin-bottom: 22px;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 4px;
}

.main-subtitle {
    font-size: 16px;
    opacity: 0.75;
    margin-bottom: 0;
}

.badge-row {
    margin-top: 14px;
}

.badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 600;
    margin-right: 8px;
    background: rgba(76,110,245,0.14);
    color: var(--accent);
    border: 1px solid rgba(76,110,245,0.25);
}

/* Section headings */
.section-heading {
    font-size: 24px;
    font-weight: 750;
    margin-top: 6px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Info / stat cards */
.info-box {
    padding: 18px 20px;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.20);
    background: rgba(128,128,128,0.03);
    margin-bottom: 12px;
    transition: border-color 0.15s ease;
}

.info-box:hover {
    border-color: rgba(76,110,245,0.4);
}

.info-title {
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 6px;
    opacity: 0.65;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

.info-text {
    opacity: 0.9;
    line-height: 1.7;
    font-size: 15px;
}

.info-text b {
    color: var(--accent);
}

/* Stat pill cards for sidebar-style metrics */
.stat-card {
    padding: 16px;
    border-radius: 14px;
    background: rgba(76,110,245,0.08);
    border: 1px solid rgba(76,110,245,0.18);
    text-align: center;
}

.stat-number {
    font-size: 30px;
    font-weight: 800;
    color: var(--accent);
    line-height: 1;
}

.stat-label {
    font-size: 12.5px;
    opacity: 0.65;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Legend swatches */
.legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-right: 18px;
    font-size: 13.5px;
    opacity: 0.85;
}

.legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
}

/* Sidebar tweaks */
section[data-testid="stSidebar"] .stButton button {
    border-radius: 10px;
    font-weight: 600;
}

/* Footer */
.footer-box {
    text-align: center;
    opacity: 0.55;
    padding: 20px;
    font-size: 13.5px;
    border-top: 1px solid rgba(128,128,128,0.15);
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# COLOR PALETTE (used for depth-based tree coloring)
# =========================================================

DEPTH_COLORS = [
    "#d9ead3",  # root - green
    "#cfe2ff",  # depth 1 - blue
    "#ffe8cc",  # depth 2 - orange
    "#f3d9fa",  # depth 3 - purple
    "#ffd8d8",  # depth 4 - red
    "#d0f5e8",  # depth 5 - teal
]


def color_for_depth(depth):
    return DEPTH_COLORS[depth % len(DEPTH_COLORS)]


# =========================================================
# SESSION STATE / SIMULATOR CORE
# =========================================================

def reset_state():
    """
    Reset the entire process simulation.
    """

    st.session_state.processes = {
        0: {
            "ppid": None,
            "step": 0,
            "depth": 0
        }
    }

    st.session_state.log = []

    # Number of processes after every step.
    st.session_state.growth = [1]

    # Next PID to assign.
    st.session_state.next_pid = 1

    # Number of fork rounds/operations.
    st.session_state.step_counter = 0

    # Currently selected process in Custom mode.
    st.session_state.selected_pid = 0


# Initialize simulation
if "processes" not in st.session_state:
    reset_state()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_children(pid):
    """Return all direct children of a process."""
    return [
        process_pid
        for process_pid, data in st.session_state.processes.items()
        if data["ppid"] == pid
    ]


def max_depth():
    return max(d["depth"] for d in st.session_state.processes.values())


def fork_process(parent_pid):
    """Create exactly one child process for the selected parent (Custom mode)."""

    st.session_state.step_counter += 1

    new_pid = st.session_state.next_pid
    parent_depth = st.session_state.processes[parent_pid]["depth"]

    st.session_state.processes[new_pid] = {
        "ppid": parent_pid,
        "step": st.session_state.step_counter,
        "depth": parent_depth + 1
    }

    st.session_state.log.append((parent_pid, new_pid, st.session_state.step_counter))
    st.session_state.next_pid += 1
    st.session_state.growth.append(len(st.session_state.processes))

    return new_pid


def sequential_fork_round():
    """
    Every process that existed BEFORE the current round performs exactly
    one fork(). Newly created children do not fork in the same round.
    """

    st.session_state.step_counter += 1
    current_pids = list(st.session_state.processes.keys())

    for parent_pid in current_pids:
        new_pid = st.session_state.next_pid
        parent_depth = st.session_state.processes[parent_pid]["depth"]

        st.session_state.processes[new_pid] = {
            "ppid": parent_pid,
            "step": st.session_state.step_counter,
            "depth": parent_depth + 1
        }

        st.session_state.log.append((parent_pid, new_pid, st.session_state.step_counter))
        st.session_state.next_pid += 1

    st.session_state.growth.append(len(st.session_state.processes))


def build_tree_graph():
    """Build the Graphviz process tree with depth-based coloring."""

    dot = Digraph()
    dot.attr(bgcolor="transparent")
    dot.attr(rankdir="TB")
    dot.attr("node", fontname="Helvetica", fontsize="12")
    dot.attr("edge", color="#9AA5B1", arrowsize="0.7")

    for pid, data in st.session_state.processes.items():
        depth = data["depth"]
        fill = color_for_depth(depth)

        if pid == 0:
            label = "P0\nPID = 0\nROOT"
            penwidth = "2"
            color = "#2f9e44"
        else:
            label = f"P{pid}\nPID = {pid}\nPPID = {data['ppid']}"
            penwidth = "1"
            color = "#5c5f66"

        dot.node(
            str(pid),
            label,
            shape="ellipse",
            style="filled",
            fillcolor=fill,
            color=color,
            penwidth=penwidth
        )

        if data["ppid"] is not None:
            dot.edge(str(data["ppid"]), str(pid))

    return dot


# =========================================================
# HEADER
# =========================================================

st.markdown(
    f"""
    <div class="hero">
        <div class="main-title">🌳 Process Tree Visualizer</div>
        <div class="main-subtitle">
            Simulation of process creation and parent-child hierarchy using
            multiple <code>fork()</code> calls
        </div>
        <div class="badge-row">
            <span class="badge">Python</span>
            <span class="badge">Streamlit</span>
            <span class="badge">Graphviz</span>
            <span class="badge">Operating Systems</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP STAT ROW
# =========================================================

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(
        f"""<div class="stat-card">
            <div class="stat-number">{len(st.session_state.processes)}</div>
            <div class="stat-label">Total Processes</div>
        </div>""",
        unsafe_allow_html=True
    )

with s2:
    st.markdown(
        f"""<div class="stat-card">
            <div class="stat-number">{st.session_state.step_counter}</div>
            <div class="stat-label">Fork Rounds / Calls</div>
        </div>""",
        unsafe_allow_html=True
    )

with s3:
    leaf_count = sum(
        1 for pid in st.session_state.processes if not get_children(pid)
    )
    st.markdown(
        f"""<div class="stat-card">
            <div class="stat-number">{leaf_count}</div>
            <div class="stat-label">Leaf Processes</div>
        </div>""",
        unsafe_allow_html=True
    )

with s4:
    st.markdown(
        f"""<div class="stat-card">
            <div class="stat-number">{max_depth()}</div>
            <div class="stat-label">Tree Depth</div>
        </div>""",
        unsafe_allow_html=True
    )

st.write("")


# =========================================================
# PROJECT INTRODUCTION
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-box">
        <div class="info-title">🎯 Objective</div>
        <div class="info-text">
        Visualize process creation and understand
        <b>parent-child relationships</b> using multiple fork() calls.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <div class="info-title">🌳 Process Hierarchy</div>
        <div class="info-text">
        Every process links to its parent through
        <b>PID</b> and <b>PPID</b> relationships.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-box">
        <div class="info-title">💻 Technologies</div>
        <div class="info-text">
        <b>Python</b> · Streamlit · Graphviz · C
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("### ⚙️ Simulation Controls")

mode = st.sidebar.radio(
    "Simulation Mode",
    ["Sequential fork()", "Custom fork()"],
    help="Sequential = every process forks each round. Custom = you choose which process forks."
)

st.sidebar.markdown("---")

# ---------------------------------------------------------
# SEQUENTIAL FORK MODE
# ---------------------------------------------------------

if mode == "Sequential fork()":

    st.sidebar.caption(
        "Each round causes **every existing process** to execute "
        "fork() once → process count doubles (2ⁿ growth)."
    )

    if st.sidebar.button("▶️  Execute Next fork() Round", use_container_width=True, type="primary"):
        sequential_fork_round()
        st.toast(f"Round {st.session_state.step_counter} complete — "
                  f"{len(st.session_state.processes)} processes now exist.", icon="🌱")
        st.rerun()

# ---------------------------------------------------------
# CUSTOM FORK MODE
# ---------------------------------------------------------

else:
    pid_options = sorted(st.session_state.processes.keys())

    if ("selected_pid" not in st.session_state
            or st.session_state.selected_pid not in pid_options):
        st.session_state.selected_pid = 0

    selected_pid = st.sidebar.selectbox(
        "Select process to fork()",
        pid_options,
        index=pid_options.index(st.session_state.selected_pid),
        format_func=lambda p: f"P{p}",
        key="custom_process_selector"
    )

    st.session_state.selected_pid = selected_pid
    st.sidebar.caption(f"Currently selected process: **P{selected_pid}**")

    if st.sidebar.button("🍴 Fork Selected Process", use_container_width=True, type="primary"):
        new_pid = fork_process(selected_pid)
        st.session_state.selected_pid = selected_pid
        st.toast(f"P{selected_pid} forked → created P{new_pid}", icon="🍴")
        st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Reset Simulation", use_container_width=True):
    reset_state()
    st.toast("Simulation reset.", icon="🔄")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📊 Live Stats")
st.sidebar.metric("Total Processes", len(st.session_state.processes))
st.sidebar.metric("Fork Operations", st.session_state.step_counter)
st.sidebar.metric("Tree Depth", max_depth())


# =========================================================
# MAIN TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🌳 Process Tree",
    "📋 Process Table",
    "📜 Fork Log",
    "📈 Growth Graph",
    "🔍 Process Explorer",
    "💻 C Code",
    "🎓 Viva Prep"
])


# ---------------------------------------------------------
# TAB 1 — PROCESS TREE
# ---------------------------------------------------------

with tab1:
    st.markdown('<div class="section-heading">🌳 Process Tree</div>', unsafe_allow_html=True)
    st.info(
        "The tree shows the parent-child relationship between all currently "
        "created processes. Color indicates the generation (depth) of each process."
    )

    st.graphviz_chart(build_tree_graph(), use_container_width=True)

    # Legend
    depth_used = max_depth()
    legend_html = "".join(
        f'<span class="legend-item">'
        f'<span class="legend-dot" style="background:{color_for_depth(d)}"></span>'
        f'Depth {d}</span>'
        for d in range(depth_used + 1)
    )
    st.markdown(f'<div style="margin-top:8px;">{legend_html}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 2 — PROCESS TABLE
# ---------------------------------------------------------

with tab2:
    st.markdown('<div class="section-heading">📋 Process Table</div>', unsafe_allow_html=True)

    rows = []
    for pid, data in sorted(st.session_state.processes.items()):
        children = get_children(pid)
        rows.append({
            "Process": f"P{pid}",
            "PID": pid,
            "PPID": data["ppid"] if data["ppid"] is not None else "-",
            "Parent": f"P{data['ppid']}" if data["ppid"] is not None else "None (Root)",
            "Children": ", ".join(f"P{c}" for c in children) if children else "-",
            "Depth": data["depth"],
            "Creation Step": data["step"]
        })

    process_df = pd.DataFrame(rows)
    st.dataframe(process_df, use_container_width=True, hide_index=True)

    csv = process_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download table as CSV",
        data=csv,
        file_name="process_table.csv",
        mime="text/csv"
    )


# ---------------------------------------------------------
# TAB 3 — FORK EXECUTION LOG
# ---------------------------------------------------------

with tab3:
    st.markdown('<div class="section-heading">📜 Fork Execution Log</div>', unsafe_allow_html=True)

    if st.session_state.log:
        log_df = pd.DataFrame(
            st.session_state.log,
            columns=["Parent PID", "Child PID", "Step"]
        )
        log_df["Event"] = log_df.apply(
            lambda row: f"P{row['Parent PID']} → P{row['Child PID']}", axis=1
        )
        st.dataframe(log_df[["Step", "Event"]], use_container_width=True, hide_index=True)
    else:
        st.info("No fork() calls have been executed yet. Use the sidebar to begin.")


# ---------------------------------------------------------
# TAB 4 — PROCESS GROWTH
# ---------------------------------------------------------

with tab4:
    st.markdown('<div class="section-heading">📈 Process Growth</div>', unsafe_allow_html=True)

    growth_df = pd.DataFrame({
        "Step": list(range(len(st.session_state.growth))),
        "Process Count": st.session_state.growth
    })
    st.line_chart(growth_df.set_index("Step"))

    st.markdown("""
    <div class="info-box">
        <div class="info-title">🧮 Process Growth Formula</div>
        <div class="info-text">
            For unrestricted sequential fork() calls:
            <br><br>
            <center><b style="font-size:20px;">Number of Processes = 2ⁿ</b></center>
            <br>
            where <b>n</b> is the number of fork() rounds.
            <br><br>
            1 fork → 2 processes &nbsp;·&nbsp;
            2 forks → 4 processes &nbsp;·&nbsp;
            3 forks → 8 processes &nbsp;·&nbsp;
            4 forks → 16 processes
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 5 — PROCESS EXPLORER
# ---------------------------------------------------------

with tab5:
    st.markdown('<div class="section-heading">🔍 Process Explorer</div>', unsafe_allow_html=True)

    pid_choice = st.selectbox(
        "Select a process to inspect",
        sorted(st.session_state.processes.keys()),
        format_func=lambda p: f"P{p}",
        key="explorer"
    )

    data = st.session_state.processes[pid_choice]
    children = get_children(pid_choice)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="info-box">
                <div class="info-title">Process Information</div>
                <div class="info-text">
                    <b>Process:</b> P{pid_choice}<br><br>
                    <b>PID:</b> {pid_choice}<br><br>
                    <b>PPID:</b> {data["ppid"] if data["ppid"] is not None else "None (Root Process)"}<br><br>
                    <b>Depth:</b> {data["depth"]}<br><br>
                    <b>Creation Step:</b> {data["step"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        children_text = ", ".join(f"P{c}" for c in children) if children else "None (Leaf Process)"
        st.markdown(
            f"""
            <div class="info-box">
                <div class="info-title">Parent-Child Relationships</div>
                <div class="info-text">
                    <b>Parent:</b> {f"P{data['ppid']}" if data["ppid"] is not None else "None"}<br><br>
                    <b>Children:</b> {children_text}<br><br>
                    <b>Number of Children:</b> {len(children)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ---------------------------------------------------------
# TAB 6 — C PROGRAM
# ---------------------------------------------------------

with tab6:
    st.markdown('<div class="section-heading">💻 Equivalent C Program</div>', unsafe_allow_html=True)
    st.info(
        "This C program demonstrates actual Unix/Linux fork() process creation. "
        "The Streamlit application simulates the resulting process hierarchy."
    )

    c_program = r'''#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {

    printf("Initial Process: PID = %d\n", getpid());

    // First fork()
    pid_t pid1 = fork();

    if (pid1 < 0) {
        printf("First fork failed.\n");
        return 1;
    }

    if (pid1 == 0) {
        printf("Child 1: PID = %d, PPID = %d\n", getpid(), getppid());
    } else {
        wait(NULL);

        // Second fork() by parent
        pid_t pid2 = fork();

        if (pid2 < 0) {
            printf("Second fork failed.\n");
            return 1;
        }

        if (pid2 == 0) {
            printf("Child 2: PID = %d, PPID = %d\n", getpid(), getppid());
        } else {
            wait(NULL);
            printf("Parent finished creating children.\n");
        }
    }

    return 0;
}
'''

    st.code(c_program, language="c")


# ---------------------------------------------------------
# TAB 7 — VIVA PREP
# ---------------------------------------------------------

with tab7:
    st.markdown('<div class="section-heading">🎓 Viva Preparation</div>', unsafe_allow_html=True)

    qa = [
        ("What is a process?", "A process is a program in execution."),
        ("What is fork()?", "fork() is a Unix/Linux system call used to create a new child process."),
        ("What is PID?", "PID (Process ID) uniquely identifies a process."),
        ("What is PPID?", "PPID (Parent Process ID) identifies the parent of a process."),
        ("What is a process tree?", "A hierarchical structure showing parent-child relationships among processes."),
        ("What happens right after fork()?", "Both parent and child continue execution from the instruction following fork()."),
        ("Why does the process count double each round?", "Because in unrestricted sequential fork(), every process that exists before the round — including earlier children — executes the next fork() call."),
        ("How many processes can n unrestricted fork() calls create?", "A maximum of 2ⁿ processes."),
        ("Does this Streamlit app create real OS processes?", "No, it simulates fork() behavior for visualization; the C code panel shows the real syscall."),
    ]

    for q, a in qa:
        with st.expander(q):
            st.write(a)


# =========================================================
# FINAL PROJECT INFORMATION
# =========================================================

st.divider()
st.markdown('<div class="section-heading">📌 Project Information</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-box">
        <div class="info-title">Subject</div>
        <div class="info-text">Operating Systems</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <div class="info-title">Topic</div>
        <div class="info-text">Process Tree Using Multiple fork() Calls</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-box">
        <div class="info-title">Primary Concept</div>
        <div class="info-text">Process Creation and Hierarchy</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# KEY OBSERVATIONS
# =========================================================

st.markdown('<div class="section-heading">💡 Key Observations</div>', unsafe_allow_html=True)

observations = [
    "Every process has a unique PID.",
    "PPID identifies the parent process.",
    "Every child process is connected to its parent.",
    "Multiple fork() calls create a process hierarchy.",
    "In unrestricted sequential fork(), the number of processes doubles after every round.",
    "The process tree makes parent-child relationships easier to understand."
]

for observation in observations:
    st.write(f"🔹 {observation}")


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer-box">
        🌳 <b>Process Tree Visualizer</b><br><br>
        Operating Systems Digital Assignment<br>
        Process Creation · fork() · PID · PPID · Parent-Child Hierarchy
    </div>
    """,
    unsafe_allow_html=True
)