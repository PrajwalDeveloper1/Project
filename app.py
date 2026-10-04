import hashlib
import json
import os
import random
import re
from collections import Counter

import requests
import streamlit as st


st.set_page_config(
	page_title="Project 3 | Resume intelligence",
	page_icon=":material/auto_awesome:",
	layout="wide",
	initial_sidebar_state="expanded",
)

st.markdown(
	"""
	<style>
	:root {
		--ink: #f5f7f2;
		--muted: #a8b2ae;
		--line: rgba(176, 196, 187, 0.16);
		--mint: #b8f2d0;
		--mint-strong: #78d9a7;
		--coral: #ff9b7a;
	}
	.stApp {
		background:
			radial-gradient(circle at 10% -10%, rgba(120, 217, 167, 0.14), transparent 26%),
			radial-gradient(circle at 94% 8%, rgba(255, 155, 122, 0.10), transparent 22%),
			#101513;
		color: var(--ink);
	}
	.main .block-container {
		padding-top: 2.2rem;
		padding-bottom: 3rem;
		max-width: 1440px;
	}
	[data-testid="stSidebar"] {
		background: linear-gradient(180deg, #161d1a 0%, #111715 65%, #0e1210 100%);
		border-right: 1px solid var(--line);
	}
	section[data-testid="stSidebar"] > div {
		padding: 1.4rem 1.15rem 1.5rem;
	}
	[data-testid="stSidebar"] h2 { letter-spacing: -0.03em; }
	[data-testid="stSidebar"] h3 { color: var(--mint); font-size: 0.85rem; letter-spacing: 0.01em; }
	[data-testid="stSidebar"] .stCaption { color: var(--muted); }
	.stButton > button {
		min-height: 2.7rem;
		border-radius: 8px;
		border: 1px solid rgba(184, 242, 208, 0.28);
		background: rgba(255,255,255,0.045);
		color: var(--ink);
		font-weight: 600;
		transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
	}
	.stButton > button:hover {
		border-color: var(--mint-strong);
		background: rgba(184, 242, 208, 0.10);
		box-shadow: 0 10px 28px rgba(0,0,0,0.20);
		transform: translateY(-1px);
	}
	.stButton > button[kind="primary"] { background: var(--mint); color: #112019; border-color: var(--mint); }
	.stButton > button[kind="primary"]:hover { background: #d0f8df; border-color: #d0f8df; }
	.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
		border-radius: 8px;
		background: rgba(7, 12, 10, 0.42);
		color: var(--ink);
		border: 1px solid var(--line);
	}
	.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--mint-strong); box-shadow: 0 0 0 1px var(--mint-strong); }
	.stMetric {
		background: rgba(255,255,255,0.045);
		border: 1px solid var(--line);
		border-radius: 10px;
		padding: 1rem 1.05rem;
	}
	[data-testid="stMetricValue"] { color: var(--mint); letter-spacing: -0.04em; }
	[data-testid="stMetricLabel"] { color: var(--muted); }
	.score-rating {
		display: inline-flex;
		align-items: center;
		padding: 0.28rem 0.7rem;
		margin-top: 0.65rem;
		border-radius: 999px;
		font-size: 0.82rem;
		font-weight: 750;
		letter-spacing: 0.01em;
	}
	.grade-line {
		display: flex;
		align-items: center;
		gap: 1rem;
		width: fit-content;
		margin: 0.35rem 0 1rem;
		padding: 0.7rem 1rem;
		border: 1px solid var(--line);
		border-radius: 12px;
		background: rgba(255, 255, 255, 0.045);
	}
	.grade-label { color: var(--ink); font-size: 1.65rem; font-weight: 750; }
	.score-rating--large { margin-top: 0; padding: 0.55rem 1.3rem; font-size: 1.35rem; }
	.score-rating--very-poor { background: #dc2626; color: #fff; }
	.score-rating--poor { background: #ff1744; color: #fff; box-shadow: 0 0 14px rgba(255, 23, 68, 0.32); }
	.score-rating--fair { background: #f59e0b; color: #241500; }
	.score-rating--good-yellow { background: #ffe600; color: #252000; }
	.score-rating--good-green, .score-rating--excellent, .score-rating--perfect { background: #22c55e; color: #06210f; }
	.score-rating--perfect-neon { background: #39ff14; color: #06210f; box-shadow: 0 0 16px rgba(57, 255, 20, 0.4); }
	[data-testid="stChatMessage"] {
		border: 1px solid var(--line);
		border-radius: 10px;
		padding: 0.7rem 0.9rem;
		margin-bottom: 0.65rem;
		background: rgba(255,255,255,0.035);
	}
	[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
		line-height: 1.65;
	}
	.chat-row {
		border: 1px solid var(--line);
		border-radius: 10px;
		padding: 0.8rem 1rem;
		margin: 0 0 0.7rem 0;
		line-height: 1.65;
	}
	.chat-user {
		background: rgba(184, 242, 208, 0.07);
	}
	.chat-assistant {
		background: rgba(255,255,255,0.035);
	}
	.chat-label {
		font-size: 0.72rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--mint-strong);
		margin-bottom: 0.25rem;
	}
	[data-testid="stChatInput"] {
		border-color: rgba(184, 242, 208, 0.32);
		background: rgba(7, 12, 10, 0.82);
	}
	[data-testid="stPills"] button {
		border-radius: 999px;
		border-color: rgba(148,163,184,0.24);
		background: rgba(15,23,42,0.72);
	}
	.hero-card {
		background: linear-gradient(135deg, rgba(184, 242, 208, 0.11), rgba(255, 155, 122, 0.06));
		border: 1px solid rgba(184, 242, 208, 0.22);
		border-radius: 14px;
		padding: 1.6rem 1.7rem;
		margin-bottom: 1.25rem;
		box-shadow: 0 18px 50px rgba(0,0,0,0.16);
	}
	.hero-kicker {
		font-size: 0.78rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--mint-strong);
		font-weight: 700;
		margin-bottom: 0.35rem;
	}
	.hero-card h3 {
		margin: 0;
		padding: 0;
		font-size: clamp(2.4rem, 5vw, 4.5rem);
		line-height: 1.1;
		letter-spacing: -0.06em;
		font-weight: 700;
		color: var(--ink);
		animation: fadeUp 0.9s ease-out both;
	}
	.hero-card p {
		margin: 0.5rem 0 0 0;
		color: #c5cfca;
		font-size: 1.02rem;
		animation: fadeUp 1.15s ease-out both;
	}
	.hero-kicker {
		font-size: 0.72rem;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		color: var(--muted);
		font-weight: 600;
		margin-bottom: 0.35rem;
	}
	.feature-strip {
		display: flex;
		flex-wrap: wrap;
		gap: 0.65rem;
		margin: 0.8rem 0 1.4rem;
	}
	.feature-pill {
		display: inline-flex;
		align-items: center;
		padding: 0.45rem 0.8rem;
		border-radius: 999px;
		background: rgba(255, 255, 255, 0.045);
		border: 1px solid rgba(184, 242, 208, 0.23);
		color: #d9f8e5;
		font-size: 0.82rem;
		font-weight: 600;
	}
	[data-testid="stHeader"] { background: transparent; }
	[data-testid="stFileUploaderDropzone"] { border-color: var(--line); background: rgba(255,255,255,0.025); }
	h1, h2, h3 { letter-spacing: -0.035em; }
	h2 { margin-top: 1.4rem; }
	@keyframes fadeUp {
		from {
			opacity: 0;
			transform: translateY(14px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
	</style>
	""",
	unsafe_allow_html=True,
)

STOP_WORDS = {
	"about", "after", "also", "and", "are", "been", "being", "but", "can",
	"for", "from", "have", "into", "its", "more", "our", "that", "their",
	"them", "this", "with", "you", "your", "will", "work", "years", "using",
}
SECTION_ALIASES = {
	"contact": ("email", "phone", "linkedin", "github"),
	"summary": ("summary", "profile", "objective"),
	"experience": ("experience", "employment", "work history"),
	"skills": ("skills", "technologies", "technical skills"),
	"education": ("education", "academic", "university", "degree"),
}
ACTION_WORDS = {
	"built", "created", "delivered", "designed", "developed", "improved", "increased",
	"launched", "led", "managed", "reduced", "owned", "shipped", "automated",
	"analyzed", "coordinated", "drove", "grew", "optimized", "produced", "resolved",
}
METRIC_PATTERN = re.compile(r"\b\d+(?:\.\d+)?(?:%|\+|k|m|x)?\b|\$\s?\d+")
COUNTRY_CODES = {
	"+1": "United States / Canada",
	"+44": "United Kingdom",
	"+61": "Australia",
	"+91": "India",
	"+971": "UAE",
	"+65": "Singapore",
}
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_FAST_MODEL = os.getenv("OLLAMA_FAST_MODEL", "qwen2.5:1.5b")


class AIServiceError(Exception):
	"""An actionable error returned by the AI provider."""


@st.cache_data(show_spinner=False)
def tokenize(text: str) -> list[str]:
	words = re.findall(r"[a-zA-Z][a-zA-Z+#.-]{2,}", text.lower())
	return [word for word in words if word not in STOP_WORDS]


@st.cache_data(show_spinner=False)
def extract_keywords(text: str, limit: int = 18) -> list[str]:
	counts = Counter(tokenize(text))
	return [word for word, _ in counts.most_common(limit)]


def extract_bullets(resume: str) -> list[str]:
	return [
		line.strip(" -*\t")
		for line in resume.splitlines()
		if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line)
	]


def build_local_recommendations(resume: str, sections: dict[str, bool], missing: list[str]) -> list[str]:
	recommendations = []
	bullets = extract_bullets(resume)
	if not sections["contact"]:
		recommendations.append("Add one clean contact line at the top with email, phone, LinkedIn, and portfolio or GitHub if relevant.")
	if not sections["summary"]:
		recommendations.append("Add a 2-3 line summary: target role + strongest specialty + the kind of outcome you create.")
	if not bullets:
		recommendations.append("Convert experience paragraphs into 3-5 bullets per role. Start each bullet with an action and end with an outcome.")
	else:
		missing_metrics = sum(not METRIC_PATTERN.search(bullet) for bullet in bullets)
		weak_openings = sum(tokenize(bullet) and tokenize(bullet)[0] not in ACTION_WORDS for bullet in bullets)
		long_bullets = sum(len(tokenize(bullet)) > 30 for bullet in bullets)
		if missing_metrics:
			recommendations.append(f"Add a number to {missing_metrics} bullet(s): quantify users, revenue, time saved, conversion, volume, or quality.")
		if weak_openings:
			recommendations.append(f"Replace {weak_openings} passive bullet opening(s) with a decisive verb such as built, led, reduced, shipped, or optimized.")
		if long_bullets:
			recommendations.append(f"Shorten {long_bullets} long bullet(s) to roughly 20-28 words so the result is easy to scan.")
	if not sections["skills"]:
		recommendations.append("Add a dedicated skills section grouped into 2-4 clusters that match the target role.")
	if missing:
		recommendations.append(f"Review these target terms and add only the ones you can support: {', '.join(missing[:6])}.")
	return recommendations[:6]


