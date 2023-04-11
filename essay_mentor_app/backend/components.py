# passive and interactive gui components for TESSY streamlit app

from typing import List, Tuple, Union, Optional, Dict

import graphviz
import matplotlib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
import streamlit as st
import textwrap

from essay_mentor_app.backend.aea_datamodel import (
    ArgumentativeEssayAnalysis,
    EssayContentItem,
    BaseContentItem,
    MapContentItem,
    MainClaim,
    Reason,
)
import backend.utils

LABELS = {
    "primary argument": "PrA",
    "objection": "Obj",
    "rebuttal": "Rbt",
}


def display_submit_notice(has_been_submitted: bool = False):
    if has_been_submitted:
        st.info(
            "Your essay has been submitted and evaluated. Results are shown on "
            "page 'Evaluate'. To start over, reload this page.",
            icon="💡",
        )


def display_essay(
    essay: Union[str, List[EssayContentItem]],
    reasons: List[Reason] = None,
    objections: List[Reason] = None,
    rebuttals: List[Reason] = None,
    has_been_submitted: bool = False,
) -> Optional[Dict[str, List[str]]]:
    """multifunctional component
    - to displays the parsed essay as list of essay content items
    - to assign and display reasons to essay content items
    """

    if isinstance(essay, str):
        essay_content = backend.utils.parse_essay_content(essay)
    else:
        essay_content = essay

    reason_labels = {}
    if any([reasons, objections, rebuttals]):
        for rlist in [reasons, objections, rebuttals]:
            if rlist is not None:
                reason_labels.update({r.label: r.uid for r in rlist})

    label_assignments = {}
    for element in essay_content:
        if element.name in ["h1", "h2", "h3", "h4"]:
            st.write(f"{'#'*(element.heading_level+3)} {element.text}")
        else:
            paragraph_placeholder = st.empty()
            if reason_labels:
                label_assignments[element.uid] = st.multiselect(
                    "Reasons discussed in paragraph quoted above (if any):",
                    options=list(reason_labels.keys()),
                    key=f"multiselect_assreas_{element.uid}",
                    disabled=has_been_submitted,
                )
                st.write("\n")

            icon = "¶" if element.name == "p" else "⋮"
            summary = f"{icon} {element.label}  {element.text[:32]}..."
            paragraph_placeholder.write(
                f"<p><details><summary>{summary}</summary>{element.text}</details></p>",
                unsafe_allow_html=True,
            )

    # use uids in label assignments
    for k, v in label_assignments.items():
        label_assignments[k] = [reason_labels[label] for label in v]

    return label_assignments if reason_labels else None


def display_reasons(
    reasons: List[Reason],
    parent_list: List[BaseContentItem],
    reason_name: str = "argument",
    parent_name: str = "parent",
):
    """displays reasons as list of items"""
    reason_name = reason_name[:1].upper() + reason_name[1:]
    for parent in parent_list:
        list_items = [
            f"* **\[{reason.label}\]**: {reason.text}"
            for reason in reasons
            if reason.parent_uid == parent.uid
        ]
        if list_items:
            st.write(
                f"{reason_name}s that address {parent_name} \[{parent.label}\] ({parent.text}):"
            )
            st.write("\n".join(list_items))


