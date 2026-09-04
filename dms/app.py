# py -m streamlit run dms/app.py

import html
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from database import (
    initialize_database,
    get_all_resumes,
    get_all_entities,
    get_resume_count,
    get_entity_count
)

from ingest_service import process_resume
from search_service import search_entity

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ENTITY_TYPES = [
    "NAME",
    "COLLEGE_NAME",
    "COMPANY",
    "DEGREE",
    "DESIGNATION",
    "EMAIL",
    "GRADUATION_YEAR",
    "LOCATION",
    "SKILLS",
    "YEARS_OF_EXPERIENCE"
]

initialize_database()

st.set_page_config(
    page_title="Resume Document Management System",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>

/* APP BACKGROUND */
.stApp {
    background:
        radial-gradient(
            circle at top right,
            rgba(112, 74, 80, 0.10),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #0d0f12 0%,
            #111419 50%,
            #0c0e11 100%
        );
    color: #f3f4f6;
}

/* MAIN PAGE */
.block-container {
    max-width: 1250px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

/* HERO */
.hero {
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;

    border: 1px solid rgba(174, 115, 125, 0.30);

    border-radius: 20px;

    background:
        linear-gradient(
            120deg,
            rgba(27, 29, 34, 0.98),
            rgba(44, 31, 35, 0.90)
        );

    box-shadow:
        0 16px 40px rgba(0, 0, 0, 0.30);
}

.hero-badge {
    display: inline-block;

    color: #d6a2aa;

    font-size: 0.78rem;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 1.5px;

    margin-bottom: 0.7rem;
}

.hero h1 {
    margin: 0;

    color: #f9fafb;

    font-size: 2.35rem;

    font-weight: 750;
}

.hero p {
    margin: 0.65rem 0 0;

    color: #b8bcc5;

    font-size: 1.02rem;
}

/* HEADINGS */
h1,
h2,
h3 {
    color: #f3f4f6 !important;
}

h2 {
    font-weight: 700 !important;
}

h3 {
    font-weight: 650 !important;
}

/* METRIC CARDS */
div[data-testid="stMetric"] {
    min-height: 125px;

    padding: 1.25rem 1.4rem;

    border: 1px solid rgba(255, 255, 255, 0.08);

    border-radius: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(27, 30, 36, 0.98),
            rgba(20, 22, 27, 0.98)
        );

    box-shadow:
        0 8px 24px rgba(0, 0, 0, 0.22);
}

div[data-testid="stMetricLabel"] {
    color: #aeb3bd;

    font-size: 0.92rem;

    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #e6c4c9;

    font-weight: 750;
}

/* TABS */
div[data-testid="stTabs"] {
    margin-top: 0.4rem;
}

div[data-testid="stTabs"] button {
    color: #aeb3bd;

    font-weight: 600;

    padding-left: 1rem;

    padding-right: 1rem;
}

div[data-testid="stTabs"] button:hover {
    color: #e4c0c5;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #e4c0c5;
}

div[data-testid="stTabs"] button[aria-selected="true"] p {
    color: #e4c0c5 !important;
}

/* TAB INDICATOR */
div[data-baseweb="tab-highlight"] {
    background-color: #b77b84 !important;
}

/* NORMAL BUTTONS */
.stButton > button {
    background:
        linear-gradient(
            90deg,
            #704a50,
            #8d5b64
        );

    color: #ffffff;

    border: 1px solid rgba(222, 179, 186, 0.20);

    border-radius: 10px;

    font-weight: 650;

    transition: 0.2s ease;
}

.stButton > button:hover {
    background:
        linear-gradient(
            90deg,
            #82555d,
            #9a6870
        );

    border-color: #b77b84;

    color: #ffffff;

    transform: translateY(-1px);
}

/* PRIMARY BUTTON */
button[kind="primary"] {
    background:
        linear-gradient(
            90deg,
            #704a50,
            #91616a
        ) !important;

    border: none !important;

    color: white !important;
}

/* DOWNLOAD BUTTON */
.stDownloadButton > button {
    background: #20242a;

    color: #f3f4f6;

    border: 1px solid #444951;

    border-radius: 10px;
}

.stDownloadButton > button:hover {
    background: #2a2e35;

    border-color: #8d5b64;

    color: white;
}

/* INPUT */
div[data-baseweb="input"] {
    background-color: #171a1f;

    border-radius: 10px;
}

div[data-baseweb="input"] input {
    color: #f3f4f6;
}

/* SELECT BOX */
div[data-baseweb="select"] > div {
    background-color: #171a1f;

    border-radius: 10px;

    border-color: #343840;
}

/* FILE UPLOADER */
section[data-testid="stFileUploaderDropzone"] {
    background:
        linear-gradient(
            145deg,
            rgba(25, 28, 33, 0.96),
            rgba(19, 21, 26, 0.96)
        );

    border: 1px dashed rgba(183, 123, 132, 0.50);

    border-radius: 15px;
}

/* EXPANDERS */
details {
    background:
        linear-gradient(
            145deg,
            rgba(25, 28, 33, 0.96),
            rgba(19, 21, 25, 0.96)
        );

    border: 1px solid rgba(255, 255, 255, 0.07);

    border-radius: 12px;

    margin-bottom: 0.6rem;
}

details:hover {
    border-color: rgba(183, 123, 132, 0.35);
}

/* DATAFRAME */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.08);

    border-radius: 12px;

    overflow: hidden;
}