@st.cache_data(show_spinner=False)
def build_local_review(resume: str, job_description: str, result: dict) -> dict:
	bullets = extract_bullets(resume)
	matched_terms = result["matched"][:5]
	resume_words = tokenize(resume)
	strengths = []
	if matched_terms:
		strengths.append(f"Your resume already uses target language such as {', '.join(matched_terms)}.")
	if result["impact_score"] >= 40:
		strengths.append("You show evidence of action and measurable impact rather than only listing responsibilities.")
	if result["section_score"] >= 80:
		strengths.append("The core resume sections are present and give the document a recruiter-friendly structure.")
	if not strengths:
		strengths.append("You have a foundation to build on; the next pass should make your evidence more specific and easier to scan.")

	weak_openings = []
	bullet_rewrites = []
	for bullet in bullets[:3]:
		words = tokenize(bullet)
		if words and words[0] in ACTION_WORDS:
			rewrite = bullet
		else:
			rewrite = re.sub(r"^(worked on|helped with|helped|responsible for|involved in)\b", "Supported", bullet, flags=re.IGNORECASE)
			if rewrite == bullet:
				rewrite = f"Delivered results by {bullet[0].lower() + bullet[1:] if bullet else bullet}"
			weak_openings.append(bullet)
		if not METRIC_PATTERN.search(rewrite):
			rewrite += " [Add a measurable result]"
		bullet_rewrites.append({"original": bullet, "rewrite": rewrite})

	weak_count = len(weak_openings)
	weaknesses = []
	if result["missing"]:
		weaknesses.append(f"The resume is missing target language that appears important for this role: {', '.join(result['missing'][:4])}.")
	if not bullets:
		weaknesses.append("Experience is not formatted as accomplishment bullets, which makes impact harder to scan.")
	elif any(not METRIC_PATTERN.search(bullet) for bullet in bullets):
		weaknesses.append("Several bullets describe activity without a number, scope, or outcome to prove the value.")
	if weak_count:
		weaknesses.append(f"{weak_count} bullet(s) begin with a passive or vague phrase instead of a clear action verb.")
	if not weaknesses:
		weaknesses.append("The main opportunity is sharper wording: make each bullet show action, scope, and outcome in one line.")

	top_terms = ", ".join(matched_terms or result["missing"][:3] or resume_words[:3])
	target_focus = ", ".join(extract_keywords(job_description, 3))
	tailored_summary = (
		f"Professional with experience in {top_terms}. "
		f"Brings a track record of {', '.join(ACTION_WORDS.intersection(resume_words)) or 'delivering practical results'} "
		f"and is targeting work centered on {target_focus or 'the requirements of this role'}."
	)
	next_steps = result["local_recommendations"][:3]
	if not next_steps:
		next_steps = ["Review each bullet for a clear action, scope, and measurable result."]

	updated_lines = []
	for line in resume.splitlines():
		if line.strip(" -*\t") in {item["original"] for item in bullet_rewrites}:
			match = next(item for item in bullet_rewrites if item["original"] == line.strip(" -*\t"))
			prefix = line[: len(line) - len(line.lstrip())]
			marker = "- " if line.lstrip().startswith(("-", "*")) else ""
			updated_lines.append(f"{prefix}{marker}{match['rewrite']}")
		else:
			updated_lines.append(line)
	updated_resume = "\n".join(updated_lines)

	return {
		"strengths": strengths[:3],
		"weaknesses": weaknesses[:3],
		"bullet_rewrites": bullet_rewrites,
		"tailored_summary": tailored_summary,
		"next_steps": next_steps,
		"updated_resume": updated_resume,
	}


@st.cache_data(show_spinner=False)
def analyze_resume(resume: str, job_description: str) -> dict:
	resume_lower = resume.lower()
	job_keywords = extract_keywords(job_description)
	matched = [word for word in job_keywords if word in resume_lower]
	missing = [word for word in job_keywords if word not in resume_lower]
	keyword_score = round((len(matched) / len(job_keywords)) * 100) if job_keywords else 0

	sections = {
		name: any(alias in resume_lower for alias in aliases)
		for name, aliases in SECTION_ALIASES.items()
	}
	section_score = round(sum(sections.values()) / len(sections) * 100)
	quantified_results = len(re.findall(r"\b\d+(?:%|\+|k|m|x)?\b", resume_lower))
	action_count = sum(word in ACTION_WORDS for word in tokenize(resume))
	impact_score = min(100, quantified_results * 12 + action_count * 4)
	length_score = 100 if 250 <= len(tokenize(resume)) <= 900 else 65
	overall = round(keyword_score * 0.45 + section_score * 0.25 + impact_score * 0.2 + length_score * 0.1)

	suggestions = []
	if missing:
		suggestions.append(f"Mirror the job language where it is truthful: {', '.join(missing[:5])}.")
	if quantified_results < 3:
		suggestions.append("Add measurable outcomes to at least three bullets: revenue, time saved, scale, or conversion.")
	if not sections["summary"]:
		suggestions.append("Add a short summary that names your level, specialty, and target direction.")
	if not sections["skills"]:
		suggestions.append("Create a dedicated skills section so recruiters and screening systems can find your toolkit quickly.")
	if len(tokenize(resume)) > 900:
		suggestions.append("Trim older or repetitive material. Keep the strongest evidence easy to scan.")
	if not suggestions:
		suggestions.append("The structure is in good shape. Tighten each bullet around action, scope, and measurable result.")
	local_recommendations = build_local_recommendations(resume, sections, missing)

	return {
		"overall": overall,
		"keyword_score": keyword_score,
		"section_score": section_score,
		"impact_score": impact_score,
		"length_score": length_score,
		"matched": matched,
		"missing": missing,
		"sections": sections,
		"suggestions": suggestions,
		"local_recommendations": local_recommendations,
		"word_count": len(tokenize(resume)),
	}


def get_api_key(entered_key: str) -> str:
	if entered_key.strip():
		return entered_key.strip()
	try:
		return st.secrets.get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
	except FileNotFoundError:
		return os.getenv("OPENAI_API_KEY", "")


@st.cache_data(ttl=15, show_spinner=False)
def local_model_available(model: str = OLLAMA_MODEL) -> bool:
	try:
		response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
		if not response.ok:
			return False
		return any(item.get("name") == model for item in response.json().get("models", []))
	except (requests.RequestException, ValueError, TypeError):
		return False


def request_ollama(prompt: str, system: str, model: str = OLLAMA_MODEL, max_tokens: int = 500, timeout: int = 30, json_mode: bool = False) -> str:
	response = requests.post(
		f"{OLLAMA_URL}/api/chat",
		json={
			"model": model,
			"stream": False,
			"format": "json" if json_mode else "",
			"options": {"temperature": 0.35, "num_predict": max_tokens},
			"messages": [
				{"role": "system", "content": system},
				{"role": "user", "content": prompt},
			],
		},
		timeout=timeout,
	)
	if not response.ok:
		raise AIServiceError(f"Local model returned HTTP {response.status_code}.")
	try:
		return response.json()["message"]["content"].strip()
	except (KeyError, TypeError, ValueError) as error:
		raise AIServiceError("The local model returned an invalid response.") from error


def request_local_review(resume: str, job_description: str, mode: str = "fast") -> dict:
	is_deep = mode.lower() == "deep think"
	model = OLLAMA_MODEL if is_deep else OLLAMA_FAST_MODEL
	max_tokens = 800 if is_deep else 420
	timeout = 18 if is_deep else 6
	prompt = f"""
Review this resume against the target job description. Be specific, honest, and encouraging.
Do not invent experience, skills, employers, metrics, or education.

Return only valid JSON with these keys:
strengths: array of 3 concise strings
weaknesses: array of 3 concise strings
bullet_rewrites: array of 3 objects with keys original and rewrite
tailored_summary: one 2-3 sentence professional summary grounded only in the resume
next_steps: array of 3 concise strings
updated_resume: a complete improved resume in plain text, preserving all truthful facts from the original

RESUME:
{resume[:12000]}

TARGET JOB:
{job_description[:10000]}
"""
	system = "You are an expert resume editor and career coach. "
	system += "Think carefully about evidence and role fit before answering." if is_deep else "Keep the feedback practical and concise."
	review = json.loads(request_ollama(prompt, system, model=model, max_tokens=max_tokens, timeout=timeout, json_mode=True))
	required_keys = {"strengths", "weaknesses", "bullet_rewrites", "tailored_summary", "next_steps", "updated_resume"}
	if not required_keys.issubset(review):
		raise ValueError("The local model did not return the expected review fields.")
	return review


def request_local_resume_draft(profile: dict, draft: str) -> str:
	prompt = f"""
Improve this resume draft using only the facts supplied in the profile.
Make it polished, specific, ATS-friendly, and easy to scan. Strengthen the professional summary,
clarify bullet wording, use consistent section headings, and emphasize action and outcome when the
supplied facts support it. You may improve grammar and combine repeated wording.

Never invent employers, job titles, dates, locations, degrees, certifications, skills, metrics,
achievements, tools, responsibilities, or results. Do not add placeholder text. If a detail is
missing, leave it out. Return only the complete resume in plain text, with no commentary.

PROFILE:
{json.dumps(profile)[:12000]}

CURRENT DRAFT:
{draft[:14000]}
"""
	result = request_ollama(
		prompt,
		"You are a meticulous resume editor. Improve clarity and impact while preserving every fact exactly.",
		model=OLLAMA_FAST_MODEL,
		max_tokens=850,
		timeout=5,
	).strip()
	result = re.sub(r"^```(?:text|plaintext)?\s*|\s*```$", "", result, flags=re.IGNORECASE).strip()
	required_sections = [
		section for section in ("SUMMARY", "EXPERIENCE", "EDUCATION", "SKILLS", "PROJECTS", "CERTIFICATIONS", "ACHIEVEMENTS / AWARDS", "ADDITIONAL INFORMATION")
		if section in draft
	]
	if (
		len(result) < 120
		or profile.get("name", "").strip().lower() not in result.lower()
		or any(section not in result for section in required_sections)
	):
		raise ValueError("The local editor returned an incomplete resume draft.")
	return result + ("\n" if not result.endswith("\n") else "")


def raise_for_ai_response(response: requests.Response) -> None:
	if response.ok:
		return
	try:
		detail = response.json().get("error", {}).get("message", "")
	except ValueError:
		detail = ""
	if response.status_code == 429:
		raise AIServiceError(
			"OpenAI rejected the request with a 429. Your API key may be out of credits, "
			f"billing may not be active, or the account may be rate-limited. "
			f"{'Provider detail: ' + detail if detail else 'Check your OpenAI usage and billing page.'}"
		)
	if response.status_code in (401, 403):
		raise AIServiceError("OpenAI rejected the key. Check that it is active and copied completely.")
	try:
		response.raise_for_status()
	except requests.RequestException as error:
		raise AIServiceError(f"OpenAI could not complete the request: {error}") from error


@st.cache_data(show_spinner=False)
def request_ai_review(resume: str, job_description: str, api_key: str, mode: str = "fast") -> dict:
	is_deep = mode.lower() in {"deep think", "deep_think", "deep"}
	prompt = f"""
Review this resume against the target job description. Be specific, honest, and encouraging.
Do not invent experience, skills, employers, metrics, or education.

Return only valid JSON with these keys:
strengths: array of 3 concise strings
weaknesses: array of 3 concise strings
bullet_rewrites: array of 3 objects with keys original and rewrite
tailored_summary: one 2-3 sentence professional summary grounded only in the resume
next_steps: array of 3 concise strings
updated_resume: a complete improved resume in plain text, preserving all truthful facts from the original

RESUME:
{resume[:12000]}

TARGET JOB:
{job_description[:10000]}
"""
	response = requests.post(
		"https://api.openai.com/v1/chat/completions",
		headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
		json={
			"model": "gpt-4o-mini",
			"temperature": 0.2 if not is_deep else 0.45,
			"response_format": {"type": "json_object"},
			"messages": [
				{"role": "system", "content": "You are an expert resume editor and career coach. " + ("Think carefully and prioritize context, evidence, and honest improvement in depth." if is_deep else "Keep the feedback practical and concise.")},
				{"role": "user", "content": prompt},
			],
		},
		timeout=45,
	)
	raise_for_ai_response(response)
	content = response.json()["choices"][0]["message"]["content"]
	review = json.loads(content)
	required_keys = {"strengths", "weaknesses", "bullet_rewrites", "tailored_summary", "next_steps", "updated_resume"}
	if not required_keys.issubset(review):
		raise ValueError("The AI response did not contain the expected review fields.")
	return review


def _pick_variation(text: str, category: str, groups: list[list[str]]) -> str:
	"""Select a variation from the supplied pools while respecting the active RNG state.

	This keeps the function deterministic when callers seed the global random module,
	which is how the project tests exercise the variation behavior.
	"""
	parts = [random.choice(group) for group in groups]
	return " ".join(part.strip() for part in parts if part and part.strip())


