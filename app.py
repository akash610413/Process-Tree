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
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}
.main-title {
    font-size: 46px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 5px;
}
.main-subtitle {
    font-size: 18px;
    opacity: 0.7;
    margin-bottom: 25px;
}
.section-heading {
    font-size: 28px;
    font-weight: 750;
    margin-top: 10px;
    margin-bottom: 15px;
}
.info-box {
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 12px;
}
.info-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}
.info-text {
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE / SIMULATOR CORE
# =========================================================
def reset_state():
    st.session_state.processes = {0: {"ppid": None, "step": 0}}
    st.session_state.log = []          # list of (parent_pid, child_pid, step)
    st.session_state.growth = [1]      # process count after each step
    st.session_state.next_pid = 1
    st.session_state.step_counter = 0

if "processes" not in st.session_state:
    reset_state()

def get_children(pid):
    return [p for p, d in st.session_state.processes.items() if d["ppid"] == pid]

def fork_process(parent_pid):
    """Create one child of parent_pid."""
    st.session_state.step_counter += 1
    new_pid = st.session_state.next_pid
    st.session_state.processes[new_pid] = {
        "ppid": parent_pid,
        "step": st.session_state.step_counter
    }
    st.session_state.log.append((parent_pid, new_pid, st.session_state.step_counter))
    st.session_state.next_pid += 1
    st.session_state.growth.append(len(st.session_state.processes))
    return new_pid

def sequential_fork_round():
    """Every existing process forks exactly one child (one round)."""
    st.session_state.step_counter += 1
    current_pids = list(st.session_state.processes.keys())
    for pid in current_pids:
        new_pid = st.session_state.next_pid
        st.session_state.processes[new_pid] = {
            "ppid": pid,
            "step": st.session_state.step_counter
        }
        st.session_state.log.append((pid, new_pid, st.session_state.step_counter))
        st.session_state.next_pid += 1
    st.session_state.growth.append(len(st.session_state.processes))

def build_tree_graph():
    dot = Digraph()
    dot.attr(bgcolor="transparent")
    for pid, data in st.session_state.processes.items():
        dot.node(str(pid), f"P{pid}\nPPID={data['ppid']}", shape="ellipse",
                  style="filled", fillcolor="#e8f0fe")
        if data["ppid"] is not None:
            dot.edge(str(data["ppid"]), str(pid))
    return dot

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">🌳 Process Tree Visualizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Simulation of Process Creation Using Multiple fork() Calls</div>',
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
st.sidebar.header("⚙️ Controls")
mode = st.sidebar.radio("Simulation Mode", ["Sequential fork()", "Custom fork()"])

if mode == "Sequential fork()":
    n_rounds = st.sidebar.number_input("Number of fork() rounds", min_value=1, max_value=6, value=1)
    if st.sidebar.button("Run Sequential Fork Round"):
        sequential_fork_round()
    st.sidebar.caption(f"Each round: every existing process calls fork() once "
                        f"→ process count doubles (2ⁿ growth).")
else:
    pid_options = sorted(st.session_state.processes.keys())
    selected_pid = st.sidebar.selectbox("Select process to fork()", pid_options,
                                         format_func=lambda p: f"P{p}")
    if st.sidebar.button("Fork Selected Process"):
        fork_process(selected_pid)

if st.sidebar.button("🔄 Reset Simulation"):
    reset_state()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.metric("Total Processes", len(st.session_state.processes))

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🌳 Process Tree", "📋 Process Table", "📜 Fork Log",
    "📈 Growth Graph", "🔍 Process Explorer", "💻 C Code", "🎓 Viva Prep"
])

with tab1:
    st.markdown('<div class="section-heading">Process Tree</div>', unsafe_allow_html=True)
    st.graphviz_chart(build_tree_graph())

