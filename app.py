import streamlit as st
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

/* Main title */
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

/* Section headings */
.section-heading {
    font-size: 28px;
    font-weight: 750;
    margin-top: 10px;
    margin-bottom: 15px;
}

/* Information cards */
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
    line-height: 1.6;
}

/* Metric cards */
[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,0.25);
    padding: 15px;
    border-radius: 12px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,0.2);
}

/* Footer */
.footer {
    text-align: center;
    opacity: 0.55;
    padding: 25px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🌳 Process Tree Visualizer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Operating Systems Digital Assignment · '
    'Process Creation Using Multiple fork() Calls'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# PROJECT OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-heading">🎯 Project Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">🎯 Objective</div>

    <div class="info-text">

    To develop an interactive application that
    demonstrates process creation using multiple
    <code>fork()</code> calls and visualizes the resulting
    parent-child hierarchy.

    </div>
    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">💡 Core Concept</div>

    <div class="info-text">

    The application demonstrates process creation,
    PID, PPID, parent-child relationships and
    process-tree formation.

    </div>
    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">🛠 Technology</div>

    <div class="info-text">

    Python · Streamlit · Graphviz · C ·
    Unix/Linux Process Concepts

    </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# =========================================================
# PROBLEM STATEMENT
# =========================================================

st.markdown(
    '<div class="section-heading">📝 Problem Statement</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="info-box">

<div class="info-text">

In Operating Systems, processes can create new processes
using the <code>fork()</code> system call. When multiple
<code>fork()</code> calls are executed, the number of processes
can increase rapidly and the resulting parent-child
relationships can become difficult to understand.

This project provides an interactive visualization that
shows how processes are created and how they form a
hierarchical process tree.

</div>

</div>
""", unsafe_allow_html=True)

st.divider()


# =========================================================
# HOW SIMULATION WORKS
# =========================================================

st.markdown(
    '<div class="section-heading">⚙️ How the Simulation Works</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">01</div>

    Start with P0

    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">02</div>

    Execute fork()

    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">03</div>

    Create Child

    </div>
    """, unsafe_allow_html=True)

with col4:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">04</div>

    Update Tree

    </div>
    """, unsafe_allow_html=True)

st.divider()


# =========================================================
# PROCESS SIMULATION FUNCTIONS
# =========================================================

def copy_processes(processes):

    return [
        {
            "id": process["id"],
            "pid": process["pid"],
            "ppid": process["ppid"],
            "parent": process["parent"],
            "children": list(process["children"]),
            "created_at": process["created_at"]
        }
        for process in processes
    ]


def create_sequential_simulation(number_of_forks):

    processes = []

    # Root process
    root = {
        "id": "P0",
        "pid": 1000,
        "ppid": None,
        "parent": None,
        "children": [],
        "created_at": 0
    }

    processes.append(root)

    steps = []

    # Initial state
    steps.append(copy_processes(processes))

    next_pid = 1001
    next_process_number = 1

    # Execute each fork
    for fork_number in range(1, number_of_forks + 1):

        # Only processes existing BEFORE this fork
        # execute the current fork operation.
        existing_processes = list(processes)

        new_processes = []

        for parent in existing_processes:

            child_id = f"P{next_process_number}"

            child = {
                "id": child_id,
                "pid": next_pid,
                "ppid": parent["pid"],
                "parent": parent["id"],
                "children": [],
                "created_at": fork_number
            }

            # Add child to parent
            parent["children"].append(child_id)

            new_processes.append(child)

            next_pid += 1
            next_process_number += 1

        processes.extend(new_processes)

        # Save snapshot
        steps.append(copy_processes(processes))

    return steps


def create_custom_simulation(fork_sequence):

    processes = []

    # Root process
    root = {
        "id": "P0",
        "pid": 1000,
        "ppid": None,
        "parent": None,
        "children": [],
        "created_at": 0
    }

    processes.append(root)

    steps = []

    steps.append(copy_processes(processes))

    next_pid = 1001
    next_process_number = 1

    # Each item specifies which process performs fork()
    for fork_number, parent_id in enumerate(
        fork_sequence,
        start=1
    ):

        parent = None

        for process in processes:

            if process["id"] == parent_id:
                parent = process
                break

        # Ignore invalid process
        if parent is None:
            continue

        child_id = f"P{next_process_number}"

        child = {
            "id": child_id,
            "pid": next_pid,
            "ppid": parent["pid"],
            "parent": parent["id"],
            "children": [],
            "created_at": fork_number
        }

        parent["children"].append(child_id)

        processes.append(child)

        next_pid += 1
        next_process_number += 1

        steps.append(copy_processes(processes))

    return steps


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Simulation Settings")

mode = st.sidebar.radio(
    "Simulation Mode",
    [
        "Sequential fork()",
        "Custom fork()"
    ]
)


# =========================================================
# SEQUENTIAL MODE
# =========================================================

if mode == "Sequential fork()":

    fork_count = st.sidebar.slider(
        "Number of fork() calls",
        min_value=1,
        max_value=6,
        value=3
    )

    steps = create_sequential_simulation(
        fork_count
    )

    if (
        "last_mode" not in st.session_state
        or st.session_state.last_mode != mode
        or "last_fork_count" not in st.session_state
        or st.session_state.last_fork_count != fork_count
    ):

        st.session_state.current_step = 0

    st.session_state.last_mode = mode
    st.session_state.last_fork_count = fork_count

    st.sidebar.info(
        f"Maximum processes: "
        f"2^{fork_count} = {2 ** fork_count}"
    )


# =========================================================
# CUSTOM MODE
# =========================================================

else:

    st.sidebar.write(
        "### Select the process that performs each fork()"
    )

    custom_count = st.sidebar.slider(
        "Number of fork() operations",
        min_value=1,
        max_value=8,
        value=4
    )

    available_processes = ["P0"]

    selected_parents = []

    for i in range(custom_count):

        parent = st.sidebar.selectbox(
            f"fork() #{i + 1}",
            available_processes,
            key=f"custom_parent_{i}"
        )

        selected_parents.append(parent)

        # One new child becomes available after each fork.
        new_child = f"P{i + 1}"

        if new_child not in available_processes:

            available_processes.append(
                new_child
            )

    steps = create_custom_simulation(
        selected_parents
    )

    if (
        "last_mode" not in st.session_state
        or st.session_state.last_mode != mode
        or "last_custom_count" not in st.session_state
        or st.session_state.last_custom_count != custom_count
    ):

        st.session_state.current_step = 0

    st.session_state.last_mode = mode
    st.session_state.last_custom_count = custom_count

    fork_count = custom_count

    st.sidebar.info(
        "Custom mode creates one child for every "
        "selected fork() operation."
    )


# =========================================================
# STEP INITIALIZATION
# =========================================================

if "current_step" not in st.session_state:

    st.session_state.current_step = 0


current_step = min(
    st.session_state.current_step,
    len(steps) - 1
)

processes = steps[current_step]


# =========================================================
# EXECUTION CONTROLS
# =========================================================

st.header("🎮 Execution Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:

    if st.button(
        "⏮ Reset",
        use_container_width=True
    ):

        st.session_state.current_step = 0
        st.rerun()


with col2:

    if st.button(
        "⬅ Previous",
        use_container_width=True
    ):

        if st.session_state.current_step > 0:

            st.session_state.current_step -= 1
            st.rerun()


with col3:

    if st.button(
        "Next ➡",
        use_container_width=True
    ):

        if (
            st.session_state.current_step
            < len(steps) - 1
        ):

            st.session_state.current_step += 1
            st.rerun()


with col4:

    if st.button(
        "Final ⏭",
        use_container_width=True
    ):

        st.session_state.current_step = (
            len(steps) - 1
        )

        st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

st.divider()

st.header("📊 Simulation Dashboard")

total_processes = len(processes)

child_processes = total_processes - 1

if mode == "Sequential fork()":

    maximum_processes = 2 ** fork_count

else:

    maximum_processes = fork_count + 1


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Current Step",
        current_step
    )

with col2:

    st.metric(
        "Processes",
        total_processes
    )

with col3:

    st.metric(
        "Child Processes",
        child_processes
    )

with col4:

    st.metric(
        "Fork Operations",
        fork_count
    )


# =========================================================
# PROCESS GROWTH FORMULA
# =========================================================

st.markdown(
    '<div class="section-heading">🧮 Process Growth</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="info-box">

<div class="info-title">
Number of Processes
</div>

<div class="info-text">

For unrestricted sequential fork() calls:

<center>

<b>Number of Processes = 2<sup>n</sup></b>

</center>

where <b>n</b> is the number of fork() calls.

</div>

</div>
""", unsafe_allow_html=True)