def local_resume_chat_answer(question: str, resume: str, job_description: str, review: dict | None = None) -> str:
	q = question.lower()
	resume_lower = resume.lower()
	job_lower = job_description.lower()

	summary_variations = [
		"Your summary can feel sharper when it leads with your role, the value you create, and the kind of problems you solve.",
		"A concise summary works best when it names the role, your specialty, and the measurable impact you produce.",
		"The strongest summary connects your specialty, your target scope, and the outcomes you deliver in plain language.",
	]
	skills_variations = [
		"The strongest skills section matches the role without sounding forced.",
		"A cleaner skill match usually balances real capability with market language.",
		"Your skills work best when they show the most relevant tools and strengths first.",
	]
	bullet_variations = [
		"The strongest bullets show what changed, not just what you were responsible for.",
		"Your experience becomes sharper when each bullet answers what you did, for whom, and what improved.",
		"The clearest impact statements combine a clear action with a measurable result.",
	]
	education_variations = [
		"Education should stay concise and relevant to the role.",
		"The cleanest education section highlights the most important credential first.",
		"A calmer education layout usually supports your story without crowding the page.",
	]
	fit_variations = [
		"The best match is usually created when your summary, skills, and bullets point to the same story.",
		"The strongest fit comes from framing your experience around the problems the role actually solves.",
		"Your role alignment improves when the resume mirrors the job language without losing honesty.",
	]
	resume_variations = [
		"If you want a stronger resume, start with a sharper summary, clearer bullets, and more targeted job alignment.",
		"The biggest gains usually come from stronger action verbs, better evidence, and tighter role relevance.",
		"Your fastest improvement path often begins with fewer vague statements and more measurable impact.",
	]

	if any(term in q for term in ["summary", "profile", "headline", "about"]):
		return random.choice(summary_variations)
	if any(term in q for term in ["skills", "keywords", "ats", "screen"]):
		return random.choice(skills_variations)
	if any(term in q for term in ["bullet", "experience", "achievement", "impact"]):
		return random.choice(bullet_variations)
	if any(term in q for term in ["education", "degree", "school", "cert"]):
		return random.choice(education_variations)
	if any(term in q for term in ["fit", "match", "role", "target"]):
		return random.choice(fit_variations)
	if review and review.get("next_steps"):
		return "The clearest next steps are: " + "; ".join(review["next_steps"][:3]) + "."
	if "resume" in q or "cv" in q:
		return random.choice(resume_variations)
	return _pick_variation(q, "fallback", [
		["Start by narrowing the issue to one area", "The best next step is usually to sharpen one section at a time", "If you want a better resume, focus on one major improvement at a time"],
		["the summary", "the skills alignment", "the bullet evidence", "the target fit"],
		["and build from there for a cleaner, stronger result.", "so the document improves without losing authenticity.", "and the rest of the page becomes easier to trust."]
	])


def request_ai_chat(resume: str, job_description: str, review: dict, messages: list[dict], api_key: str) -> str:
	context = f"""
Resume:
{resume[:12000]}

Target job:
{job_description[:10000]}

Existing review:
{json.dumps(review)[:12000]}
"""
	chat_messages = [
		{
			"role": "system",
			"content": "You are a practical, encouraging resume coach. Give specific advice grounded only in the resume and target job. Never invent experience or credentials.",
		},
		{"role": "user", "content": context},
	]
	chat_messages.extend(messages[-8:])
	response = requests.post(
		"https://api.openai.com/v1/chat/completions",
		headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
		json={
			"model": "gpt-4o-mini",
			"temperature": 0.4,
			"messages": chat_messages,
		},
		timeout=45,
	)
	raise_for_ai_response(response)
	return response.json()["choices"][0]["message"]["content"].strip()


def request_local_chat(resume: str, job_description: str, review: dict, messages: list[dict], mode: str = "fast") -> str:
	prompt = f"""
Resume:
{resume[:12000]}

Target job:
{job_description[:10000]}

Existing review:
{json.dumps(review)[:12000]}

Conversation:
{json.dumps(messages[-8:])}
"""
	return request_ollama(
		prompt,
		"You are a practical, encouraging resume coach. Give specific advice grounded only in the resume and target job. Never invent experience or credentials.",
		model=OLLAMA_MODEL if mode.lower() == "deep think" else OLLAMA_FAST_MODEL,
		max_tokens=360 if mode.lower() == "deep think" else 220,
		timeout=18 if mode.lower() == "deep think" else 6,
	)


def normalize_phone(country_code: str, local_number: str) -> str:
	code = (country_code or "+1").strip()
	digits = re.sub(r"\D", "", local_number or "")
	if not digits:
		raise ValueError("Phone number is required.")
	if len(digits) == 11 and digits.startswith("1"):
		digits = digits[1:]
	if len(digits) != 10:
		raise ValueError("Phone number must contain exactly 10 digits after optional leading 1.")
	return f"{code} {digits[:3]} {digits[3:6]} {digits[6:]}"


def build_demo_profile() -> dict:
	return get_demo_variants()[0]["profile"]


def _make_demo_profile(name: str, title: str, email: str, city_country: str, summary: str, skills: list[str], experience: list[dict], education: list[str], projects: list[str], certifications: list[str], achievements: list[str], optional_sections: list[str]) -> dict:
	return {
		"name": name,
		"title": title,
		"email": email,
		"phone": "+1 415 512 3894",
		"city_country": city_country,
		"links": f"https://linkedin.com/in/{name.lower().replace(' ', '')} | https://github.com/{name.lower().replace(' ', '')}",
		"summary": summary,
		"skills": skills,
		"experience": experience,
		"education": education,
		"projects": projects,
		"certifications": certifications,
		"achievements": achievements,
		"optional_sections": optional_sections,
	}


