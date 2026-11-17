"""Review-first writing controls shared by all editable resume sections."""
import json
import os
import streamlit as st
from ai_service import (ACTIONS, STYLES, LENGTHS, AIError, WritingRequest, improve,
                        default_provider, get_provider, list_nvidia_models, NVIDIA_DEFAULT_MODEL)


def ai_settings():
    with st.expander('Provider & model settings'):
        options = ['nvidia', 'openai']
        saved = st.session_state.get('writing_config', {})
        st.session_state.setdefault('writing_provider', saved.get('provider', default_provider()))
        name = st.selectbox('AI provider', options, index=options.index(default_provider()),
                            format_func=lambda p: 'NVIDIA NIM' if p == 'nvidia' else 'OpenAI', key='writing_provider')
        if name == 'nvidia':
            st.caption('Uses NVIDIA_API_KEY from the server environment. Your existing NVIDIA Build key is sufficient; select a model below.')
            if st.button('Load NVIDIA models', key='load_nvidia_models'):
                try:
                    with st.spinner('Loading model catalog…'):
                        st.session_state.nvidia_models = list_nvidia_models()
                except AIError as error:
                    st.error(str(error))
            preferred = os.getenv('NVIDIA_MODEL', NVIDIA_DEFAULT_MODEL)
            models = list(dict.fromkeys([preferred, *st.session_state.get('nvidia_models', [])]))
            st.session_state.setdefault('writing_nvidia_choice', saved.get('nvidia_choice', preferred))
            if st.session_state.writing_nvidia_choice not in models + ['Enter model ID…']:
                models.append(st.session_state.writing_nvidia_choice)
            st.session_state.setdefault('writing_nvidia_custom', saved.get('nvidia_custom', ''))
            selected = st.selectbox('NVIDIA model', models + ['Enter model ID…'], key='writing_nvidia_choice')
            model = st.text_input('Custom NVIDIA model ID', key='writing_nvidia_custom') if selected == 'Enter model ID…' else selected
            st.caption('Choose a text/chat model. Catalog listing does not guarantee account access or JSON support. Try another model if requests fail. Loading models sends no resume text.')
        else:
            st.session_state.setdefault('writing_openai_model', saved.get('openai_model', os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')))
            model = st.text_input('OpenAI model', key='writing_openai_model')
        st.session_state.writing_model = model.strip()
        st.session_state.writing_config = dict(provider=name, model=model.strip(),
            nvidia_choice=st.session_state.get('writing_nvidia_choice', saved.get('nvidia_choice', os.getenv('NVIDIA_MODEL', NVIDIA_DEFAULT_MODEL))),
            nvidia_custom=st.session_state.get('writing_nvidia_custom', saved.get('nvidia_custom', '')),
            openai_model=st.session_state.get('writing_openai_model', saved.get('openai_model', os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'))))
        destination = (name, model.strip())
        if st.session_state.get('writing_destination') != destination:
            for key in list(st.session_state):
                if key.startswith('ai_consent_'):
                    st.session_state[key] = False
            st.session_state.writing_destination = destination


def accept_suggestion(key, data, field):
    suggestion = st.session_state.get('ai_result_' + key)
    if suggestion and suggestion['original'] == data.get(field, ''):
        data[field] = suggestion['text']
        st.session_state[key] = suggestion['text']
        st.session_state.pop('ai_result_' + key, None)


def writing_controls(key, data, field, section, *, summary=False, context=''):
    if not st.session_state.get('ai_studio_active', False):
        return
    with st.expander('Summary assistant' if summary else 'AI Improve', expanded=False):
        name = st.session_state.get('writing_provider', default_provider())
        provider = get_provider(name, st.session_state.get('writing_model'))
        label = 'NVIDIA NIM' if name == 'nvidia' else 'OpenAI'
        st.caption(f'Optional · {label} receives the text shown below and the supplied context only when you request a suggestion. Review every factual claim before accepting.')
        if not provider.api_key.strip():
            st.info(f'AI is unavailable until {provider.key_variable} is configured. You can keep editing and exporting.')
        action = 'Generate summary' if summary else st.selectbox('Writing action', ACTIONS, key='ai_action_' + key)
        style = st.session_state.get('studio_style', 'Professional')
        length = st.session_state.get('studio_length', 'Balanced')
        original = data.get(field, '')
        source = context if summary else original
        signature = json.dumps([name, provider.model, source, context, section, action, style, length], ensure_ascii=False)
        st.caption('Text to send')
        st.code(source or '(empty)', language=None)
        if context and not summary:
            st.caption('Context to send')
            st.code(context, language=None)
        st.caption(f'Clicking Generate or Regenerate sends the displayed text and context to {label}.')
        consent = True
        cached = st.session_state.get('ai_result_' + key)
        busy_key = 'ai_busy_' + key
        if st.button('Regenerate' if cached else 'Generate suggestion', key='ai_generate_' + key,
                     disabled=not consent or not bool(source.strip()) or st.session_state.get(busy_key, False)):
            st.session_state[busy_key] = True
            try:
                with st.spinner('Preparing a suggestion…'):
                    if not st.session_state.get('writing_model', provider.model).strip():
                        raise AIError('Select a model in AI settings first.')
                    result = improve(WritingRequest(source, section, action, style, length, context if not summary else ''), consent=consent, provider=provider)
                st.session_state['ai_result_' + key] = dict(original=original, text=result.text, questions=result.questions, signature=signature)
            except AIError as error:
                st.error(str(error))
            finally:
                st.session_state[busy_key] = False
        result = st.session_state.get('ai_result_' + key)
        if result:
            st.caption('Original')
            st.text(result['original'] or '(empty)')
            st.caption('Suggestion · verify facts before accepting')
            st.text(result['text'])
            for question in result['questions']:
                st.info(question)
            stale = result['original'] != original or result.get('signature') != signature
            if stale:
                st.warning('The source, context, or writing preferences changed. Regenerate before accepting.')
            left, right = st.columns(2)
            left.button('Accept', key='ai_accept_' + key, disabled=stale, on_click=accept_suggestion, args=(key, data, field))
            if right.button('Reject', key='ai_reject_' + key):
                del st.session_state['ai_result_' + key]
                st.rerun()