formula_col1, formula_col2, formula_col3, formula_col4 = st.columns(4)

with formula_col1:
    st.metric("1 fork()", "2 processes")

with formula_col2:
    st.metric("2 fork()", "4 processes")

with formula_col3:
    st.metric("3 fork()", "8 processes")

with formula_col4:
    st.metric("4 fork()", "16 processes")


# =========================================================
# CURRENT EXECUTION
# =========================================================

st.divider()

st.header("🧠 Current Execution")

if current_step == 0:

    st.info(
        """
        **Initial State**

        Only the root process P0 exists.

        No fork() operation has been executed yet.
        """
    )

else:

    previous = steps[current_step - 1]

    previous_ids = {
        p["id"]
        for p in previous
    }

    new_processes = [
        p
        for p in processes
        if p["id"] not in previous_ids
    ]

    st.success(
        f"fork() operation #{current_step} executed."
    )

    st.write(
        f"Processes before operation: "
        f"**{len(previous)}**"
    )

    st.write(
        f"New processes created: "
        f"**{len(new_processes)}**"
    )

    st.write(
        f"Processes after operation: "
        f"**{len(processes)}**"
    )

    for child in new_processes:

        st.write(
            f"🔹 **{child['parent']}** "
            f"→ `fork()` → "
            f"**{child['id']}** "
            f"(PID {child['pid']})"
        )