def get_demo_variants() -> list[dict]:
	product_design_profiles = [
		_make_demo_profile(
			name="Aisha Patel",
			title="Senior Product Designer",
			email="aisha.patel.design@gmail.com",
			city_country="Seattle, United States",
			summary="Product designer with 6+ years of experience building human-centered B2B and SaaS experiences, leading discovery, design systems, and measurable product improvements.",
			skills=["Product Design", "UX Research", "Design Systems", "Figma", "User Flows", "Prototyping", "Accessibility", "Stakeholder Management"],
			experience=[
				{"role": "Senior Product Designer", "company": "Northstar Labs", "location": "Seattle, WA", "dates": "2022-Present", "bullets": ["Led the redesign of a workflow platform used by 10,000+ customers, improving onboarding completion by 28%.", "Built and maintained a design system that reduced duplicate UI work across 4 product squads and cut implementation time by 20%.", "Partnered with product and engineering to define user journeys, validate prototypes with users, and prioritize high-impact improvements."]},
				{"role": "Product Designer", "company": "FlowPilot", "location": "Remote", "dates": "2019-2022", "bullets": ["Designed end-to-end experiences for internal operations tools, improving task completion speed by 32%.", "Conducted 25+ usability interviews and translated findings into prioritized feature recommendations and clearer flows.", "Created accessible interaction patterns and documentation that improved design consistency across the product."]}
			],
			education=["B.A. in Interaction Design, University of Washington", "Certified UX Researcher, Nielsen Norman Group"],
			projects=["Design system migration - Figma, React - reduced duplicate components by 30% and accelerated feature delivery across teams", "Customer onboarding refresh - UX research, prototyping - improved activation rate by 24%"],
			certifications=["NN/g UX Certification - Nielsen Norman Group - 2024"],
			achievements=["Design Excellence Award - 2023", "Accessibility Champion - Northstar Labs - 2024"],
			optional_sections=["Volunteer mentor - Women in Design", "Languages: English, Spanish"],
		),
		_make_demo_profile(
			name="Mateo Silva",
			title="UX Product Designer",
			email="mateo.silva.design@gmail.com",
			city_country="Austin, United States",
			summary="UX designer focused on simplifying complex workflows, running discovery, and turning product insights into clear team-wide experiences.",
			skills=["UX Design", "Journey Mapping", "Interaction Design", "Figma", "Research Synthesis", "Service Design", "Usability Testing", "Content Strategy"],
			experience=[
				{"role": "UX Product Designer", "company": "Signal Forge", "location": "Austin, TX", "dates": "2021-Present", "bullets": ["Redesigned a B2B dashboard used by 8,000+ operators, reducing task time by 36%.", "Led moderated interviews and synthesized findings into a prioritized roadmap across 3 squads.", "Worked across product, marketing, and engineering to align the customer journey and improve adoption."]},
				{"role": "Product Designer", "company": "Cinder Studio", "location": "Remote", "dates": "2018-2021", "bullets": ["Designed onboarding and reporting flows for SaaS clients, improving conversion by 19%.", "Created reusable patterns that accelerated project delivery and reduced design debt.", "Partnered with founders to refine messaging and product priorities from customer feedback."]}
			],
			education=["B.S. in Visual Communication, University of Texas"],
			projects=["Operations dashboard redesign - workflow analysis - reduced support tickets by 22%", "Discovery sprint program - interviews and prototypes - improved roadmap clarity for product teams"],
			certifications=["Google UX Design Certificate - 2022"],
			achievements=["People's Choice Award - 2021"],
			optional_sections=["Mentor - design bootcamp", "Volunteer for civic UX projects"],
		),
		_make_demo_profile(
			name="Nina Hassan",
			title="Senior Visual Designer",
			email="nina.hassan.design@gmail.com",
			city_country="Toronto, Canada",
			summary="Visual and product designer combining systems thinking, accessibility, and experimentation to create polished customer experiences.",
			skills=["Visual Design", "Design Systems", "Accessibility", "Illustration", "Figma", "Brand Systems", "Research", "Prototyping"],
			experience=[
				{"role": "Senior Visual Designer", "company": "North Peak", "location": "Toronto, ON", "dates": "2022-Present", "bullets": ["Refined product experience language and visual patterns for a fintech platform serving 40,000+ users.", "Created accessible UI components that improved compliance and reduced design review cycles.", "Collaborated with PMs and engineers to standardize design decisions across mobile and web."]},
				{"role": "Product Designer", "company": "Bluewave Media", "location": "Remote", "dates": "2019-2022", "bullets": ["Designed marketing and product web experiences that increased leads by 27%.", "Built landing page systems and experimentation flows for campaign optimization.", "Partnered closely with content teams to align story, visuals, and conversion goals."]}
			],
			education=["B.A. in Graphic Design, Ryerson University"],
			projects=["Accessibility audit for web app - improved color contrast and keyboard support - raised usability score by 31%", "Landing page optimization - A/B testing - lifted demo requests by 18%"],
			certifications=["WCAG Accessibility Specialist - 2023"],
			achievements=["Design Impact Award - 2024"],
			optional_sections=["Design volunteer - community health initiative", "Speaker - Design Ops Meetup"],
		),
		_make_demo_profile(
			name="Priya Nair",
			title="Product Designer, Growth",
			email="priya.nair.design@gmail.com",
			city_country="London, United Kingdom",
			summary="Growth-focused product designer with a strong track record in experimentation, onboarding optimization, and clear cross-functional product decision-making.",
			skills=["Growth Design", "Experimentation", "A/B Testing", "UX Writing", "Figma", "Analytics", "Prototyping", "Research"],
			experience=[
				{"role": "Product Designer, Growth", "company": "OrbitIQ", "location": "London, UK", "dates": "2021-Present", "bullets": ["Improved acquisition funnel conversion by 24% through growth experiments and onboarding redesigns.", "Partnered with marketing and data teams to define drop-off points and turn insights into prioritized UX fixes.", "Built reusable experiment templates to support faster, more efficient testing across channels."]},
				{"role": "UX Designer", "company": "Motive Labs", "location": "Remote", "dates": "2018-2021", "bullets": ["Designed onboarding and lifecycle experiences for fintech customers, improving activation by 21%.", "Created user-friendly educational flows that reduced customer confusion and support tickets.", "Translated customer interviews into design requirements that informed roadmap planning."]}
			],
			education=["M.A. in Human-Centered Design, Royal College of Art"],
			projects=["Activation optimization - onboarding journey - lifted customer activation by 21%", "Experiment framework - prototype testing - accelerated release planning across teams"],
			certifications=["CXL Growth Design Certificate - 2023"],
			achievements=["Growth Design Excellence - 2024"],
			optional_sections=["Volunteer mentor - Women in Product", "Languages: English, Hindi"],
		),
		_make_demo_profile(
			name="Daniel Brooks",
			title="Senior UX Designer",
			email="daniel.brooks.design@gmail.com",
			city_country="New York, United States",
			summary="UX designer with experience shaping enterprise software, supporting discovery work, and leading practical design improvements with measurable outcomes.",
			skills=["UX Design", "User Research", "Design Strategy", "Figma", "Accessibility", "Service Design", "Product Thinking", "Stakeholder Communication"],
			experience=[
				{"role": "Senior UX Designer", "company": "Northframe", "location": "New York, NY", "dates": "2022-Present", "bullets": ["Led UX improvements across an internal operations suite, reducing training time by 30%.", "Worked with product managers to align feature roadmaps with measurable user and business outcomes.", "Built design reviews and lightweight testing rituals that improved product decision quality."]},
				{"role": "UX Designer", "company": "Harbor Systems", "location": "Remote", "dates": "2018-2022", "bullets": ["Improved internal workflow navigation and documentation, reducing task friction across departments.", "Performed usability reviews and analyzed support data to guide improvement priorities.", "Helped create consistent workflow patterns for a growing product operation."]}
			],
			education=["B.A. in Human Computer Interaction, Rochester Institute of Technology"],
			projects=["Knowledge base redesign - content architecture - reduced support friction by 18%", "Workflow improvement sprint - design review process - shortened decision cycles by 25%"],
			certifications=["UX Certification - 2023"],
			achievements=["Innovation in UX Award - 2022"],
			optional_sections=["Volunteer UX mentor", "Languages: English, French"],
		),
		_make_demo_profile(
			name="Sofia Martinez",
			title="Product Designer, AI",
			email="sofia.martinez.ai@gmail.com",
			city_country="San Francisco, United States",
			summary="Product designer creating AI-enabled experiences with a focus on trust, clarity, and user journeys that make advanced features feel easy to understand.",
			skills=["AI Product Design", "Prompt UX", "Research", "Interaction Design", "Figma", "Design Systems", "Analytics", "UX Writing"],
			experience=[
				{"role": "Product Designer, AI", "company": "BrightPilot", "location": "San Francisco, CA", "dates": "2022-Present", "bullets": ["Designed AI workflows that improved idea-to-output speed by 40% for internal teams.", "Created trust-building patterns for complex AI experiences and improved completion confidence.", "Partnered with researchers and engineers to test effective agent interactions and edge cases."]},
				{"role": "UX Designer", "company": "Nova Labs", "location": "Remote", "dates": "2019-2022", "bullets": ["Designed data-heavy products for operations teams, simplifying complex actions and decisions.", "Led usability testing for automation features and translated findings into design changes.", "Standardized interaction patterns across dashboard experiences and embedded workflows."]}
			],
			education=["M.S. in Human-Centered Design, Stanford University"],
			projects=["AI workflow onboarding - trust design - increased feature adoption by 32%", "Alert explanation redesign - clear service health communication - reduced escalations by 15%"],
			certifications=["Human-AI Interaction Certificate - 2024"],
			achievements=["Best AI Experience Award - 2024"],
			optional_sections=["Speaker - AI Experience Summit", "Volunteer design mentor"],
		),
		_make_demo_profile(
			name="Ethan Clark",
			title="Senior UX Researcher & Designer",
			email="ethan.clark.design@gmail.com",
			city_country="Chicago, United States",
			summary="Research-driven designer helping teams turn customer insight into simple, high-confidence decisions and product experiences that scale.",
			skills=["UX Research", "Design Strategy", "Interviewing", "Journey Mapping", "Wireframing", "Figma", "Data Synthesis", "Stakeholder Workshops"],
			experience=[
				{"role": "Senior UX Researcher & Designer", "company": "Harbor One", "location": "Chicago, IL", "dates": "2021-Present", "bullets": ["Led discovery across B2B workflows and translated findings into roadmap recommendations.", "Designed and tested experiences for complex internal tools, improving completion rates by 26%.", "Facilitated user interviews and stakeholder alignment to reduce product ambiguity."]},
				{"role": "UX Designer", "company": "Define Studio", "location": "Remote", "dates": "2017-2021", "bullets": ["Designed customer journeys for digital platforms and simplified multi-step processes.", "Created prototypes for concept testing and shared insight-driven recommendations with product teams.", "Improved handoff quality by defining clearer design specifications."]}
			],
			education=["B.A. in Psychology and Design, DePaul University"],
			projects=["Customer journey redesign - research synthesis - improved task completion by 29%", "Prototype testing program - reduced cross-team rework by 18%"],
			certifications=["Nielsen Norman UX Research - 2023"],
			achievements=["Research Impact Award - 2024"],
			optional_sections=["UX volunteer - local nonprofit", "Workshop facilitator"],
		),
		_make_demo_profile(
			name="Grace Park",
			title="Product Designer, Mobile",
			email="grace.park.design@gmail.com",
			city_country="Seoul, South Korea",
			summary="Mobile product designer helping teams create intuitive, conversion-focused interfaces for high-growth consumer products.",
			skills=["Mobile UX", "iOS Design", "Product Design", "Research", "Figma", "Usability Testing", "Design Systems", "Analytics"],
			experience=[
				{"role": "Product Designer, Mobile", "company": "Nimble App", "location": "Seoul, KR", "dates": "2021-Present", "bullets": ["Redesigned mobile onboarding and retention journeys, increasing activation by 23%.", "Worked with engineering to deliver new core experiences leading to a higher app engagement score.", "Built reusable mobile components and enabled a faster release cadence across teams."]},
				{"role": "UX Designer", "company": "Pixel Harbor", "location": "Remote", "dates": "2018-2021", "bullets": ["Designed consumer experiences for mobile products and improved retention through simplified flows.", "Ran usability tests and translated research into actionable design updates.", "Built design QA standards for smoother launch readiness."]}
			],
			education=["B.A. in Digital Media Design, Korea National University of Arts"],
			projects=["Mobile journey redesign - conversion uplift - +18% retention performance", "App experimentation program - design testing - improved release decisions"],
			certifications=["Mobile UX Certification - 2022"],
			achievements=["App Experience Winner - 2023"],
			optional_sections=["Language skills: English, Korean", "Volunteer mentor for university design club"],
		),
		_make_demo_profile(
			name="Hugo Mendes",
			title="Senior Product Designer, Commerce",
			email="hugo.mendes.design@gmail.com",
			city_country="Lisbon, Portugal",
			summary="Commerce-focused product designer building product flows that connect customer needs, sharper experiences, and measurable commercial performance.",
			skills=["E-commerce UX", "Checkout Design", "Analytics", "Research", "Figma", "A/B Testing", "Design Systems", "Stakeholder Alignment"],
			experience=[
				{"role": "Senior Product Designer, Commerce", "company": "CrestCart", "location": "Lisbon, PT", "dates": "2020-Present", "bullets": ["Redesigned checkout and product discovery flows, increasing conversion by 34%.", "Used experimentation and funnels to identify the biggest friction points for customers.", "Collaborated with product and engineering to improve customer trust and purchase confidence."]},
				{"role": "UX Designer", "company": "TrendLane", "location": "Remote", "dates": "2016-2020", "bullets": ["Designed discovery and merchandising experiences for online storefronts.", "Built prototypes to test offers and promotional flows against user expectations.", "Improved consistency across merchandising pages and product detail interactions."]}
			],
			education=["B.S. in Interaction Design, University of Lisbon"],
			projects=["Checkout optimization - friction analysis - conversion uplift of 27%", "Merchandising redesign - search and filters - improved product discovery"],
			certifications=["CXL UX Strategy - 2022"],
			achievements=["Commerce Experience Award - 2024"],
			optional_sections=["Volunteer - digital inclusion project", "Languages: English, Portuguese"],
		),
		_make_demo_profile(
			name="Leah Thompson",
			title="Design Systems Product Designer",
			email="leah.thompson.design@gmail.com",
			city_country="Denver, United States",
			summary="Design systems product designer translating platform complexity into clear scalable systems that help teams ship faster with more consistency.",
			skills=["Design Systems", "Design Tokens", "Product Design", "Figma", "Documentation", "Accessibility", "Component Design", "Research"],
			experience=[
				{"role": "Design Systems Product Designer", "company": "Summit Cloud", "location": "Denver, CO", "dates": "2021-Present", "bullets": ["Built and scaled a design system used by 7 product teams, accelerating design and development cycles by 22%.", "Created documentation and governance patterns that reduced inconsistent UI decisions across the platform.", "Partnered with engineering to refine tokens, accessibility standards, and component adoption."]},
				{"role": "Product Designer", "company": "Bright Path", "location": "Remote", "dates": "2018-2021", "bullets": ["Designed SaaS workflows and standardized interactions across multiple product surfaces.", "Improved feature velocity by creating component libraries that were easy for teams to adopt.", "Created testing rituals and review processes to reduce rework and improve consistency."]}
			],
			education=["B.A. in Interactive Design, University of Colorado Boulder"],
			projects=["Design system rollout - component adoption - reduced UI variance by 35%", "Component governance guide - cross-team documentation - improved design handoff quality"],
			certifications=["DesignOps Certification - 2023"],
			achievements=["System Design Award - 2024"],
			optional_sections=["Volunteer design ops mentor", "Languages: English, Spanish"],
		),
	]

	software_engineering_profiles = [
		_make_demo_profile(
			name="Daniel Kim",
			title="Senior Full-Stack Engineer",
			email="daniel.kim.engineer@gmail.com",
			city_country="Seattle, United States",
			summary="Full-stack engineer with 6+ years building scalable web products, improving platform reliability, and simplifying developer workflows.",
			skills=["JavaScript", "Python", "React", "Node.js", "SQL", "AWS", "CI/CD", "System Design"],
			experience=[
				{"role": "Senior Full-Stack Engineer", "company": "Northstar Cloud", "location": "Seattle, WA", "dates": "2022-Present", "bullets": ["Built internal analytics and workflow tooling used by 10,000+ users, reducing cycle time by 30%.", "Improved application reliability by reducing deployment failures and improving runbook automation.", "Collaborated with product and design to ship several customer-facing features on a rapid release cadence."]},
				{"role": "Software Engineer", "company": "Signal Forge", "location": "Remote", "dates": "2019-2022", "bullets": ["Developed reusable frontend services and APIs for mature multi-tenant SaaS features.", "Improved page responsiveness and reduced client-side bottlenecks across the platform.", "Wrote tests and instrumentation that improved release confidence and observability."]}
			],
			education=["B.S. in Computer Science, University of Washington"],
			projects=["Observability platform - logs and metrics - reduced incident triage time by 35%", "Developer workflow automation - CI/CD - cut release time by 22%"],
			certifications=["AWS Solutions Architect Associate - 2024"],
			achievements=["Engineering Impact Award - 2023"],
			optional_sections=["Volunteer mentor for coding bootcamp", "Languages: English, Korean"],
		),
		_make_demo_profile(
			name="Alicia Ross",
			title="Backend Engineer",
			email="alicia.ross.engineer@gmail.com",
			city_country="Austin, United States",
			summary="Backend engineer focused on distributed systems, API design, and performance improvements that make critical customer experiences more reliable.",
			skills=["Python", "Go", "PostgreSQL", "Kafka", "Docker", "Kubernetes", "REST APIs", "Microservices"],
			experience=[
				{"role": "Backend Engineer", "company": "FlowPilot", "location": "Austin, TX", "dates": "2021-Present", "bullets": ["Designed and maintained APIs supporting high-traffic customer workflows with strong uptime requirements.", "Optimized query patterns and caching to reduce latency for high-volume requests by 42%.", "Shipped resilient background job processing and alerting for critical platform events."]},
				{"role": "Software Engineer", "company": "OpsLab", "location": "Remote", "dates": "2018-2021", "bullets": ["Built internal services for operations analytics and automation frameworks.", "Improved service reliability and metric visibility across distributed systems.", "Introduced test coverage and deployment gates that reduced regressions."]}
			],
			education=["B.S. in Software Engineering, University of Texas"],
			projects=["API performance tuning - Redis and SQL optimization - reduced p95 latency by 40%", "Event pipeline modernization - Kafka - improved throughput by 28%"],
			certifications=["Certified Kubernetes Administrator - 2023"],
			achievements=["Platform Reliability Award - 2024"],
			optional_sections=["Volunteer software mentor", "Languages: English, Spanish"],
		),
		_make_demo_profile(
			name="Maya Chen",
			title="Frontend Engineer",
			email="maya.chen.engineer@gmail.com",
			city_country="San Francisco, United States",
			summary="Frontend engineer building polished interfaces, improving performance, and collaborating closely with design and product on customer-facing experiences.",
			skills=["React", "TypeScript", "CSS", "Testing Library", "Node.js", "Web Performance", "Next.js", "Accessibility"],
			experience=[
				{"role": "Frontend Engineer", "company": "Lattice Studio", "location": "San Francisco, CA", "dates": "2021-Present", "bullets": ["Built responsive product experiences used by enterprise customers and improved interaction quality for complex workflows.", "Reduced bundle size and JavaScript load time by 38% through performance optimization.", "Worked closely with designers to turn UX prototypes into solid production features."]},
				{"role": "Web Engineer", "company": "Studio North", "location": "Remote", "dates": "2018-2021", "bullets": ["Developed marketing and product pages with scalable component design and strong visual consistency.", "Improved accessibility across apps and reduced support issues tied to poor keyboard navigation.", "Helped establish frontend quality standards with unit and integration tests."]}
			],
			education=["B.S. in Computer Engineering, UC Berkeley"],
			projects=["Design system frontend library - React - reduced UI build time by 20%", "Performance overhaul - Lighthouse improvements - raised mobile score by 30 points"],
			certifications=["Google Professional Cloud Developer - 2022"],
			achievements=["Frontend Excellence Award - 2024"],
			optional_sections=["Volunteer mentor for women in engineering", "Languages: English, Mandarin"],
		),
		_make_demo_profile(
			name="Marcus Hill",
			title="Platform Engineer",
			email="marcus.hill.engineer@gmail.com",
			city_country="Chicago, United States",
			summary="Platform engineer with experience improving developer productivity, deploying reliable infrastructures, and creating automation that reduces operational drag.",
			skills=["Terraform", "AWS", "Kubernetes", "Linux", "Python", "Infrastructure", "CI/CD", "Monitoring"],
			experience=[
				{"role": "Platform Engineer", "company": "Northwind Data", "location": "Chicago, IL", "dates": "2021-Present", "bullets": ["Built CI/CD and infrastructure automation that reduced deployment time from 2 hours to 20 minutes.", "Improved platform observability and standardization for 15 engineering teams across the organization.", "Created self-service tooling that made environment setup faster and safer for developers."]},
				{"role": "DevOps Engineer", "company": "Arc Systems", "location": "Remote", "dates": "2018-2021", "bullets": ["Managed cloud infrastructure, deployment workflows, and incident response patterns.", "Improved release safety and service health with better monitoring and rollback tooling.", "Documented systems and built operational guardrails to reduce production risk."]}
			],
			education=["B.S. in Computer Science, Illinois Institute of Technology"],
			projects=["Infrastructure automation - Terraform - cut provisioning time by 70%", "Platform reliability initiative - logging and alerts - reduced downtime by 25%"],
			certifications=["Terraform Associate - 2023"],
			achievements=["Platform Reliability Award - 2024"],
			optional_sections=["Volunteer STEM mentor", "Languages: English, Spanish"],
		),
		_make_demo_profile(
			name="Iris Gomez",
			title="Machine Learning Engineer",
			email="iris.gomez.engineer@gmail.com",
			city_country="New York, United States",
			summary="Machine learning engineer building data products, evaluating model quality, and delivering user-facing AI features that stay practical and measurable.",
			skills=["Python", "PyTorch", "ML Pipelines", "Data Engineering", "MLOps", "SQL", "Model Evaluation", "Feature Engineering"],
			experience=[
				{"role": "Machine Learning Engineer", "company": "Vantage AI", "location": "New York, NY", "dates": "2022-Present", "bullets": ["Built and deployed prediction models that improved recommendation quality and reduced manual review effort.", "Created evaluation pipelines and monitoring for production models, increasing trust and reducing drift.", "Partnered with product teams to identify high-impact AI use cases and measurable success metrics."]},
				{"role": "Data Engineer", "company": "Insight Grid", "location": "Remote", "dates": "2019-2022", "bullets": ["Built data pipelines for analytics and experimentation, improving data quality and team decision-making.", "Optimized large-scale ETL jobs and warehouse models to support better product insights.", "Documented data architecture and supported cross-functional experimentation initiatives."]}
			],
			education=["M.S. in Computer Science, Columbia University"],
			projects=["Recommendation model tuning - ranking optimization - lifted click-through rate by 15%", "MLOps pipeline rollout - drift monitoring - reduced model incidents by 30%"],
			certifications=["AWS Machine Learning Specialty - 2024"],
			achievements=["AI Product Impact Award - 2024"],
			optional_sections=["Volunteer mentor for AI education", "Languages: English, Spanish"],
		),
		_make_demo_profile(
			name="Owen Patel",
			title="Data Engineer",
			email="owen.patel.engineer@gmail.com",
			city_country="Boston, United States",
			summary="Data engineer designing robust pipelines and trusted data products that support product analytics, experimentation, and team-level decision making.",
			skills=["SQL", "Python", "Spark", "Airflow", "Warehouse Design", "ETL", "Big Data", "Data Modeling"],
			experience=[
				{"role": "Data Engineer", "company": "Echo Metrics", "location": "Boston, MA", "dates": "2021-Present", "bullets": ["Built ETL and warehouse pipelines that accelerated reporting and simplified access to business-critical datasets.", "Reduced data processing time by 50% through efficient orchestration and query tuning.", "Worked with product and analytics teams to create reliable event tracking and measurement standards."]},
				{"role": "Analytics Engineer", "company": "North Peak", "location": "Remote", "dates": "2018-2021", "bullets": ["Developed metrics definitions and analysis pipelines to support reporting and experimentation.", "Improved data quality and schema governance across multiple business domains.", "Enabled faster downstream analysis by standardizing sources and transformation layers."]}
			],
			education=["B.S. in Statistics and Computer Science, Boston University"],
			projects=["Warehouse redesign - data model optimization - reduced reporting latency by 45%", "Event taxonomy project - instrumentation standards - improved analytics accuracy"],
			certifications=["Databricks Certified Associate - 2023"],
			achievements=["Data Infrastructure Award - 2024"],
			optional_sections=["Volunteer Data for Good", "Languages: English, Hindi"],
		),
		_make_demo_profile(
			name="Sara Nguyen",
			title="QA Automation Engineer",
			email="sara.nguyen.engineer@gmail.com",
			city_country="Dallas, United States",
			summary="QA automation engineer building reliable test strategies and automation pipelines that improve release confidence across web and API products.",
			skills=["Python", "Selenium", "Playwright", "API Testing", "CI/CD", "Test Automation", "Quality Strategy", "JavaScript"],
			experience=[
				{"role": "QA Automation Engineer", "company": "LaunchWorks", "location": "Dallas, TX", "dates": "2021-Present", "bullets": ["Built automated test suites that reduced regression testing time from 8 hours to 1.5 hours.", "Improved test coverage for critical customer workflows and reduced production issues after releases.", "Partnered with engineers to identify flaky tests and improve quality gates in the deployment pipeline."]},
				{"role": "Software Engineer in Test", "company": "Pixel Harbor", "location": "Remote", "dates": "2018-2021", "bullets": ["Created automation for web and API flows to support faster validation of software releases.", "Improved regression detection and reduced time spent on repetitive validation tasks.", "Built dashboards and reporting for quality metrics used across delivery teams."]}
			],
			education=["B.S. in Computer Science, University of Texas at Dallas"],
			projects=["Regression suite modernization - Playwright - reduced release regressions by 40%", "API contract testing program - quality automation - improved delivery confidence"],
			certifications=["ISTQB Foundation - 2022"],
			achievements=["Quality Champion Award - 2024"],
			optional_sections=["Volunteer mentor for software testing community", "Languages: English, Vietnamese"],
		),
		_make_demo_profile(
			name="Marcus Lee",
			title="DevOps Engineer",
			email="marcus.lee.engineer@gmail.com",
			city_country="Denver, United States",
			summary="DevOps engineer focused on infrastructure reliability, automation, and release quality for modern cloud-native products.",
			skills=["Docker", "Kubernetes", "Terraform", "AWS", "Grafana", "Prometheus", "Linux", "GitHub Actions"],
			experience=[
				{"role": "DevOps Engineer", "company": "Summit Cloud", "location": "Denver, CO", "dates": "2021-Present", "bullets": ["Built deployment automation for cloud services, cutting rollout time and reducing human error.", "Established observability and alerting standards that improved on-call efficiency and service uptime.", "Mentored engineering teams on reliability best practices and operational readiness."]},
				{"role": "Systems Engineer", "company": "Cobalt Works", "location": "Remote", "dates": "2018-2021", "bullets": ["Managed Linux environments and automated systems operations for critical workloads.", "Improved backup, failover, and incident response processes to support uptime goals.", "Supported application teams with deployment patterns and environment consistency."]}
			],
			education=["B.S. in Information Technology, University of Colorado Denver"],
			projects=["Infrastructure refactor - Kubernetes - reduced deployment failures by 33%", "Monitoring platform rollout - Prometheus/Grafana - improved incident detection"],
			certifications=["AWS DevOps Professional - 2024"],
			achievements=["Operational Excellence Award - 2024"],
			optional_sections=["Volunteer IT mentor", "Languages: English, Korean"],
		),
		_make_demo_profile(
			name="Lena Fischer",
			title="Security Engineer",
			email="lena.fischer.engineer@gmail.com",
			city_country="Berlin, Germany",
			summary="Security engineer building safer systems, hardening cloud environments, and turning security concerns into practical product and infrastructure improvements.",
			skills=["Security Engineering", "Cloud Security", "DevSecOps", "Terraform", "Python", "AWS", "Identity", "Monitoring"],
			experience=[
				{"role": "Security Engineer", "company": "Cobalt Works", "location": "Berlin, DE", "dates": "2021-Present", "bullets": ["Hardened cloud infrastructure and reduced attack surface through policy, secrets, and identity improvements.", "Built security automation for CI/CD to catch vulnerabilities earlier in delivery workflows.", "Partnered with engineering teams to reduce friction while improving product and platform security."]},
				{"role": "Systems Engineer", "company": "Bluewave Media", "location": "Remote", "dates": "2018-2021", "bullets": ["Managed server security baselines and policy standards for production environments.", "Improved monitoring and incident response around infrastructure vulnerabilities.", "Helped teams implement secure development practices and safer deployment patterns."]}
			],
			education=["M.S. in Cybersecurity, Technical University of Berlin"],
			projects=["Cloud security hardening - IAM and policy review - reduced risk exposures by 46%", "Vulnerability automation - CI/CD - improved remediation time by 35%"],
			certifications=["AWS Security Specialty - 2024"],
			achievements=["Security Excellence Award - 2024"],
			optional_sections=["Volunteer cyber safety educator", "Languages: English, German"],
		),
		_make_demo_profile(
			name="Noah Williams",
			title="Site Reliability Engineer",
			email="noah.williams.engineer@gmail.com",
			city_country="Portland, United States",
			summary="Site reliability engineer improving production resilience, reducing toil, and creating scalable reliability patterns for modern cloud-native services.",
			skills=["SRE", "Kubernetes", "Observability", "Linux", "Python", "Terraform", "Incident Response", "Monitoring"],
			experience=[
				{"role": "Site Reliability Engineer", "company": "Northwind Data", "location": "Portland, OR", "dates": "2021-Present", "bullets": ["Improved platform reliability by reducing incident recovery time and strengthening alerting across critical services.", "Automated operational workflows and runbooks, reducing toil and speeding up incident response efforts.", "Partnered with application teams to improve service-level objectives and support long-term scaling."]},
				{"role": "Systems Engineer", "company": "Westwind Labs", "location": "Remote", "dates": "2018-2021", "bullets": ["Managed deployments, cloud environments, and production support patterns for multiple services.", "Improved system observability and reliability guardrails for development and production workloads.", "Worked cross-functionally to reduce risk and improve service ownership across engineering teams."]}
			],
			education=["B.S. in Computer Science, Oregon State University"],
			projects=["Reliability automation - runbook and alerting - reduced incident response time by 35%", "Service lifecycle improvement - standards and SLOs - improved uptime across core workloads"],
			certifications=["Google Cloud Professional SRE - 2024"],
			achievements=["Reliability Excellence Award - 2024"],
			optional_sections=["Volunteer STEM mentor", "Languages: English, Spanish"],
		),
	]

	job_descriptions = {
		"Product Design": [
			"Senior Product Designer\nWe are looking for a Senior Product Designer to shape elegant, intuitive product experiences for an enterprise SaaS platform. Responsibilities include leading discovery research, translating customer pain points into flows and interactions, and defining design systems that scale across product teams. We need someone comfortable with Figma, usability testing, accessibility, and stakeholder collaboration. The ideal candidate brings strong UX research skills, a user-centered mindset, and a track record of improving activation and onboarding.",
			"UX Product Designer\nWe need a UX Product Designer to support discovery, service design, and interface improvements across a customer-facing platform. The role includes gathering user insight, turning research into prototypes, and collaborating closely with PMs and engineers. Experience with Figma, journey mapping, and usability testing is essential, and candidates should be comfortable shipping work in high-velocity product teams.",
			"Senior Visual Designer\nWe are searching for a Senior Visual Designer to help define the look, feel, and interaction patterns of a digital product. Responsibilities include creating polished interfaces, building accessible design systems, and partnering with product teams to maintain consistency across web and mobile experiences. Strong visual design fundamentals and Figma skill are expected.",
			"Product Designer, Growth\nWe are hiring a Product Designer focused on growth and conversion. This role owns onboarding, experimentation, and funnel work across the customer journey. The ideal candidate can turn customer data and interviews into actionable design changes, run A/B tests, and work closely with marketing and product teams to improve user activation and retention.",
			"Senior UX Designer\nWe are seeking a Senior UX Designer to improve critical enterprise workflows. The role should drive discovery with users, propose strong interactions and information architecture, and help teams make clear decisions. You should be comfortable collaborating with stakeholders and translating customer pain points into elegant product solutions.",
			"Product Designer, AI\nWe need a Product Designer working on AI-powered experiences to improve trust, clarity, and usability. Responsibilities include defining user journeys for new features, reducing cognitive load, and shaping the interface language for AI interactions. Candidates should be comfortable working with research, prototyping, and product teams on complex, emerging workflows.",
			"Senior UX Researcher & Designer\nWe are looking for a research-driven designer who can both investigate and design. The role includes leading discovery, synthesizing user insights, and turning findings into clear flows and prototypes. Great communication and product thinking are essential for helping teams understand user needs and prioritize improvements.",
			"Product Designer, Mobile\nWe are seeking a Mobile Product Designer to shape the next generation of app experiences. Responsibilities include designing intuitive flows, supporting usability testing, and collaborating with engineering and product to launch high-quality mobile features. Strong mobile UX judgment and a data-driven mindset are required.",
			"Senior Product Designer, Commerce\nWe are hiring a commerce-focused Product Designer to improve the customer journey across search, landing pages, and checkout. The role blends UX strategy, experimentation, and strong cross-functional execution. You should be able to use analytics and research to identify friction, make tradeoffs, and deliver meaningful conversion gains.",
			"Design Systems Product Designer\nWe are looking for a Design Systems Product Designer to shape scalable UI patterns and team-level design standards. The position includes component design, design governance, accessibility guidance, and collaboration with engineering to improve consistency across workflows. The ideal candidate brings strong systems thinking and polished execution.",
		],
		"Software Engineering": [
			"Senior Full-Stack Engineer\nWe are looking for a Senior Full-Stack Engineer to design and deliver customer-facing features across the platform. Responsibilities include building frontend experiences, maintaining backend APIs, and collaborating with product and design teams to solve technical problems at scale. Strong experience with JavaScript, Python, React, and cloud deployments is a must.",
			"Backend Engineer\nWe are hiring a Backend Engineer to design reliable APIs, optimize database access, and improve service performance for customer workflows. The role requires strong Python or Go experience, distributed system design knowledge, and a focus on scalability, observability, and operational excellence.",
			"Frontend Engineer\nWe are seeking a Frontend Engineer with strong React and TypeScript experience to build polished, accessible interfaces. The role includes collaborating with designers, shipping production-ready UI, and creating performant customer experiences. Good communication and strong product instincts are valued.",
			"Platform Engineer\nWe need a Platform Engineer to make our deployment, infrastructure, and developer workflows more reliable and scalable. You should be comfortable with Terraform, Kubernetes, CI/CD, and cloud operations while helping engineering teams ship faster with less operational risk.",
			"Machine Learning Engineer\nWe are looking for a Machine Learning Engineer to build and improve production ML systems. Responsibilities include model evaluation, experimentation, feature preparation, and deployment workflows. Strong Python, ML tooling, and production-minded thinking are essential in this role.",
			"Data Engineer\nWe are hiring a Data Engineer to build pipelines that support analytics, reporting, and product decision-making. The role includes data modeling, ETL design, and warehouse optimization while working closely with analytics and product teams on high-trust data products.",
			"QA Automation Engineer\nWe are looking for a QA Automation Engineer to elevate release quality and reduce manual testing overhead. The role includes building automation for web and API flows, improving test coverage, and partnering with engineers to accelerate delivery while maintaining quality standards.",
			"DevOps Engineer\nWe are seeking a DevOps Engineer to improve deployment speed, observability, and cloud operations. The role covers infrastructure as code, monitoring, automation, and environment consistency across service teams. Strong Linux, AWS, and CI/CD experience is important.",
			"Security Engineer\nWe are hiring a Security Engineer to help harden our cloud and production environments. The role includes security reviews, IAM improvements, vulnerability remediation, and CI/CD security automation. Strong communication and a practical approach to risk reduction are essential.",
			"Site Reliability Engineer\nWe need a Site Reliability Engineer to ensure our systems stay resilient and observable while supporting a growing service footprint. This role includes incident response, automation, infrastructure improvements, and service reliability practices across a production platform.",
		],
	}

	variants = []
	for family, profiles in (("Product Design", product_design_profiles), ("Software Engineering", software_engineering_profiles)):
		for i, profile in enumerate(profiles):
			variants.append({
				"job_family": family,
				"profile": profile,
				"job_description": job_descriptions[family][i],
			})
	return variants


