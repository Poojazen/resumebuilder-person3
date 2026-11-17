from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

import streamlit as st

from models import Education, Experience, PersonalInfo


def apply_styles():
    st.html(Path(__file__).with_name("styles.css"))


def personal_info_form():
    data = asdict(PersonalInfo(**st.session_state.personal_info))
    labels = {
        "full_name": "Full name",
        "headline": "Professional headline",
        "email": "Email",
        "phone": "Phone",
        "location": "Location",
        "website": "Website or LinkedIn",
        "summary": "Professional summary",
    }
    for field, label in labels.items():
        widget = st.text_area if field == "summary" else st.text_input
        key = f"personal_{field}"
        st.session_state.setdefault(key, data[field])
        data[field] = widget(label, key=key)
    st.session_state.personal_info = data


def education_form():
    entries = st.session_state.education
    if st.button("Add degree", type="primary"):
        entries[uuid4().hex] = asdict(Education())
        st.rerun()
    if not entries:
        st.info("Add a degree to start your education section.")
    for entry_id, data in list(entries.items()):
        with st.container(border=True):
            st.markdown(f"**Degree {list(entries).index(entry_id) + 1}**")
            if st.button("Remove degree", key=f"remove_education_{entry_id}"):
                del entries[entry_id]
                st.rerun()
            for field, label in {
                "institution": "School or university",
                "degree": "Degree",
                "field_of_study": "Field of study",
                "start_date": "Start date (e.g. Aug 2020)",
                "end_date": "End date (e.g. May 2024 or Present)",
                "details": "Honors, coursework, or other details",
            }.items():
                widget = st.text_area if field == "details" else st.text_input
                data[field] = widget(
                    label, value=data[field], key=f"education_{entry_id}_{field}"
                )
            entries[entry_id] = asdict(Education(**data))


def experience_form():
    entries = st.session_state.experience
    if st.button("Add job", type="primary"):
        entries[uuid4().hex] = asdict(Experience())
        st.rerun()
    if not entries:
        st.info("Add a job to start your experience section.")
    for entry_id, data in list(entries.items()):
        with st.container(border=True):
            st.markdown(f"**Job {list(entries).index(entry_id) + 1}**")
            if st.button("Remove job", key=f"remove_experience_{entry_id}"):
                del entries[entry_id]
                st.rerun()
            for field, label in {
                "company": "Company",
                "job_title": "Job title",
                "location": "Job location",
                "start_date": "Start date (e.g. Jun 2024)",
                "end_date": "End date (e.g. Oct 2025 or Present)",
                "achievements": "Responsibilities and achievements (one per line)",
            }.items():
                widget = st.text_area if field == "achievements" else st.text_input
                data[field] = widget(
                    label, value=data[field], key=f"experience_{entry_id}_{field}"
                )
            entries[entry_id] = asdict(Experience(**data))