def display_argument_map(
    claims: List[MainClaim],
    reasons: List[Reason],
    objections: List[Reason],
    rebuttals: List[Reason],
) -> Optional[str]:
    """construct, display and return argument map as graphviz graph"""

    NODE_TEMPLATE = """<
    <TABLE BORDER="0" COLOR="#444444" CELLPADDING="8" CELLSPACING="2"><TR><TD BORDER="0" BGCOLOR="{bgcolor}" STYLE="rounded" ALIGN="center"><FONT FACE="sans serif;Arial;Helvetica;" POINT-SIZE="10.5"><B>[{label}]</B><br/>{text}</FONT></TD></TR></TABLE>
    >"""

    graph = graphviz.Digraph()
    graph.attr(
        ratio="compress",
        size="6,10",
        orientation="portrait",
        overlay="compress",
        rankdir="BT",
    )
    graph.attr("node", shape="plaintext")

    edgecolor: Dict[str, str] = {}
    edgecolor.update({x.uid: "green" for x in reasons})
    edgecolor.update({x.uid: "red" for x in objections})
    edgecolor.update({x.uid: "blueviolet" for x in rebuttals})

    with graph.subgraph(name="claims") as subgraph:
        subgraph.attr(rank="same")
        for claim in claims:
            textlines = textwrap.wrap(claim.text, width=30)
            text = "<BR/>".join(textlines)
            subgraph.node(
                "node-%s" % claim.uid,
                NODE_TEMPLATE.format(
                    text=text,
                    label=claim.label,
                    bgcolor="lightgray",
                ),
                tooltip=textwrap.fill(claim.text, width=30),
            )

    for reason in reasons + objections + rebuttals:
        textlines = textwrap.wrap(reason.text, width=30)
        text = "<BR/>".join(textlines)
        graph.node(
            "node-%s" % reason.uid,
            NODE_TEMPLATE.format(
                text=text,
                label=reason.label,
                bgcolor="lightblue",
            ),
            tooltip=textwrap.fill(reason.text, width=30),
        )
        # add edge
        graph.edge(
            "node-%s" % reason.uid,
            "node-%s" % reason.parent_uid,
            color=edgecolor[reason.uid],
            penwidth="1.5",
        )

    st.graphviz_chart(graph)
    try:
        graph_svg = graph.pipe(format="svg", encoding="utf-8")
        graph_svg = graph_svg[153:]  # strip xml header
        graph_svg.strip()
        return graph_svg
    except Exception as exc:
        st.error(f"Error while generating argument map: {exc}")
        return None


def display_reasons_hierarchy(
    claims: List[MainClaim],
    reasons: List[Reason],
    objections: List[Reason],
    rebuttals: List[Reason],
):
    """displays reason hierarchy (argument map) as nested list"""
    markdown_lines = []
    for claim in claims:
        markdown_lines.append(f"* **\[{claim.label}\]**: {claim.text}")
        for reason in reasons:
            if reason.parent_uid == claim.uid:
                markdown_lines.append(f"  * **\[{reason.label}\]**: {reason.text}")
                for objection in objections:
                    if objection.parent_uid == reason.uid:
                        markdown_lines.append(
                            f"    * **\[{objection.label}\]**: {objection.text}"
                        )
                        for rebuttal in rebuttals:
                            if rebuttal.parent_uid == objection.uid:
                                markdown_lines.append(
                                    f"      * **\[{rebuttal.label}\]**: {rebuttal.text}"
                                )
        for objection in objections:
            if objection.parent_uid == claim.uid:
                markdown_lines.append(
                    f"  * **\[{objection.label}\]**: {objection.text}"
                )
                for rebuttal in rebuttals:
                    if rebuttal.parent_uid == objection.uid:
                        markdown_lines.append(
                            f"    * **\[{rebuttal.label}\]**: {rebuttal.text}"
                        )
    st.markdown("\n".join(markdown_lines))


def input_reasons(
    parent_list: List[MapContentItem],
    parent_name: str = "parent",
    reason_name: str = "argument",
    expanded_per_default=True,
    with_skip_button=False,
    has_been_submitted=False,
    default_value="",
) -> Tuple[List[Reason], bool]:
    """dynamic input form for submitting reasons"""
    reasons_text_areas = []
    for e, parent in enumerate(parent_list):
        # initial_text = "\n\n".join([
        #    ir.text for ir in initial_reasons
        #    if ir.parent_uid==parent.uid
        # ])
        key = f"{reason_name}_txt_{parent.uid}"
        expanded = expanded_per_default or bool(st.session_state.get(key, None))
        with st.expander(f"\[{parent.label}\]: {parent.text}", expanded=expanded):
            reasons_text_areas.append(
                st.text_area(
                    f"Summarize {reason_name}s for this {parent_name} (separated by empty lines)",
                    value=default_value,
                    height=120,
                    key=key,
                    disabled=has_been_submitted,
                )
            )

    n_reasons = 0
    for reasons_txt in reasons_text_areas:
        if reasons_txt:
            n_reasons += len([r for r in reasons_txt.splitlines() if r.strip()])

    if n_reasons == 0:
        st.warning(str(f"No {reason_name}s provided."))
    else:
        st.success(str(f"{n_reasons} {reason_name}s provided."))

    reasons: List[Reason] = []

    button_proceed = st.button(
        str(f"Proceed with these {reason_name}s"),
        disabled=not any(reasons_txt for reasons_txt in reasons_text_areas)
        or has_been_submitted,
    )
    button_skip = (
        st.button("Skip this input step.", disabled=has_been_submitted)
        if with_skip_button
        else False
    )

    if button_proceed:
        count = 0
        for e, parent in enumerate(parent_list):
            if reasons_text_areas[e]:
                for raw_reason in reasons_text_areas[e].splitlines():
                    if raw_reason.strip():
                        count += 1
                        reasons.append(
                            Reason(
                                text=raw_reason,
                                parent_uid=parent.uid,
                                label=f"{LABELS.get(reason_name,'ARG')}{count}",
                            )
                        )

    return reasons, button_skip