def build_demo_job_description() -> str:
	return get_demo_variants()[0]["job_description"]


def build_demo_resume_text(profile: dict | None = None) -> str:
	profile = profile or build_demo_profile()
	return polish_structured_resume(profile, generate_resume_from_profile(profile))


def profile_quality_issues(profile: dict) -> list[str]:
	profile = profile or {}
	combined = " ".join(str(value) for value in profile.values()).lower()
	suspicious_terms = ("asdf", "qwerty", "lorem ipsum", "blah", "test test", "troll", "joke resume")
	if any(term in combined for term in suspicious_terms):
		return ["This profile looks like placeholder or joke content. Add your real details so I can build a useful resume."]

	issues = []
	if len(str(profile.get("name") or "").strip()) < 2:
		issues.append("your full name")
	if len(str(profile.get("title") or "").strip()) < 2:
		issues.append("your target or professional title")
	if "@" not in str(profile.get("email") or ""):
		issues.append("a professional email address")
	if not str(profile.get("summary") or "").strip():
		issues.append("a 2-4 line professional summary")
	if not str(profile.get("city_country") or "").strip():
		issues.append("your city and country")
	if len(profile.get("skills") or []) < 2:
		issues.append("at least two relevant skills")
	if not profile.get("experience") and not profile.get("projects"):
		issues.append("work experience or projects")
	if not profile.get("education"):
		issues.append("education or training")
	return issues

