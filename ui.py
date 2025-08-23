import streamlit as st


def render_start_page():
	st.markdown("""
	<style>
	.stApp {
		background-image: url("https://phuongnamvina.com/img_data/images/ui-ux-design.jpg");
		background-size: cover;
		background-position: center;
		background-repeat: no-repeat;
		background-attachment: fixed;
		min-height: 100vh;
	}
	.button-container {
		position: fixed;
		bottom: 150px;
		left: 90px;
		z-index: 20;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
	}
	div.stButton > button:first-child {
		background-color: #c0423c !important;
		color: white !important;
		font-size: 1.35em !important;
		font-weight: bold !important;
		border: none !important;
		padding: 20px 70px !important;
		border-radius: 14px !important;
		cursor: pointer !important;
		transition: background 0.3s ease !important;
		margin-bottom: 30px !important;
		box-shadow: 0 2px 24px #ad89f799;
	}
	div.stButton > button:first-child:hover {
		background-color: #a83732 !important;
	}
	.features-bar {
		width: 100vw;
		display: flex;
		justify-content: flex-start;
		gap: 64px;
		position: fixed;
		bottom: 55px;
		left: 80px;
		z-index: 10;
	}
	.feature-icon-img {
		width: 82px;
		height: 82px;
		border-radius: 20px;
		background: rgba(36, 22, 97, 0.92);
		padding: 16px;
		box-shadow: 0 3px 24px #ad89f755;
	}
	</style>
	""", unsafe_allow_html=True)

	# Button container, positioned left/bottom (above icons)
	st.markdown('<div class="button-container">', unsafe_allow_html=True)
	clicked = st.button("⚡ Get Started Now", key="get_started_btn")
	st.markdown('</div>', unsafe_allow_html=True)

	# Icons, horizontally aligned, left and near bottom
	st.markdown("""
		<div class="features-bar">
			<img src="https://img.icons8.com/clouds/100/pdf.png" alt="PDF Icon" class="feature-icon-img"/>
			<img src="https://img.icons8.com/fluency/96/folder-invoices.png" alt="Folder Icon" class="feature-icon-img"/>
			<img src="https://img.icons8.com/fluency/96/artificial-intelligence.png" alt="AI Brain Icon" class="feature-icon-img"/>
		</div>
	""", unsafe_allow_html=True)

	return clicked


def render_tools_page():
	st.markdown("""
		<style>
		.tools-title {
			font-size: 2.2em;
			font-weight: 800;
			text-align: center;
			margin-top: 18px;
			margin-bottom: 30px;
			letter-spacing: 0.01em;
		}
		.tool-card {
			background: #fff;
			border-radius: 18px;
			box-shadow: 0 8px 64px #ad89f755, 0 1.5px 3px #eee;
			width: 310px;
			min-height: 380px;
			padding: 32px 22px 26px 22px;
			display: flex;
			flex-direction: column;
			align-items: center;
			transition: box-shadow 0.2s;
		}
		.tool-card:hover {
			box-shadow: 0 12px 72px #ad89f7cc, 0 3px 11px #ccc;
		}
		.tool-icon {
			margin-bottom: 11px;
			margin-top: 6px;
		}
		.tool-title {
			font-size: 1.28em;
			font-weight: 700;
			margin-bottom: 12px;
			text-align: center;
		}
		.tool-desc {
			font-size: 1.01em;
			color: #555;
			text-align: center;
			margin-bottom: 32px;
		}
		</style>
	""", unsafe_allow_html=True)

	st.markdown('<div class="tools-title">Choose Your AI Power</div>', unsafe_allow_html=True)

	col1, col2, col3 = st.columns(3)
	# Smart Summarize
	with col1:
		if st.button("Start Summarizing", key="start_summarizing_btn"):
			st.session_state.page = 'summarize'
		st.markdown('''
			<div class="tool-card">
				<img src="https://img.icons8.com/fluency/96/artificial-intelligence.png" class="tool-icon" width="68"/>
				<div class="tool-title">Smart Summarize</div>
				<div class="tool-desc">Get instant AI-powered summaries with key insights and important highlights from any PDF document.</div>
			</div>
		''', unsafe_allow_html=True)

	# Intelligent Q&A
	with col2:
		if st.button("Start Chatting", key="start_chatting_btn"):
			st.session_state.page = 'chat'
		st.markdown('''
			<div class="tool-card">
				<img src="https://img.icons8.com/color/96/speech-bubble.png" class="tool-icon" width="61"/>
				<div class="tool-title">Intelligent Q&amp;A</div>
				<div class="tool-desc">Have natural conversations with your documents. Ask questions in any language and get precise answers.</div>
			</div>
		''', unsafe_allow_html=True)

	# Smart Editor
	with col3:
		if st.button("Start Editing", key="start_editing_btn"):
			st.session_state.page = 'edit'
		st.markdown('''
			<div class="tool-card">
				<img src="https://img.icons8.com/clouds/100/pdf.png" class="tool-icon" width="65"/>
				<div class="tool-title">Smart Editor</div>
				<div class="tool-desc">Edit your PDF content with AI assistance and download the modified document instantly.</div>
			</div>
		''', unsafe_allow_html=True)

	# Centered Back to Home button
	st.markdown("<br>", unsafe_allow_html=True)
	col_left, col_center, col_right = st.columns([1, 2, 1])
	with col_center:
		if st.button("← Back to Home", key="back_to_home_btn"):
			st.session_state.page = 'start'