def display_essay_annotation_metrics(
    essay: List[EssayContentItem],
    reasons: List[Reason] = None,
    objections: List[Reason] = None,
    rebuttals: List[Reason] = None,
):
    """displays the following global metrics for submitted essay annotation:
    - coverage
    - ratio of assigned arguments
    - paragraphs per argument
    """
    # list of all arguments
    arguments: List[Reason] = []
    if reasons:
        arguments += reasons
    if objections:
        arguments += objections
    if rebuttals:
        arguments += rebuttals

    # list of all paragraph uids
    essay_content_items = [
        element for element in essay if element.name not in ["h1", "h2", "h3", "h4"]
    ]
    essay_content_uids = [element.uid for element in essay_content_items]

    # metrics
    essay_content_covered = [
        uid
        for uid in essay_content_uids
        if any([arg for arg in arguments if uid in arg.essay_text_refs])
    ]
    essay_content_covered_ratio = len(essay_content_covered) / len(essay_content_uids)

    arguments_assigned = [arg for arg in arguments if arg.essay_text_refs]
    arguments_assigned_ratio = len(arguments_assigned) / len(arguments)

    average_paragraphs_per_argument = np.mean(
        [len(arg.essay_text_refs) for arg in arguments_assigned]
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Essay content covered", f"{essay_content_covered_ratio*100:.0f} %")
    col2.metric("Arguments assigned", f"{arguments_assigned_ratio*100:.0f} %")
    col3.metric(
        "Paragraphs per ass. argument", f"{average_paragraphs_per_argument:.2f}"
    )


def display_essay_annotation_figure(
    essay: List[EssayContentItem],
    reasons: List[Reason] = None,
    objections: List[Reason] = None,
    rebuttals: List[Reason] = None,
) -> object:
    """creates and displays chart with mapping of arguments to essay items"""
    essay_content_items = [
        element for element in essay if element.name not in ["h1", "h2", "h3", "h4"]
    ]
    essay_content_uids = [element.uid for element in essay_content_items]

    data = []
    for reason in reasons:
        if reason.essay_text_refs:
            for ref in reason.essay_text_refs:
                if ref in essay_content_uids:
                    essay_item = next(x for x in essay_content_items if x.uid == ref)
                    data.append(
                        {
                            "reason": "[%s]" % reason.label,
                            "paragraph": essay_item.label,
                            "rtype": "PrimArg",
                        }
                    )
        else:
            data.append(
                {
                    "reason": "[%s]" % reason.label,
                    "paragraph": "None",
                    "rtype": "PrimArg",
                }
            )
    for objection in objections:
        if objection.essay_text_refs:
            for ref in objection.essay_text_refs:
                if ref in essay_content_uids:
                    essay_item = next(x for x in essay_content_items if x.uid == ref)
                    data.append(
                        {
                            "reason": "[%s]" % objection.label,
                            "paragraph": essay_item.label,
                            "rtype": "Object.",
                        }
                    )
        else:
            data.append(
                {
                    "reason": "[%s]" % objection.label,
                    "paragraph": "None",
                    "rtype": "Object.",
                }
            )
    for rebuttal in rebuttals:
        if rebuttal.essay_text_refs:
            for ref in rebuttal.essay_text_refs:
                if ref in essay_content_uids:
                    essay_item = next(x for x in essay_content_items if x.uid == ref)
                    data.append(
                        {
                            "reason": "[%s]" % rebuttal.label,
                            "paragraph": essay_item.label,
                            "rtype": "Rebut.",
                        }
                    )
        else:
            data.append(
                {
                    "reason": "[%s]" % rebuttal.label,
                    "paragraph": "None",
                    "rtype": "Rebut.",
                }
            )
    for essay_item in essay_content_items:
        if not any(
            essay_item.uid in r.essay_text_refs
            for r in reasons + objections + rebuttals
        ):
            data.append(
                {
                    "reason": "None",
                    "paragraph": essay_item.label,
                    "rtype": "None",
                }
            )

    df = pd.DataFrame(data)

    # Create dimensions
    paragraph_dim = go.parcats.Dimension(
        values=df.paragraph, categoryorder="category ascending", label="Paragraph"
    )

    reason_dim = go.parcats.Dimension(
        values=df.reason,
        label="Reason",
    )

    rtype_order = ["PrimArg", "Object.", "Rebut.", "None"]
    rtype_order = [t for t in rtype_order if t in df.rtype]
    rtype_dim = go.parcats.Dimension(
        values=df.rtype,
        label="Argument Type",
        categoryorder="array",
        categoryarray=rtype_order,
    )

    # Create parcats trace
    colormap = dict(
        [
            ("PrimArg", "green"),
            ("Object.", "red"),
            ("Rebut.", "blueviolet"),
            ("None", "gray"),
        ]
    )
    color = df.rtype.apply(lambda rtype: colormap.get(rtype))

    fig_trace = go.Parcats(
        dimensions=[paragraph_dim, reason_dim, rtype_dim],
        line={"color": color},
        labelfont={'size': 16, 'family': 'Sans-Serif'},
        tickfont={'size': 14, 'family': 'Sans-Serif'},
        hoveron="dimension",
        hoverinfo="count",
    )
    fig_data = [fig_trace]


    fig = go.Figure(fig_data)
    fig.update_layout(
        width=700,
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
    )

    st.plotly_chart(fig, use_container_width=False)

    return fig


def display_evaluation_results(
    evaluation_results: Dict[str, Dict], aea: ArgumentativeEssayAnalysis
):
    # helper functions

    def inv_uncertainty_cat(numscore: float) -> str:
        """casts argument-specific numerical scores as uncertainty labels (inspired by IPCC)"""
        if numscore < 0.1:
            uncertainty_cat = "very likely"
        elif numscore < 0.33:
            uncertainty_cat = "likely"
        elif numscore < 0.66:
            uncertainty_cat = "about as likely as not"
        elif numscore < 0.9:
            uncertainty_cat = "unlikely"
        else:
            uncertainty_cat = "very unlikely"
        return uncertainty_cat

    def format_argm_alt(alt_info: Dict) -> str:
        """format parent node alternative as list item"""
        target = alt_info["alternative"]["edgelist"][0]["target"]
        target = None if target == "None" else target
        valence = alt_info["alternative"]["edgelist"][0].get("valence")
        probability = alt_info.get("probability")
        probability = f"{probability*100:.0f}%" if probability is not None else "N.A."
        if target is None:
            return f"<li>Root claim ({probability*100:.0f}%)</li>"
        if valence == "pro":
            return f"<li>Pro reason for [{aea.get_map_node_by_uid(target).label}] ({probability})</li>"
        if valence == "con":
            return f"<li>Con reason against [{aea.get_map_node_by_uid(target).label}] ({probability})</li>"
        return "<li>Unspecified alternative</li>"

    def format_anno_alt(alt_info: Dict) -> str:
        """format annotation reference alternative as list item"""
        probability = alt_info.get("probability")
        probability = f"{probability*100:.0f}%" if probability is not None else "N.A."
        text_content_items = alt_info["alternative"].get("textContentItems", None)
        if text_content_items:
            txt_id = text_content_items[0].get("id", "")
            if txt_id:
                essay_item = aea.get_essay_item_by_uid(txt_id)
                return f"<li>Not discussed in {essay_item.formatted_label()} ({probability})</li>"
        else:
            txt_id = (
                alt_info["alternative"]
                .get("argmap", {})
                .get("nodelist", [{}])[0]
                .get("annotationReferences", [{}])[0]
                .get("textContentId", "")
            )
            if txt_id:
                essay_item = aea.get_essay_item_by_uid(txt_id)
                return f"<li>Discussed in {essay_item.formatted_label()} ({probability})</li>"

        return "<li>Unspecified alternative</li>"

    def gauge_metric_figure(score: Union[float, int], label: str = "") -> go.Figure:
        """plotly gauge indicator"""
        cmap = matplotlib.cm.get_cmap("RdYlGn")
        rgba = cmap(score)
        gauge = {
            "axis": {
                "range": [None, 100.0],
                "tick0": 100 / 7,
                "dtick": 100 / 7,
                "showticklabels": False,
                "tickwidth": 1,
                "tickcolor": "darkgray",
            },
            "bar": {"color": f"rgba{rgba}"},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": 100.0 * score,
            },
        }
        if label == "arbitrary":
            score = 0
            gauge.pop("threshold")
            gauge["bgcolor"] = "lightgray"

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=100.0 * score,
                domain={"x": [0, 1], "y": [0, 1]},
                number={
                    "font": {"size": 24},
                    "prefix": f"{label} (",
                    "suffix": ")",
                },
                gauge=gauge,
            )
        )
        fig.update_layout(
            width=300,
            height=150,
            margin=dict(l=20, r=20, t=1, b=1),
        )
        return fig

    def bar_metric_figure(score: Union[float, int], label: str = "") -> go.Figure:
        """plotly bar indicator"""
        cmap = matplotlib.cm.get_cmap("RdYlGn")
        rgba = cmap(score)
        gauge = {
            "bar": {"color": f"rgba{rgba}", "thickness": 0.6},
            "shape": "bullet",
            "axis": {"range": [None, 100.0], "visible": False},
        }
        if label == "arbitrary":
            score = None
            gauge["bgcolor"] = "lightgray"
        fig = go.Figure(
            go.Indicator(
                mode="number+gauge",
                value=100.0 * score if score is not None else None,
                gauge=gauge,
                domain={"x": [0, 1], "y": [0, 1]},
            )
        )
        fig.update_layout(
            width=300,
            height=25,
            margin=dict(l=10, r=10, t=1, b=1),
        )
        return fig

    argmap_metrics = evaluation_results.get("argmap_metrics")
    annotation_metrics = evaluation_results.get("annotation_metrics")

    # display overall scores

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Overall quality of the **argumentative analysis**:")
        st.plotly_chart(
            gauge_metric_figure(
                argmap_metrics["globalScore"]["numericalScore"],
                label=argmap_metrics["globalScore"]["qualitativeScore"],
            ),
            use_container_width=True,
        )
    with col2:
        st.markdown("Overall quality of the **essay annotation**:")
        st.plotly_chart(
            gauge_metric_figure(
                annotation_metrics["globalScore"]["numericalScore"],
                label=annotation_metrics["globalScore"]["qualitativeScore"],
            ),
            use_container_width=True,
        )

    # display individual scores for each arguments

    arguments: List[Reason] = []
    if aea.reasons:
        arguments += aea.reasons
    if aea.objections:
        arguments += aea.objections
    if aea.rebuttals:
        arguments += aea.rebuttals

    for argument in arguments:
        arg_argm_mtr = next(
            x for x in argmap_metrics["individualScores"] if x["idRef"] == argument.uid
        )
        arg_anno_mtr = next(
            x
            for x in annotation_metrics["individualScores"]
            if x["idRef"] == argument.uid
        )

        with st.expander(f"Detailed score [{argument.label}]"):
            annorefs = ", ".join(
                [
                    f"{aea.get_essay_item_by_uid(uid).formatted_label()}"
                    for uid in argument.essay_text_refs
                ]
            )
            st.caption(
                f"[{argument.label}]: {argument.text} (Linked to paragraphs: {annorefs})"
            )

            # Argumentative embedding score of argument

            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(
                    f"Argumentative relation of [{argument.label}] to further arguments:"
                )
            with col2:
                st.plotly_chart(
                    bar_metric_figure(
                        arg_argm_mtr["score"].get("numericalScore"),
                        label=arg_argm_mtr["score"]["qualitativeScore"],
                    ),
                    use_container_width=True,
                )

            numscore = arg_argm_mtr["score"].get("numericalScore")
            if numscore is not None:
                summary = f"It is <b>{inv_uncertainty_cat(numscore)}</b> that [{argument.label}] is related to further arguments in another way than specified by the author (i.e., not as pro reason for [{aea.get_map_node_by_uid(argument.parent_uid).label}]). Most plausible alternatives:"
                alternatives = [
                    format_argm_alt(x) for x in arg_argm_mtr["topAlternatives"]
                ]
                alternatives = "".join(alternatives)
                details = f"<ol>{alternatives}</ol>"
                st.markdown(f"<p>{summary}</p><p>{details}</p>", unsafe_allow_html=True)

            # Annotation score of argument

            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(
                    f"Linkage of [{argument.label}] to paragraphs in the text (annotation):"
                )
            with col2:
                st.plotly_chart(
                    bar_metric_figure(
                        arg_anno_mtr["score"].get("numericalScore"),
                        label=arg_anno_mtr["score"]["qualitativeScore"],
                    ),
                    use_container_width=True,
                )

            numscore = arg_anno_mtr["score"].get("numericalScore")
            if numscore is not None:
                summary = f"It is <b>{inv_uncertainty_cat(numscore)}</b> that [{argument.label}] appears in the essay at different places than specified by the author. Most plausible alternatives:"
                alternatives = [
                    format_anno_alt(x) for x in arg_anno_mtr["topAlternatives"]
                ]
                alternatives = "".join(alternatives)
                details = f"<ol>{alternatives}</ol>"
                st.markdown(f"<p>{summary}</p><p>{details}</p>", unsafe_allow_html=True)