/* ENTITY HIGHLIGHT */
mark {
    background-color: #d9aa66;

    color: #181818;

    padding: 2px 5px;

    border-radius: 4px;

    font-weight: 750;
}

/* SUCCESS MESSAGE */
div[data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: 12px;
}

/* DIVIDER */
hr {
    border-color: rgba(255, 255, 255, 0.08);
}

/* CAPTION */
.small-muted {
    color: #8f949d;

    font-size: 0.88rem;
}

/* SECTION CARD */
.section-card {
    padding: 1.2rem 1.4rem;

    border-radius: 14px;

    border: 1px solid rgba(255, 255, 255, 0.07);

    background: rgba(24, 27, 32, 0.72);

    margin-bottom: 1rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<div class="hero-badge">Intelligent Resume Management</div>
<h1>Resume Document Management System</h1>
<p>Extract named entities, organize resume information, and retrieve relevant documents efficiently.</p>
</div>
""", unsafe_allow_html=True)

dashboard_tab, upload_tab, search_tab, documents_tab = st.tabs([
    "Dashboard",
    "Upload Resume",
    "Search Entity",
    "View Documents"
])

with dashboard_tab:
    st.subheader("Dashboard")

    total_resumes = get_resume_count()
    total_entities = get_entity_count()

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric(
            "Total Resumes",
            total_resumes
        )

    with metric_col2:
        st.metric(
            "Total Extracted Entities",
            total_entities
        )

    st.write("")
    st.subheader("Entity Distribution")

    st.markdown(
        """
        <p class="small-muted">
            Number of entities extracted from all resumes currently stored in the DMS.
        </p>
        """,
        unsafe_allow_html=True
    )

    entities = get_all_entities()

    if entities:
        counts = {}

        for entity in entities:
            entity_type = entity[1]

            if entity_type not in counts:
                counts[entity_type] = 0

            counts[entity_type] += 1

        chart_data = {
            "Entity Type": list(counts.keys()),
            "Count": list(counts.values())
        }

        df = pd.DataFrame(chart_data)

        df = df.sort_values(
            by="Count",
            ascending=True
        )

        chart_colors = [
            "#8c7ae6",
            "#6fa8dc",
            "#5fb3b3",
            "#78b892",
            "#a2bf68",
            "#d3b65b",
            "#d69b60",
            "#c97d70",
            "#bd8295",
            "#9b8bb5"
        ]

        fig, ax = plt.subplots(
            figsize=(11, 6.4)
        )

        fig.patch.set_facecolor(
            "#101216"
        )

        ax.set_facecolor(
            "#101216"
        )

        bars = ax.barh(
            df["Entity Type"],
            df["Count"],
            color=[
                chart_colors[
                    i % len(chart_colors)
                ]
                for i in range(len(df))
            ],
            height=0.62
        )

        ax.set_title(
            "Extracted Entity Distribution",
            fontsize=16,
            color="#f2f3f5",
            pad=18,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Number of Extracted Entities",
            color="#aeb3bd",
            fontsize=10
        )

        ax.set_ylabel(
            "",
            color="#aeb3bd"
        )

        ax.tick_params(
            axis="x",
            colors="#9ca3af"
        )

        ax.tick_params(
            axis="y",
            colors="#d6d8dc",
            labelsize=10
        )

        ax.xaxis.grid(
            True,
            color="#34373d",
            alpha=0.55,
            linewidth=0.8
        )

        ax.yaxis.grid(
            False
        )

        ax.set_axisbelow(
            True
        )

        for spine in [
            "top",
            "right",
            "left"
        ]:
            ax.spines[
                spine
            ].set_visible(False)

        ax.spines[
            "bottom"
        ].set_color(
            "#34373d"
        )

        maximum_count = max(
            df["Count"]
        )

        for bar in bars:
            width = bar.get_width()

            ax.text(
                width + maximum_count * 0.012,
                bar.get_y() + bar.get_height() / 2,
                str(int(width)),
                va="center",
                ha="left",
                color="#e7e9ed",
                fontsize=9,
                fontweight="bold"
            )

        ax.set_xlim(
            0,
            maximum_count * 1.12
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(
            fig
        )

        with st.expander(
            "View Entity Distribution Data"
        ):
            display_df = df.sort_values(
                by="Count",
                ascending=False
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

    else:
        st.info(
            "No entities available yet."
        )

with upload_tab:
    st.subheader(
        "Upload and Process Resumes"
    )

    st.markdown(
        """
        <p class="small-muted">
            Upload PDF, DOCX, or image-based resumes.
            Text will be extracted, processed using the NER model,
            and stored in the database.
        </p>
        """,
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "Choose one or more resume files",
        type=[
            "pdf",
            "docx",
            "png",
            "jpg",
            "jpeg",
            "bmp",
            "tiff",
            "webp"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info(
            f"{len(uploaded_files)} file(s) selected"
        )

        if st.button(
            "Process Resumes",
            type="primary"
        ):
            success_count = 0
            duplicate_count = 0
            failed_count = 0

            progress_bar = st.progress(
                0
            )

            status_text = st.empty()

            total_files = len(
                uploaded_files
            )

            for index, uploaded_file in enumerate(
                uploaded_files,
                start=1
            ):
                status_text.write(
                    f"Processing {index}/{total_files}: "
                    f"{uploaded_file.name}"
                )

                file_path = (
                    UPLOAD_DIR /
                    uploaded_file.name
                )

                with open(
                    file_path,
                    "wb"
                ) as file:
                    file.write(
                        uploaded_file.getbuffer()
                    )

                try:
                    result = process_resume(
                        file_path
                    )

                    if result is None:
                        failed_count += 1

                        st.error(
                            f"{uploaded_file.name}: "
                            f"No text could be extracted."
                        )

                    elif (
                        result["status"]
                        == "duplicate"
                    ):
                        duplicate_count += 1

                        st.warning(
                            f"{uploaded_file.name}: "
                            f"Already exists in database "
                            f"(Resume ID {result['resume_id']})."
                        )

                    else:
                        success_count += 1

                        st.success(
                            f"{uploaded_file.name}: "
                            f"Stored successfully "
                            f"with {len(result['entities'])} entities."
                        )

                except Exception as error:
                    failed_count += 1

                    st.error(
                        f"{uploaded_file.name}: "
                        f"{error}"
                    )

                progress_bar.progress(
                    index / total_files
                )

            status_text.empty()

            st.write("")
            st.subheader(
                "Processing Summary"
            )

            summary_col1, summary_col2, summary_col3 = st.columns(
                3
            )

            with summary_col1:
                st.metric(
                    "Stored",
                    success_count
                )

            with summary_col2:
                st.metric(
                    "Duplicates",
                    duplicate_count
                )

            with summary_col3:
                st.metric(
                    "Failed",
                    failed_count
                )

with search_tab:
    st.subheader(
        "Search Resume by Entity"
    )

    st.markdown(
        """
        <p class="small-muted">
            Search for an entity stored in the database.
            If an exact match is unavailable, the DMS recommends similar entities.
        </p>
        """,
        unsafe_allow_html=True
    )

    search_col1, search_col2 = st.columns(
        [1, 2]
    )

    with search_col1:
        entity_type = st.selectbox(
            "Entity Type",
            ENTITY_TYPES
        )

    with search_col2:
        query = st.text_input(
            "Search Entity",
            placeholder="Example: Kuala Lumpur"
        )

    if st.button(
        "Search",
        type="primary"
    ):
        if not query.strip():
            st.warning(
                "Please enter an entity to search."
            )

        else:
            with st.spinner(
                "Searching database..."
            ):
                result = search_entity(
                    query,
                    entity_type
                )

            if (
                result["status"]
                == "exact"
            ):
                st.success(
                    f'Exact match found for '
                    f'"{result["matched_entity"]}".'
                )

            elif (
                result["status"]
                == "similar"
            ):
                st.warning(
                    f'No exact match was found for "{query}". '
                    f'The closest entity is '
                    f'"{result["matched_entity"]}".'
                )

                st.write(
                    "**Best Similarity Score:**",
                    f'{result["similarity_score"]:.2f}'
                )

                st.subheader(
                    "Similar Entities"
                )

                suggestion_columns = st.columns(
                    len(
                        result["suggestions"]
                    )
                )

                for index, suggestion in enumerate(
                    result["suggestions"]
                ):
                    with suggestion_columns[index]:
                        st.markdown(
                            f"""
                            <div class="section-card">
                                <b>{html.escape(suggestion["entity"])}</b>
                                <br>
                                <span class="small-muted">
                                    Similarity: {suggestion["score"]:.2f}
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            elif (
                result["status"]
                == "not_found"
            ):
                st.error(
                    "No sufficiently similar entity was found."
                )

            if result.get(
                "results"
            ):
                st.write("")
                st.subheader(
                    f'{len(result["results"])} '
                    f'Document(s) Found'
                )

                for document in result[
                    "results"
                ]:
                    document_highlight = document.get(
                        "similar_entity",
                        result.get(
                            "matched_entity",
                            query
                        )
                    )

                    with st.expander(
                        f'📄 {document["file_name"]}'
                    ):
                        information_col1, information_col2 = st.columns(
                            2
                        )

                        with information_col1:
                            st.write(
                                "**Entity Type**"
                            )

                            st.write(
                                document[
                                    "entity_type"
                                ]
                            )

                        with information_col2:
                            st.write(
                                "**Matched Entity**"
                            )

                            st.write(
                                document_highlight
                            )

                        if (
                            result["status"]
                            == "similar"
                        ):
                            document_similarity = document.get(
                                "similarity_score"
                            )

                            if (
                                document_similarity
                                is not None
                            ):
                                st.write(
                                    "**Similarity Score:**",
                                    f"{document_similarity:.2f}"
                                )

                        file_path = Path(
                            document[
                                "file_path"
                            ]
                        )

                        if file_path.exists():
                            with open(
                                file_path,
                                "rb"
                            ) as file:
                                st.download_button(
                                    "Download Original Resume",
                                    data=file,
                                    file_name=file_path.name,
                                    key=(
                                        f"download_"
                                        f"{document['resume_id']}_"
                                        f"{document_highlight}"
                                    )
                                )

                        st.divider()

                        st.write(
                            "### Resume Content"
                        )

                        safe_text = html.escape(
                            document[
                                "text"
                            ]
                        )

                        safe_entity = html.escape(
                            document_highlight
                        )

                        highlighted_text = re.sub(
                            re.escape(
                                safe_entity
                            ),
                            lambda match: (
                                f"<mark>"
                                f"{match.group(0)}"
                                f"</mark>"
                            ),
                            safe_text,
                            flags=re.IGNORECASE
                        )

                        highlighted_text = (
                            highlighted_text
                            .replace(
                                "\n",
                                "<br>"
                            )
                        )

                        st.markdown(
                            highlighted_text,
                            unsafe_allow_html=True
                        )

with documents_tab:
    st.subheader(
        "Stored Documents"
    )

    st.markdown(
        """
        <p class="small-muted">
            Browse resumes and named entities currently stored in the DMS database.
        </p>
        """,
        unsafe_allow_html=True
    )

    document_metric1, document_metric2 = st.columns(
        2
    )

    with document_metric1:
        st.metric(
            "Total Resumes",
            get_resume_count()
        )

    with document_metric2:
        st.metric(
            "Total Entities",
            get_entity_count()
        )

    st.write("")
    st.subheader(
        "Resume Library"
    )

    resumes = get_all_resumes()

    if not resumes:
        st.info(
            "No resumes stored yet."
        )

    else:
        for resume in resumes:
            resume_id = resume[0]
            file_name = resume[1]
            file_path = resume[2]
            file_type = resume[3]
            created_at = resume[4]

            with st.expander(
                f"📄 {file_name}"
            ):
                info_col1, info_col2, info_col3 = st.columns(
                    3
                )

                with info_col1:
                    st.write(
                        "**Resume ID**"
                    )

                    st.write(
                        resume_id
                    )

                with info_col2:
                    st.write(
                        "**File Type**"
                    )

                    st.write(
                        file_type.upper()
                    )

                with info_col3:
                    st.write(
                        "**Uploaded**"
                    )

                    st.write(
                        created_at
                    )

                original_file = Path(
                    file_path
                )

                if original_file.exists():
                    with open(
                        original_file,
                        "rb"
                    ) as file:
                        st.download_button(
                            "Download Resume",
                            data=file,
                            file_name=original_file.name,
                            key=(
                                f"library_download_"
                                f"{resume_id}"
                            )
                        )

    entities = get_all_entities()

    if entities:
        st.write("")
        st.subheader(
            "Extracted Entity Records"
        )

        entity_data = []

        for entity in entities:
            entity_data.append({
                "Entity ID": entity[0],
                "Type": entity[1],
                "Entity": entity[2],
                "Resume": entity[3]
            })

        entity_df = pd.DataFrame(
            entity_data
        )

        filter_col1, filter_col2 = st.columns(
            [1, 2]
        )

        with filter_col1:
            selected_type = st.selectbox(
                "Filter Entity Type",
                [
                    "ALL"
                ] + ENTITY_TYPES,
                key="document_entity_filter"
            )

        with filter_col2:
            entity_filter = st.text_input(
                "Filter Entity Text",
                placeholder="Type to filter entity records...",
                key="document_entity_text_filter"
            )

        filtered_df = entity_df.copy()

        if (
            selected_type
            != "ALL"
        ):
            filtered_df = filtered_df[
                filtered_df[
                    "Type"
                ] == selected_type
            ]

        if entity_filter.strip():
            filtered_df = filtered_df[
                filtered_df[
                    "Entity"
                ].str.contains(
                    entity_filter,
                    case=False,
                    na=False
                )
            ]

        st.caption(
            f"{len(filtered_df)} entity record(s) displayed"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