def generate_resume_from_profile(profile: dict) -> str:
	profile = profile or {}
	name = (profile.get("name") or "Your Name").strip()
	title = (profile.get("title") or "Professional").strip()
	email = (profile.get("email") or "").strip()
	phone = (profile.get("phone") or "").strip()
	city_country = (profile.get("city_country") or "").strip()
	links = (profile.get("links") or "").strip()
	summary = (profile.get("summary") or "Results-driven professional with a track record of delivering measurable impact and building strong stakeholder relationships.").strip()

	skills = profile.get("skills") or []
	if isinstance(skills, str):
		skills = [item.strip() for item in skills.split(",") if item.strip()]
	elif not isinstance(skills, list):
		skills = []

	experience = profile.get("experience") or []
	if isinstance(experience, str):
		experience = [{"role": title, "company": "", "dates": "", "bullets": [line.strip("- ") for line in experience.splitlines() if line.strip()]}]
	elif not isinstance(experience, list):
		experience = []

	education = profile.get("education") or []
	if isinstance(education, str):
		education = [line.strip() for line in education.splitlines() if line.strip()]
	elif not isinstance(education, list):
		education = []

	projects = profile.get("projects") or []
	if isinstance(projects, str):
		projects = [line.strip("- ") for line in projects.splitlines() if line.strip()]
	elif not isinstance(projects, list):
		projects = []

	certifications = profile.get("certifications") or []
	if isinstance(certifications, str):
		certifications = [line.strip("- ") for line in certifications.splitlines() if line.strip()]
	elif not isinstance(certifications, list):
		certifications = []

	achievements = profile.get("achievements") or []
	if isinstance(achievements, str):
		achievements = [line.strip("- ") for line in achievements.splitlines() if line.strip()]
	elif not isinstance(achievements, list):
		achievements = []

	optional_sections = profile.get("optional_sections") or []
	if isinstance(optional_sections, str):
		optional_sections = [line.strip("- ") for line in optional_sections.splitlines() if line.strip()]
	elif not isinstance(optional_sections, list):
		optional_sections = []

	lines = [name, title]
	contact = " | ".join(part for part in [email, phone, city_country, links] if part)
	if contact:
		lines.append(contact)
	lines.extend(["", "SUMMARY", summary, ""])

	lines.append("EXPERIENCE")
	if experience:
		for item in experience:
			if isinstance(item, dict):
				role = (item.get("role") or "Professional Experience").strip()
				company = (item.get("company") or "").strip()
				location = (item.get("location") or "").strip()
				dates = (item.get("dates") or "").strip()
				bullets = item.get("bullets") or []
				if isinstance(bullets, str):
					bullets = [line.strip("- ") for line in bullets.splitlines() if line.strip()]
				header = " | ".join(part for part in [role, company, location, dates] if part)
				if header:
					lines.append(header)
				else:
					lines.append(role)
				for bullet in bullets:
					formatted = str(bullet).strip()
					if formatted:
						lines.append(f"- {formatted}")
				lines.append("")
			else:
				formatted = str(item).strip()
				if formatted:
					lines.append(formatted)
	else:
		lines.append("Add your experience details here.")
	lines.extend(["", "EDUCATION"])
	if education:
		for item in education:
			if str(item).strip():
				lines.append(f"- {item}")
	else:
		lines.append("- Add your degrees or training")
	lines.extend(["", "SKILLS", ", ".join(skills) if skills else "Add your core strengths."])
	if projects:
		lines.extend(["", "PROJECTS"])
		lines.extend(f"- {str(project).strip()}" for project in projects if str(project).strip())
	if certifications:
		lines.extend(["", "CERTIFICATIONS"])
		lines.extend(f"- {str(certification).strip()}" for certification in certifications if str(certification).strip())
	if achievements:
		lines.extend(["", "ACHIEVEMENTS / AWARDS"])
		lines.extend(f"- {str(achievement).strip()}" for achievement in achievements if str(achievement).strip())
	if optional_sections:
		lines.extend(["", "ADDITIONAL INFORMATION"])
		lines.extend(f"- {str(item).strip()}" for item in optional_sections if str(item).strip())
	return "\n".join(lines).strip() + "\n"