## DEPRECATED ##


def eval_scores_table(data: Dict[str, int]) -> str:
    """Return a html table with the evaluation scores."""

    def emoji(score: int) -> str:
        if score == 0:
            return "😟"
        elif score == 1:
            return "😕"
        elif score == 2:
            return "😐"
        elif score == 3:
            return "😊"
        elif score == 4:
            return "😄"

    data_rows = ""
    for key, value in data.items():
        row = f"<tr><td width=65%>{key}</td>"
        for i in range(5):
            if i == value:
                row += f"<td margin=0 padding=0 align=center width=7%>{emoji(i)}</td>"
            else:
                row += "<td align=center width=7%></td>"
        row += "</tr>"
        data_rows += row

    table_header = (
        "<table width=100%>"
        # "<tr>"
        # "<td width=30%></td>"
        # "<td align=center width=14%><i>erroneous</i></td>"
        # "<td align=center width=14%><i>implausible</i></td>"
        # "<td align=center width=14%><i>arbitrary</i></td>"
        # "<td align=center width=14%><i>plausible</i></td>"
        # "<td align=center width=14%><i>compelling</i></td>"
        # "</tr>"
    )
    table_footer = "</table><br/>"

    return table_header + data_rows + table_footer


def dummy_show_detailed_scores(aea):
    # list of all arguments
    arguments: List[Reason] = []
    if aea.reasons:
        arguments += aea.reasons
    if aea.objections:
        arguments += aea.objections
    if aea.rebuttals:
        arguments += aea.rebuttals

    for argument in arguments:
        st.write(f"###### [{argument.label}]: {argument.text}")
        st.caption(f"Linked to paragraphs: ¶003, ¶005")
        dummy_scores = {
            f"Argumentative relation of [{argument.label}] to further arguments": random.randint(
                0, 4
            ),
            f"Link of [{argument.label}] to paragraphs in the essay": random.randint(
                0, 4
            ),
        }
        st.markdown(eval_scores_table(dummy_scores), unsafe_allow_html=True)
        explanation = st.expander("More details and explanation...", expanded=False)
        with explanation:
            summary = f"It is <b>very likely</b> that [{argument.label}] is related to further arguments in another way than specified by the author (i.e., not as pro reason for [xxx]). Most plausible alternatives:"
            details = f"<ol><li>Pro reason for [Obj2] (23%)</li><li>Con reason against [Claim1] (12%)</li><li>Pro reason for [Rbt3] (11%)</li></ol>"
            st.markdown(f"<p>{summary}</p><p>{details}</p>", unsafe_allow_html=True)
            summary = f"It is <b>unlikely</b> that [{argument.label}] appears in the essay at different places than specified by the author. Most plausible alternatives:"
            details = f"<ol><li>Discussed in ¶002 (15%)</li><li>Not discussed in ¶003 (12%)</li><li>Discussed in ¶001 (4%)</li></ol>"
            st.markdown(f"<p>{summary}</p><p>{details}</p>", unsafe_allow_html=True)