with tab2:
    st.markdown('<div class="section-heading">Process Table</div>', unsafe_allow_html=True)
    rows = []
    for pid, data in sorted(st.session_state.processes.items()):
        rows.append({
            "PID": pid,
            "PPID": data["ppid"] if data["ppid"] is not None else "-",
            "Parent": f"P{data['ppid']}" if data["ppid"] is not None else "None (root)",
            "Children": ", ".join(f"P{c}" for c in get_children(pid)) or "-",
            "Creation Step": data["step"]
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<div class="section-heading">Fork Execution Log</div>', unsafe_allow_html=True)
    if st.session_state.log:
        log_df = pd.DataFrame(st.session_state.log, columns=["Parent (PID)", "Child (PID)", "Step"])
        log_df["Event"] = log_df.apply(lambda r: f"P{r['Parent (PID)']} → P{r['Child (PID)']}", axis=1)
        st.dataframe(log_df[["Step", "Event"]], use_container_width=True, hide_index=True)
    else:
        st.info("No fork() calls executed yet.")

with tab4:
    st.markdown('<div class="section-heading">Process Growth</div>', unsafe_allow_html=True)
    growth_df = pd.DataFrame({
        "Step": list(range(len(st.session_state.growth))),
        "Process Count": st.session_state.growth
    }).set_index("Step")
    st.line_chart(growth_df)
    st.caption("For unrestricted sequential fork(): Number of Processes = 2ⁿ")

with tab5:
    st.markdown('<div class="section-heading">Process Explorer</div>', unsafe_allow_html=True)
    pid_choice = st.selectbox("Select a process", sorted(st.session_state.processes.keys()),
                               format_func=lambda p: f"P{p}", key="explorer")
    data = st.session_state.processes[pid_choice]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="info-box">
        <div class="info-title">Process P{pid_choice}</div>
        <div class="info-text">
        PID: {pid_choice}<br>
        PPID: {data['ppid'] if data['ppid'] is not None else 'None (root process)'}<br>
        Creation Step: {data['step']}
        </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        children = get_children(pid_choice)
        st.markdown(f"""
        <div class="info-box">
        <div class="info-title">Children</div>
        <div class="info-text">{', '.join(f'P{c}' for c in children) if children else 'None (leaf process)'}</div>
        </div>
        """, unsafe_allow_html=True)

with tab6:
    st.markdown('<div class="section-heading">Equivalent C Program</div>', unsafe_allow_html=True)
    st.code('''
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    printf("Parent process PID: %d\\n", getpid());

    // First fork()
    pid_t pid1 = fork();
    if (pid1 == 0) {
        printf("Child 1: PID=%d PPID=%d\\n", getpid(), getppid());
    } else {
        wait(NULL);
        // Second fork() by parent
        pid_t pid2 = fork();
        if (pid2 == 0) {
            printf("Child 2: PID=%d PPID=%d\\n", getpid(), getppid());
        } else {
            wait(NULL);
            printf("Parent finished creating children.\\n");
        }
    }
    return 0;
}
''', language="c")

with tab7:
    st.markdown('<div class="section-heading">Viva Preparation</div>', unsafe_allow_html=True)
    qa = [
        ("What is a process?", "A process is a program in execution."),
        ("What is fork()?", "fork() is a Unix/Linux system call used to create a new child process."),
        ("What is PID?", "PID (Process ID) uniquely identifies a process."),
        ("What is PPID?", "PPID (Parent Process ID) identifies the parent of a process."),
        ("What is a process tree?", "A hierarchical structure showing parent-child relationships among processes."),
        ("What happens right after fork()?", "Both parent and child continue execution from the instruction following fork()."),
        ("Why does the process count double each round?", "Because in unrestricted sequential fork(), every existing process (including children created in the same run) executes the next fork() call."),
        ("How many processes can n unrestricted fork() calls create?", "Maximum 2ⁿ processes."),
        ("Does this Streamlit app create real OS processes?", "No, it simulates fork() behavior for visualization; the C code shows the real syscall."),
    ]
    for q, a in qa:
        with st.expander(q):
            st.write(a)