def polish_structured_resume(profile: dict, draft: str) -> str:
	"""Improve clarity using only facts already supplied by the user."""
	profile = profile or {}
	title = str(profile.get("title") or "Professional").strip()
	skills = profile.get("skills") or []
	if isinstance(skills, str):
		skills = [item.strip() for item in skills.split(",") if item.strip()]
	lines = draft.splitlines()
	try:
		summary_start = lines.index("SUMMARY") + 1
		summary_end = lines.index("EXPERIENCE")
		summary = " ".join(line.strip() for line in lines[summary_start:summary_end] if line.strip())
		if summary and not summary.lower().startswith(title.lower()):
			summary = f"{title} with a focus on {', '.join(skills[:4]) or 'delivering strong results'}. {summary}"
		elif skills and not any(skill.lower() in summary.lower() for skill in skills[:2]):
			summary = summary.rstrip(".") + f". Core strengths include {', '.join(skills[:4])}."
		lines[summary_start:summary_end] = [summary]
	except ValueError:
		pass

	polished_lines = []
	action_words = tuple(sorted(ACTION_WORDS, key=len, reverse=True))
	for line in lines:
		if line.startswith("- ") and len(line) > 2:
			content = line[2:].strip()
			lower_content = content.lower()
			for weak_start, strong_start in (("worked on ", "Improved "), ("helped with ", "Supported "), ("helped ", "Supported "), ("responsible for ", "Managed ")):
				if lower_content.startswith(weak_start):
					content = strong_start + content[len(weak_start):]
					break
			if content and not content.split()[0].lower().rstrip(":,") in action_words:
				content = f"Delivered results by {content}"
			content = content[:1].upper() + content[1:]
			if content[-1:] not in ".!?":
				content += "."
			line = f"- {content}"
		polished_lines.append(line)
	return "\n".join(polished_lines).strip() + "\n"


def score_rating(score: int) -> tuple[str, str]:
	if score < 30:
		return "Very poor", "score-rating--very-poor"
	if score < 40:
		return "Poor", "score-rating--poor"
	if score < 50:
		return "Fair", "score-rating--fair"
	if score < 60:
		return "Good", "score-rating--good-yellow"
	if score < 75:
		return "Good", "score-rating--good-green"
	if score <= 90:
		return "Excellent", "score-rating--excellent"
	if score <= 95:
		return "Perfect", "score-rating--perfect"
	return "Perfect", "score-rating--perfect-neon"


def render_score_rating(score: int) -> None:
	rating, color_class = score_rating(score)
	st.markdown(
		f'<div class="grade-line"><span class="grade-label">Grade:</span>'
		f'<span class="score-rating score-rating--large {color_class}">{rating}</span></div>',
		unsafe_allow_html=True,
	)


def render_score(label: str, score: int) -> None:
	st.metric(label, f"{score}/100")
	st.progress(score / 100)


def load_demo_data() -> None:
	variants = get_demo_variants()
	index = int(st.session_state.get("demo_variant_index", 0))
	variant = variants[index % len(variants)]
	st.session_state["demo_variant_index"] = (index + 1) % len(variants)
	demo = variant["profile"]
	demo_resume = build_demo_resume_text(demo)
	for key, value in {
		"profile_name": demo["name"],
		"profile_title": demo["title"],
		"profile_email": demo["email"],
		"profile_city_country": demo["city_country"],
		"profile_links": demo["links"],
		"profile_country_code": "+1",
		"profile_phone_local": "4155123894",
		"profile_summary": demo["summary"],
		"profile_skills": ", ".join(demo["skills"]),
		"profile_experience_company": demo["experience"][0]["company"],
		"profile_experience_location": demo["experience"][0]["location"],
		"profile_experience_dates": demo["experience"][0]["dates"],
		"profile_experience": "\n".join(f"- {bullet}" for bullet in demo["experience"][0]["bullets"]),
		"profile_education": "\n".join(demo["education"]),
		"profile_projects": "\n".join(demo["projects"]),
		"profile_certifications": "\n".join(demo["certifications"]),
		"profile_achievements": "\n".join(demo["achievements"]),
		"profile_optional_sections": "\n".join(demo["optional_sections"]),
		"job_description": variant["job_description"],
		"target_role": demo["title"],
		"resume_text": demo_resume,
		"resume_upload_name": "demo_resume.txt",
	}.items():
		st.session_state[key] = value


def apply_demo_job_only() -> None:
	variants = get_demo_variants()
	index = int(st.session_state.get("demo_variant_index", 0))
	variant = variants[index % len(variants)]
	st.session_state["demo_variant_index"] = (index + 1) % len(variants)
	st.session_state["job_description"] = variant["job_description"]
	st.session_state["target_role"] = variant["profile"]["title"]
	if not st.session_state.get("resume_text", "").strip():
		st.session_state["resume_text"] = build_demo_resume_text(variant["profile"])
		st.session_state["resume_upload_name"] = "demo_resume.txt"


def apply_updated_resume() -> None:
	updated_resume = st.session_state.get("updated_resume_preview", "").strip()
	if updated_resume:
		st.session_state["resume_text"] = updated_resume
		st.session_state["resume_upload_name"] = "updated_resume.txt"
		for key in ("analysis_result", "ai_review", "local_review", "analysis_resume", "analysis_job"):
			st.session_state.pop(key, None)

st.markdown(
	"""
	<div class="hero-card">
		<div class="hero-kicker">Resume intelligence studio</div>
		<h3>Make your next move legible.</h3>
		<p>Turn experience into a sharper story, stronger evidence, and a resume built for the role in front of you.</p>
	</div>
	<div class="feature-strip">
		<span class="feature-pill">01&nbsp;&nbsp;Signal scoring</span>
		<span class="feature-pill">02&nbsp;&nbsp;Role alignment</span>
		<span class="feature-pill">03&nbsp;&nbsp;Editorial rewrites</span>
	</div>
	""",
	unsafe_allow_html=True,
)
st.caption("A focused career editor for sharper language, stronger evidence, and better role fit.")

with st.sidebar:
	st.markdown("## Your workspace")
	st.caption("Local scoring stays on this device. AI mode sends your resume to OpenAI for personalized feedback.")
	analysis_mode = st.radio(
		"Analysis mode",
		["Fast", "Deep think"],
		horizontal=True,
		index=0,
		key="analysis_mode",
	)

	st.markdown("### Build a resume from your profile")
	st.button("Load demo profile", type="secondary", width="stretch", on_click=load_demo_data)
	with st.form("resume_profile_form"):
		name = st.text_input("Full name", key="profile_name", label_visibility="visible", placeholder="Your full name")
		title = st.text_input("Professional title", key="profile_title", label_visibility="visible", placeholder="e.g. Senior Product Designer")
		email = st.text_input("Email", key="profile_email", label_visibility="visible", placeholder="you@company.com")
		city_country = st.text_input("City / country", placeholder="e.g. Austin, United States", key="profile_city_country")
		links = st.text_input("LinkedIn, GitHub, or portfolio", placeholder="https://linkedin.com/in/yourname", key="profile_links")
		country_code = st.selectbox("Country code", list(COUNTRY_CODES.keys()), index=3, key="profile_country_code")
		phone_local = st.text_input("Local phone number", key="profile_phone_local", max_chars=10, placeholder="9876543210")
		if phone_local and (not phone_local.isdigit() or len(phone_local) != 10):
			st.warning("Local phone number must be exactly 10 digits with no spaces or symbols.")
		summary = st.text_area("Summary", height=120, key="profile_summary")
		skills = st.text_area("Skills (comma separated)", height=80, key="profile_skills")
		experience_company = st.text_input("Most recent company", key="profile_experience_company")
		experience_location = st.text_input("Experience location", placeholder="e.g. Remote or New York, United States", key="profile_experience_location")
		experience_dates = st.text_input("Experience dates", placeholder="e.g. Jan 2022 - Present", key="profile_experience_dates")
		experience = st.text_area("Experience bullets (one per line)", height=120, placeholder="- Led product redesign for ...\n- Increased conversion by 18%", key="profile_experience")
		education = st.text_area("Education (one per line)", height=100, placeholder="B.S. in Computer Science\nUniversity of Texas", key="profile_education")
		projects = st.text_area("Projects (one per line)", height=90, placeholder="Project name - what you built, tools used, and result", key="profile_projects")
		certifications = st.text_area("Certifications (one per line)", height=70, placeholder="Certification - issuing organization - year", key="profile_certifications")
		achievements = st.text_area("Achievements / awards (one per line)", height=70, placeholder="Award, scholarship, competition, or professional achievement", key="profile_achievements")
		optional_sections = st.text_area("Optional details (one per line)", height=80, placeholder="Volunteer work, leadership, publications, languages, or relevant interests", key="profile_optional_sections")
		if st.form_submit_button("Generate polished resume draft", type="primary", width="stretch"):
			try:
				phone = normalize_phone(country_code, phone_local)
			except ValueError as error:
				st.error(str(error))
				st.stop()
			experience_bullets = [line.strip("- ") for line in experience.splitlines() if line.strip()]
			experience_items = []
			if experience_bullets or experience_company.strip():
				experience_items = [{
					"role": title or "Professional Experience",
					"company": experience_company,
					"location": experience_location,
					"dates": experience_dates,
					"bullets": experience_bullets,
				}]
			profile = {
				"name": name,
				"title": title,
				"email": email,
				"phone": phone,
				"city_country": city_country,
				"links": links,
				"summary": summary,
				"skills": [item.strip() for item in skills.split(",") if item.strip()],
				"experience": experience_items,
				"education": [line.strip() for line in education.splitlines() if line.strip()],
				"projects": [line.strip("- ") for line in projects.splitlines() if line.strip()],
				"certifications": [line.strip("- ") for line in certifications.splitlines() if line.strip()],
				"achievements": [line.strip("- ") for line in achievements.splitlines() if line.strip()],
				"optional_sections": [line.strip("- ") for line in optional_sections.splitlines() if line.strip()],
			}
			quality_issues = profile_quality_issues(profile)
			if quality_issues:
				st.error("This profile is not strong enough to generate a reliable resume yet.")
				st.info("Give me these details and I can make you a much better one: " + "; ".join(quality_issues) + ".")
				st.stop()
			generated = polish_structured_resume(profile, generate_resume_from_profile(profile))
			if local_model_available(OLLAMA_FAST_MODEL):
				with st.spinner("Polishing the draft with your local resume editor..."):
					try:
						generated = request_local_resume_draft(profile, generated)
					except (AIServiceError, requests.RequestException, KeyError, TypeError, ValueError):
						st.info("The local editor was unavailable, so I created the structured draft instead.")
			st.session_state["resume_text"] = generated
			st.session_state["resume_upload_name"] = "generated_resume.txt"
			st.success("Resume draft created and polished. Review it in the main text area.")
			st.rerun()

	target_role = st.text_input("Target role", placeholder="e.g. Product designer", key="target_role")
	openai_key = st.text_input(
		"OpenAI API key (optional)",
		type="password",
		help="Use an environment variable or Streamlit secret for production. This field is kept only in your session.",
		key="openai_key",
	)
	if get_api_key(openai_key):
		st.success("AI review enabled")
	elif local_model_available(OLLAMA_FAST_MODEL) or local_model_available(OLLAMA_MODEL):
		st.success(f"Free local AI ready · {OLLAMA_FAST_MODEL} / {OLLAMA_MODEL}")
	else:
		st.caption("Local analysis is ready. Start Ollama to unlock free AI feedback, or add an OpenAI key.")
	if st.button("Clear analysis", width="stretch"):
		for key in ("analysis_mode", "analysis_result", "ai_review", "local_review", "analysis_resume", "analysis_job", "chat_messages", "updated_resume_preview", "target_role", "openai_key", "resume_text", "job_description"):
			st.session_state.pop(key, None)
		st.rerun()
	st.divider()
	st.markdown("#### Signal map")
	st.markdown("- Role-specific language\n- Essential resume sections\n- Evidence and measurable impact\n- Length and scanability")