# =========================================================
# PROCESS TREE
# =========================================================

st.divider()

st.header("🌳 Process Hierarchy")

graph = Digraph()

graph.attr(
    rankdir="TB",
    bgcolor="transparent",
    nodesep="0.5",
    ranksep="0.7"
)

graph.attr(
    "node",
    shape="box",
    style="rounded,filled",
    fontname="Arial",
    margin="0.2"
)

existing_ids = {
    process["id"]
    for process in processes
}


# Create nodes
for process in processes:

    if process["id"] == "P0":

        label = (
            "P0\n"
            f"PID: {process['pid']}\n"
            "ROOT"
        )

    else:

        label = (
            f"{process['id']}\n"
            f"PID: {process['pid']}\n"
            f"PPID: {process['ppid']}"
        )

    graph.node(
        process["id"],
        label
    )


# Create parent-child edges
for process in processes:

    for child in process["children"]:

        if child in existing_ids:

            graph.edge(
                process["id"],
                child
            )


st.graphviz_chart(
    graph,
    use_container_width=True
)


# =========================================================
# PROCESS EXPLORER
# =========================================================

st.divider()

st.header("🔍 Process Explorer")

process_names = [
    process["id"]
    for process in processes
]

selected_process = st.selectbox(
    "Select a process to inspect",
    process_names
)

selected = next(
    process
    for process in processes
    if process["id"] == selected_process
)

col1, col2 = st.columns(2)

with col1:

    st.subheader("Process Information")

    st.write(
        f"**Process:** {selected['id']}"
    )

    st.write(
        f"**PID:** {selected['pid']}"
    )

    st.write(
        f"**PPID:** "
        f"{selected['ppid'] or 'None'}"
    )

    st.write(
        f"**Created at fork():** "
        f"{selected['created_at']}"
    )


with col2:

    st.subheader("Relationships")

    st.write(
        f"**Parent:** "
        f"{selected['parent'] or 'None'}"
    )

    if selected["children"]:

        st.write(
            f"**Children:** "
            f"{', '.join(selected['children'])}"
        )

    else:

        st.write(
            "**Children:** None"
        )


# =========================================================
# PROCESS TABLE
# =========================================================

st.divider()

