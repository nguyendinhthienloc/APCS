# Project Overview

| Project name | Description | Similar existing Apps/Systems |
|---|---|---|
| **DebateSpeak AI** | A web-based live spoken-debate and English-learning platform. Two learners join a shared audio room, debate a topic by microphone, and the system transcribes each speaker in real time. AI agents then analyze English usage (grammar, vocabulary, fluency, clarity), evaluate arguments (claims, evidence, rebuttals), fact-check selected claims against retrieved sources, and generate a personalized post-debate learning report with concrete practice recommendations. Debate is the learning activity; AI feedback is the learning mechanism. | ArguFight, Khaos Live, ELSA Speak |

## Elevator Pitch

> DebateSpeak is a live spoken-debate platform for English learners. Two users debate a topic in a real-time audio room while AI agents transcribe, analyze English usage, evaluate arguments, investigate factual claims, and produce personalized feedback for improving both spoken English and debate skills.

## Core Product Concept

```
Live room -> speech -> transcript -> AI analysis -> evidence -> learning feedback
```

| Step | What happens | Who does it |
|---|---|---|
| Live room | Two authenticated learners join, give consent and talk in a WebRTC audio room (LiveKit) | Learners + media layer |
| Speech | Each speaker's microphone is a separate audio track | Browser + LiveKit |
| Transcript | Streaming speech-to-text produces speaker-attributed, timestamped segments | Transcription worker (existing STT API/library) |
| AI analysis | Language Coach, Argument Coach and Claim Detector process targeted transcript segments | LLM agents + deterministic speech metrics |
| Evidence | Selected factual claims are matched to retrieved sources and evaluated, with uncertainty shown | Fact Investigator, Evidence Evaluator, Skeptic |
| Learning feedback | Scores, key issues, quoted corrections and a practice plan adapted to the learner's CEFR level | Judge, Consensus Engine, Learning Coach |

The team does **not** train any speech, language or fact-checking model. The engineering contribution is integrating and orchestrating existing services into a reliable web application.

## Actors

| Actor | Role |
|---|---|
| **Learner / Debater** | Registers, sets CEFR level (A2-C1), picks a topic, creates or joins a room, debates, and reviews transcript, report, history and progress |
| **Moderator / Admin** | Manages topics and difficulty, handles abuse reports and suspensions, configures AI providers, prompts and feature flags, and processes deletion requests |

## Functional Groups

| ID | Functional group | Scope |
|---|---|---|
| FG-01 | User Account & Profile Management | Registration, login, profile, CEFR level, account deletion, suspension |
| FG-02 | Debate Topic & Difficulty Management | Topic library, categories, CEFR difficulty, recommendations |
| FG-03 | Debate Room / Live Session Management | Create/join room, state machine, consent, timer, leave/reconnect, abuse reports |
| FG-04 | Real-Time Audio Communication | WebRTC audio via LiveKit, mic permission and test, mute, connection status |
| FG-05 | Speech-to-Text & Speaker Attribution | Streaming transcription, per-track speaker attribution, persistence, live transcript |
| FG-06 | English Language Analysis | Speech metrics, grammar and vocabulary feedback, CEFR adaptation |
| FG-07 | Argument & Debate Analysis | Claim structure, relevance, evidence, rebuttal, fallacies |
| FG-08 | AI Fact Checking & Evidence Analysis | Claim detection, retrieval, evidence evaluation, five-level verdicts with sources |
| FG-09 | Multi-Agent Evaluation / Consensus | Independent evaluators, deterministic consensus, "contested" flags, AI configuration |
| FG-10 | Learning History & Personalized Reports | Report generation, history, progress tracking, recommendations |

## Deployment Note

Two users debating from **different devices and networks requires a deployed system**: microphone access needs HTTPS, WebRTC needs managed STUN/TURN, and both users must reach the same server. The plan is a hybrid deployment (app stack on one VM or container host, LiveKit Cloud for media), with a staging deployment ready by Week 4. Local-only mode (two browser windows on one machine) is for development, and a same-Wi-Fi HTTPS setup is the classroom fallback. Details are in the spec (Section 5.5) and the roadmap (Section 3.10).