resume_text = st.session_state.get("resume_text", "")
job_description = st.session_state.get("job_description", "")

if not (resume_text.strip() or job_description.strip()):
	st.markdown("### Quick start")
	quick_col_1, quick_col_2 = st.columns(2)
	with quick_col_1:
		st.button("Load full demo", type="primary", width="stretch", on_click=load_demo_data)
	with quick_col_2:
		st.button("Use sample job only", type="secondary", width="stretch", on_click=apply_demo_job_only)
	st.info("Tip: start with the demo data for a realistic example, then swap in your real resume and target role.")

left, right = st.columns((1.1, 0.9), gap="large")
with left:
	st.markdown("## 1. Add your resume")
	uploaded_file = st.file_uploader("Upload a plain-text resume", type=["txt"], label_visibility="collapsed")
	if uploaded_file and st.session_state.get("resume_upload_name") != uploaded_file.name:
		st.session_state["resume_text"] = uploaded_file.getvalue().decode("utf-8", errors="ignore")
		st.session_state["resume_upload_name"] = uploaded_file.name
	resume_text = st.text_area(
		"Resume text",
		height=360,
		placeholder="Paste the resume you want to sharpen here...",
		label_visibility="collapsed",
		key="resume_text",
	)

with right:
	st.markdown("## 2. Add the target")
	job_description = st.text_area(
		"Job description",
		height=360,
		placeholder="Paste the job description or a few lines describing the role...",
		label_visibility="collapsed",
		key="job_description",
	)

analysis_mode = st.session_state.get("analysis_mode", "Fast")
analyze = st.button("Get resume analysis", type="primary", width="stretch", help="Analyze your resume and receive concrete, actionable suggestions")

if analyze or "analysis_result" in st.session_state:
	if not resume_text.strip():
		if analyze:
			st.warning("Add your resume text first.")
	elif not job_description.strip():
		if analyze:
			st.warning("Add a target role or job description so the relevance score has something to compare.")
	else:
		if analyze:
			result = analyze_resume(resume_text, job_description)
			api_key = get_api_key(openai_key)
			ai_review = None
			review_source = "Local"
		else:
			result = st.session_state["analysis_result"]
			ai_review = st.session_state.get("ai_review")
			review_source = st.session_state.get("review_source", "Local")
			local_review = st.session_state.get("local_review", build_local_review(resume_text, job_description, result))
		if analyze:
			if api_key:
				review_source = "OpenAI"
				spinner_text = "Deep-thinking through your resume and target fit..." if analysis_mode == "Deep think" else "Checking your resume fit and improving the strongest signals..."
				with st.spinner(spinner_text):
					try:
						ai_review = request_ai_review(resume_text, job_description, api_key, mode=analysis_mode)
					except (AIServiceError, requests.RequestException, KeyError, TypeError, ValueError) as error:
						st.warning(f"OpenAI review unavailable: {error}. Showing the local analysis instead.")
			elif local_model_available(OLLAMA_MODEL if analysis_mode == "Deep think" else OLLAMA_FAST_MODEL):
				review_source = "Local AI"
				with st.spinner("Your local resume model is reviewing the evidence and role fit..."):
					try:
						ai_review = request_local_review(resume_text, job_description, mode=analysis_mode)
					except (AIServiceError, requests.RequestException, KeyError, TypeError, ValueError) as error:
						st.warning(f"Local AI review unavailable: {error}. Showing the local analysis instead.")
		if analyze:
			st.session_state["analysis_result"] = result
			st.session_state["ai_review"] = ai_review
			st.session_state["review_source"] = review_source
			st.session_state["local_review"] = build_local_review(resume_text, job_description, result)
			st.session_state["analysis_resume"] = resume_text
			st.session_state["analysis_job"] = job_description
		local_review = st.session_state["local_review"]
		st.divider()
		st.markdown("## Your signal report")
		render_score_rating(result["overall"])
		st.caption(f"{result['word_count']} words analyzed" + (f" for {target_role}" if target_role else ""))

		score_col, keyword_col, impact_col, structure_col = st.columns(4)
		with score_col:
			st.metric("Overall signal", f"{result['overall']}/100", help="A weighted blend of relevance, structure, impact, and length.")
		with keyword_col:
			render_score("Role match", result["keyword_score"])
		with impact_col:
			render_score("Proof of impact", result["impact_score"])
		with structure_col:
			render_score("Structure", result["section_score"])

		report_left, report_right = st.columns((1, 1), gap="large")
		with report_left:
			st.markdown("### Strong signals")
			if result["matched"]:
				st.pills("Matched language", result["matched"], selection_mode="multi", default=result["matched"])
			else:
				st.info("No clear overlap yet. Use the target role's language where it honestly reflects your experience.")
			st.markdown("### Section health")
			for section, present in result["sections"].items():
				status = "Present" if present else "Needs review"
				st.markdown(f"**{section.title()}** · {status}")

		with report_right:
			st.markdown("### Highest-leverage edits")
			for index, suggestion in enumerate(result["suggestions"], start=1):
				st.markdown(f"**{index:02d}**  {suggestion}")
			st.markdown("### Local editor recommendations")
			for index, recommendation in enumerate(result["local_recommendations"], start=1):
				st.markdown(f"**{index:02d}**  {recommendation}")
			st.markdown("### Missing language to review")
			if result["missing"]:
				st.write(", ".join(result["missing"][:10]))
			else:
				st.success("Your resume covers the most frequent terms in this target.")
			report_text = (
			f"RESUME SIGNAL REPORT\n\n"
			f"Overall signal: {result['overall']}/100\n"
			f"Role match: {result['keyword_score']}/100\n"
			f"Proof of impact: {result['impact_score']}/100\n"
			f"Structure: {result['section_score']}/100\n"
			f"Words analyzed: {result['word_count']}\n\n"
			f"RECOMMENDATIONS\n"
			+ "\n".join(f"- {suggestion}" for suggestion in result["suggestions"])
			+ "\n\nLOCAL EDITOR RECOMMENDATIONS\n"
			+ "\n".join(f"- {recommendation}" for recommendation in result["local_recommendations"])
			+ "\n\nMISSING LANGUAGE TO REVIEW\n"
			+ ", ".join(result["missing"][:10])
		)
		st.download_button(
			"Download signal report",
			data=report_text,
			file_name="resume_signal_report.txt",
			mime="text/plain",
			width="content",
		)

		review = ai_review or local_review
		if review:
			updated_resume_text = str(review.get("updated_resume") or resume_text).strip()
			st.divider()
			st.markdown(f"## {review_source if ai_review else 'Local'} editor review")
			ai_left, ai_right = st.columns((1, 1), gap="large")
			with ai_left:
				st.markdown("### What is already working")
				for strength in review["strengths"]:
					st.markdown(f"**Strong** · {strength}")
				st.markdown("### What needs attention")
				for weakness in review["weaknesses"]:
					st.markdown(f"**Review** · {weakness}")
				st.markdown("### Your tailored summary")
				st.info(review["tailored_summary"])
			with ai_right:
				st.markdown("### Stronger bullet rewrites")
				for bullet in review["bullet_rewrites"]:
					with st.container(border=True):
						st.caption("Current")
						st.write(bullet["original"])
						st.caption("Suggested")
						st.write(bullet["rewrite"])
				st.markdown("### Next steps")
				for index, next_step in enumerate(review["next_steps"], start=1):
					st.markdown(f"**{index:02d}**  {next_step}")

			st.markdown("### Updated resume")
			st.caption("This is an optional draft. Review every line and edit anything that does not sound like you before using it.")
			updated_resume = st.text_area(
				"AI-updated resume",
				value=updated_resume_text,
				height=520,
				key="updated_resume_preview",
				label_visibility="collapsed",
			)
			st.button(
				"Use this as my resume",
				type="primary",
				width="content",
				on_click=apply_updated_resume,
			)
			st.download_button(
				"Download updated resume",
				data=updated_resume,
				file_name="updated_resume.txt",
				mime="text/plain",
				width="content",
			)

if st.session_state.get("analysis_result") or (resume_text.strip() and job_description.strip()):
	st.divider()
	st.markdown("## Resume coach")
	st.caption("Ask a focused question about your summary, skills, bullets, or fit for the target role.")
	if "analysis_resume" not in st.session_state and resume_text.strip():
		st.session_state["analysis_resume"] = resume_text
	if "analysis_job" not in st.session_state and job_description.strip():
		st.session_state["analysis_job"] = job_description
	if "chat_messages" not in st.session_state:
		st.session_state["chat_messages"] = []

	suggestion_map = {
		"What should I fix first?": "What are the three highest-priority changes I should make first?",
		"Rewrite my summary": "Rewrite my professional summary in three different tones: confident, concise, and warm.",
		"Make it ATS-friendly": "What ATS issues do you see, and how should I improve the resume without keyword stuffing?",
		"Tailor it more": "How can I tailor this resume more closely to the target job while staying truthful?",
	}
	if not st.session_state["chat_messages"]:
		selected_suggestion = st.pills(
			"Start with a focused question",
			list(suggestion_map),
			label_visibility="collapsed",
		)
	else:
		selected_suggestion = None
	chat_prompt = st.chat_input(
		"Ask about your resume...",
		disabled=st.session_state.get("chat_busy", False),
	) or suggestion_map.get(selected_suggestion)

	for message in st.session_state["chat_messages"]:
		role = message["role"]
		label = "You" if role == "user" else "Resume coach"
		style = "chat-user" if role == "user" else "chat-assistant"
		st.markdown(
			f'<div class="chat-row {style}"><div class="chat-label">{label}</div>{message["content"]}</div>',
			unsafe_allow_html=True,
		)

	if chat_prompt:
		st.session_state["chat_busy"] = True
		st.session_state["chat_messages"].append({"role": "user", "content": chat_prompt})
		st.markdown(
			f'<div class="chat-row chat-user"><div class="chat-label">You</div>{chat_prompt}</div>',
			unsafe_allow_html=True,
		)
		with st.spinner("Thinking through the next improvement..."):
			try:
				api_key = get_api_key(openai_key)
				if api_key:
					answer = request_ai_chat(
						st.session_state["analysis_resume"],
						st.session_state["analysis_job"],
						st.session_state.get("ai_review") or st.session_state.get("local_review", {}),
						st.session_state["chat_messages"],
						api_key,
					)
				elif local_model_available(OLLAMA_MODEL if analysis_mode == "Deep think" else OLLAMA_FAST_MODEL):
					answer = request_local_chat(
						st.session_state["analysis_resume"],
						st.session_state["analysis_job"],
						st.session_state.get("ai_review") or st.session_state.get("local_review", {}),
						st.session_state["chat_messages"],
						analysis_mode,
					)
				else:
					answer = local_resume_chat_answer(
						chat_prompt,
						st.session_state["analysis_resume"],
						st.session_state["analysis_job"],
						st.session_state.get("local_review"),
					)
				st.markdown(
					f'<div class="chat-row chat-assistant"><div class="chat-label">Resume coach</div>{answer}</div>',
					unsafe_allow_html=True,
				)
				st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
			except (AIServiceError, requests.RequestException, KeyError, TypeError, ValueError):
					fallback = local_resume_chat_answer(chat_prompt, st.session_state["analysis_resume"], st.session_state["analysis_job"], st.session_state.get("local_review"))
					st.markdown(
						f'<div class="chat-row chat-assistant"><div class="chat-label">Resume coach</div>{fallback}</div>',
						unsafe_allow_html=True,
					)
					st.session_state["chat_messages"].append({"role": "assistant", "content": fallback})
			finally:
				st.session_state["chat_busy"] = False

st.divider()
st.caption("Resume signal is a decision aid, not a hiring prediction. Review every suggestion for accuracy before applying.")