st.header("📋 Process Table")

table = []

for process in processes:

    table.append(
        {
            "Process": process["id"],
            "PID": process["pid"],
            "PPID": (
                process["ppid"]
                if process["ppid"]
                else "-"
            ),
            "Parent": (
                process["parent"]
                if process["parent"]
                else "-"
            ),
            "Children": (
                ", ".join(process["children"])
                if process["children"]
                else "-"
            ),
            "Created At": process["created_at"]
        }
    )

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FORK EXECUTION LOG
# =========================================================

st.divider()

st.header("📜 Fork Execution Log")

if current_step == 0:

    st.write(
        "No fork() operations have been executed."
    )

else:

    for i in range(
        1,
        current_step + 1
    ):

        before = steps[i - 1]

        after = steps[i]

        before_ids = {
            p["id"]
            for p in before
        }

        created = [
            p
            for p in after
            if p["id"] not in before_ids
        ]

        st.markdown(
            f"### fork() #{i}"
        )

        for child in created:

            st.write(
                f"`{child['parent']}` "
                f"→ `{child['id']}`"
            )

        st.write(
            f"Total processes: **{len(after)}**"
        )

        st.markdown("---")


# =========================================================
# PROCESS GROWTH GRAPH
# =========================================================

st.divider()

st.header("📈 Process Growth")

growth = []

for i, step in enumerate(steps):

    growth.append(
        {
            "Fork Operations": i,
            "Processes": len(step)
        }
    )

st.line_chart(
    growth,
    x="Fork Operations",
    y="Processes"
)


# =========================================================
# C PROGRAM
# =========================================================

st.divider()

st.header("💻 Equivalent C Program")

if mode == "Sequential fork()":

    c_program = f"""#include <stdio.h>
#include <unistd.h>

int main()
{{
    printf("Initial PID: %d\\n", getpid());

"""

    for i in range(fork_count):

        c_program += (
            f"    // fork() #{i + 1}\n"
            "    fork();\n"
        )

    c_program += """
    printf("Process PID: %d, Parent PID: %d\\n",
           getpid(), getppid());

    return 0;
}
"""

else:

    c_program = """#include <stdio.h>
#include <unistd.h>

int main()
{
    printf("Initial PID: %d\\n", getpid());

"""

    c_program += (
        "    /*\n"
        "     * Custom mode in the application is a\n"
        "     * simulation of selected parent processes.\n"
        "     * The following fork() calls demonstrate\n"
        "     * the basic Unix/Linux process-creation API.\n"
        "     */\n\n"
    )

    for i, parent in enumerate(selected_parents):

        c_program += (
            f"    // Simulated operation {i + 1}: "
            f"{parent} performs fork()\n"
            "    fork();\n"
        )

    c_program += """
    printf("Process PID: %d, Parent PID: %d\\n",
           getpid(), getppid());

    return 0;
}
"""


st.code(
    c_program,
    language="c"
)

st.caption(
    "Note: The Streamlit application simulates process "
    "creation. The C code demonstrates the actual "
    "Unix/Linux fork() syntax."
)


# =========================================================
# WHAT YOU CAN DO
# =========================================================

st.divider()