## MVP Boundary

| MVP (committed) | Stretch goals |
|---|---|
| 1. Login 2. Topic selection 3. Create/join room 4. Two-person live audio 5. Speech-to-text 6. Transcript 7. English analysis 8. Argument analysis 9. Basic fact checking 10. Final learning report | Live video; advanced pronunciation scoring; multiple simultaneous AI judges; tournaments; rankings/ELO; audience mode; live fact-check overlays; teacher dashboard; sophisticated CEFR progression model |

## Existing Apps / Systems

Similar products exist, and DebateSpeak does **not** claim to be unprecedented in any single feature. AI judging, speech-to-text, voice input, multiple AI judges, debate scoring and AI fact-checking are all offered by other products. Feature descriptions below are approximate, based on public marketing material, and should be verified before they are cited in a presentation.

| Existing System | Main Focus | Relevant Features | Proposed Difference |
|---|---|---|---|
| **ArguFight** | Structured competitive debate with AI judging | AI-judged debates, voice input, fact checking, multiple AI judges | DebateSpeak is learning-first: live human-to-human spoken conversation, CEFR-aware language feedback and personalized practice plans rather than a competitive verdict |
| **DebateGuard** | Real-time speech transcription and fact checking | Live transcription, claim checking | DebateSpeak adds English-learning analysis (grammar, vocabulary, fluency) and argument coaching, and its fact checks are shown with uncertainty in a learning report |
| **Khaos Live** | Live debates with transcription and AI scoring | Live rooms, transcript, scoring | DebateSpeak targets language learners, not entertainment or competition; the output is a corrective, level-adapted report |
| **Who's Right?** | Two-person spoken argument settled by an AI verdict | Spoken argument, AI verdict, fact checking | DebateSpeak gives developmental feedback and shows evaluator disagreement instead of a single winner |
| **Debate Judge AI / Dikast** | AI-assisted debate judging and analysis | Rubric-based judging, analysis | DebateSpeak is a live-room product for learners, with language analysis integrated into the same report |
| **ELSA Speak** (English learning) | Pronunciation and speaking practice with AI | AI feedback on pronunciation and fluency | Practice is solo or scripted; DebateSpeak uses spontaneous human-to-human debate and adds argument and evidence feedback (pronunciation scoring is only a stretch goal) |
| **Generic AI English tutors** (conversation apps) | Conversation with an AI partner and language correction | Corrections, role-play | Flow is conversation → language correction; DebateSpeak adds debate → spontaneous rebuttal → evidence → argumentation → language feedback → personalized improvement |
| **Human tutor marketplaces** (e.g., Cambly, iTalki) | Scheduled lessons with human tutors | Live video with a tutor | DebateSpeak supports peer debate with automatic, objective-evidence-grounded feedback at lower cost, but it does not replace tutors |

## Differentiation

DebateSpeak's value is the **combination**, with each element individually already present elsewhere:

1. **Live human-to-human spoken debate room**, not typed debate and not an AI partner.
2. **English-learning-first objective**, with CEFR-adapted feedback.
3. **Debate as the learning activity** that forces spontaneous rebuttal, evidence and structured reasoning.
4. **Combined language + argument + evidence analysis** in one report.
5. **Personalized post-debate improvement**, with quoted corrections, recurring error patterns and practice plans.
6. **Optional multi-agent independent evaluation** that surfaces disagreement and uncertainty instead of presenting one model's answer as fact.

## Why AI Is Essential (Practical Value)

- A human cannot easily monitor grammar, rebuttal quality and factual accuracy at the same time during a live debate; AI agents analyze the transcript afterwards and point to the learner's own words.
- Feedback is **grounded**: each language or argument item quotes the transcript and is verified automatically, so it is not a decorative chatbot comment.
- Fact checks are evidence-based (claim → retrieval → evaluation) and carry explicit uncertainty.