st.markdown(
    '<div class="section-heading">🎮 What You Can Do</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    Sequential Mode
    </div>

    <div class="info-text">

    Simulate multiple unrestricted fork() calls
    and observe how the number of processes increases.

    </div>

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown("""
    <div class="info-box">

    <div class="info-title">
    Custom Mode
    </div>

    <div class="info-text">

    Select which process performs each simulated
    fork() operation and observe the resulting
    process hierarchy.

    </div>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# KEY OBSERVATIONS
# =========================================================

st.divider()

st.markdown(
    '<div class="section-heading">💡 Key Observations</div>',
    unsafe_allow_html=True
)

observations = [
    "Every newly created process receives a unique PID.",
    "Every child process stores the PID of its parent as its PPID.",
    "A process can create one or more child processes.",
    "Parent-child relationships form a hierarchical process tree.",
    "With unrestricted sequential fork() calls, the process count can double after each fork.",
    "The process tree makes process relationships easier to understand visually."
]

for observation in observations:

    st.write(
        f"🔹 {observation}"
    )


# =========================================================
# OPERATING SYSTEM CONCEPTS
# =========================================================

st.divider()

st.header("📚 Operating System Concepts")

with st.expander("What is a process?"):

    st.write(
        """
        A process is a program that is currently in execution.
        It contains the program code, data, CPU state and other
        resources required for execution.
        """
    )


with st.expander("What is fork()?"):

    st.write(
        """
        fork() is a Unix/Linux system call used to create
        a new child process.

        The process that calls fork() is the parent, while
        the newly created process is the child.
        """
    )


with st.expander("What is PID?"):

    st.write(
        """
        PID stands for Process ID.

        It is a unique identifier assigned to a process
        by the operating system.
        """
    )


with st.expander("What is PPID?"):

    st.write(
        """
        PPID stands for Parent Process ID.

        It identifies the process that created the current
        process.
        """
    )


with st.expander("What is a process tree?"):

    st.write(
        """
        A process tree represents the parent-child
        relationships between processes.

        The root process is at the top and child processes
        appear below their parents.
        """
    )


with st.expander("Why can the number of processes double?"):

    st.write(
        """
        In unrestricted sequential fork() execution,
        every process that exists before the next fork()
        can execute that fork().

        Therefore the number of processes can double
        after every fork.

        1 → 2 → 4 → 8 → 16 → ...

        Hence:

        Number of processes = 2ⁿ
        """
    )


# =========================================================
# PROJECT INFORMATION
# =========================================================

st.divider()

st.markdown(
    '<div class="section-heading">📌 Project Information</div>',
    unsafe_allow_html=True
)

project_info = {
    "Subject": "Operating Systems",
    "Project Type": "Digital Assignment",
    "Topic": "Process Tree Using Multiple fork() Calls",
    "Primary Concept": "Process Creation and Hierarchy",
    "Programming Language": "Python / C",
    "Visualization": "Graphviz",
    "Interface": "Streamlit"
}

st.table(project_info)


# =========================================================
# VIVA PREPARATION
# =========================================================

st.divider()

st.markdown(
    '<div class="section-heading">🎓 Viva Preparation</div>',
    unsafe_allow_html=True
)

st.info(
    "Use these questions to prepare for your project demonstration."
)

viva_categories = {

    "🔹 Basic Concepts": [
        (
            "What is a process?",
            "A process is a program in execution."
        ),
        (
            "What is fork()?",
            "fork() is a Unix/Linux system call used to create a child process."
        ),
        (
            "What is PID?",
            "PID is the unique Process ID assigned to a process."
        ),
        (
            "What is PPID?",
            "PPID is the Process ID of the parent process."
        )
    ],

    "🔹 Process Tree": [
        (
            "What is a process tree?",
            "A process tree represents the parent-child relationships among processes."
        ),
        (
            "What is the root process?",
            "The root process is the starting process of the hierarchy."
        ),
        (
            "Why is a process tree useful?",
            "It makes process relationships and process creation easier to visualize."
        )
    ],

    "🔹 fork() Behaviour": [
        (
            "What happens after fork()?",
            "The parent and newly created child continue execution from the instruction following fork()."
        ),
        (
            "Why can processes double?",
            "Because every existing process may execute the next unrestricted fork()."
        ),
        (
            "How many processes can n unrestricted forks create?",
            "The maximum number is 2ⁿ."
        ),
        (
            "Does this Streamlit application create real OS processes?",
            "No. The application simulates the behavior of fork() for visualization. The actual fork() system call is demonstrated using C syntax."
        )
    ]
}


for category, questions in viva_categories.items():

    with st.expander(category):

        for question, answer in questions:

            st.markdown(
                f"**Q: {question}**"
            )

            st.write(
                f"**A:** {answer}"
            )

            st.markdown("---")


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown("""
<div class="footer">

🌳 <b>Process Tree Visualizer</b>

<br>

Operating Systems Digital Assignment

<br><br>

Process Creation · fork() · PID · PPID ·
Parent-Child Hierarchy

</div>
""", unsafe_allow_html=True)