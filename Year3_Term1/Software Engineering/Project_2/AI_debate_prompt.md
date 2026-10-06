You are working on a Software Engineering course project. I have provided three existing Markdown files from a previous project:

- `AI_COMBINE_SPEC.md`
- `PROJECT_OVERVIEW.md`
- `ROADMAP_AND_EXECUTION.md`

Use these three files as the PRIMARY STRUCTURAL AND DETAIL-LEVEL REFERENCES for creating a completely new project documentation package.

The previous project was AI-Combine, an adversarial multi-agent code-hardening system. DO NOT preserve its domain, terminology, architecture, CLI-first design, or code-testing assumptions. Instead, create a new project based on the concept below.

# NEW PROJECT

Working name:

**DebateSpeak AI**

Alternative names may be proposed if they are better, but use `DebateSpeak AI` consistently unless there is a strong reason to change it.

Core idea:

A web-based live spoken debate and English-learning platform.

Two human users enter a shared live debate room, similar conceptually to a lightweight Google Meet room. They communicate using their microphones and debate a selected topic.

The system:

1. Creates/join a live debate room.
2. Connects two users through real-time audio.
3. Captures their speech.
4. Converts speech into a real-time transcript.
5. Separates the two speakers.
6. Analyzes their English speaking performance.
7. Analyzes their debate/argumentation performance.
8. Fact-checks meaningful factual claims.
9. Uses multiple independent AI analysis/judge agents where appropriate.
10. Produces a personalized post-debate learning report.

The primary target is NOT competitive debaters.

The primary target is:

**English learners who want to improve spontaneous speaking, argumentation, vocabulary, grammar, fluency, and critical thinking through live debate.**

The debate is the learning activity.

The AI feedback is the learning mechanism.

The product should therefore be positioned as:

> An AI-assisted English speaking platform that uses live debate to develop learners' speaking and critical-thinking skills.

Do NOT position it merely as:

> "An AI that judges debates."

That distinction is important.

---

# IMPORTANT PRODUCT DIFFERENTIATION

There are already products that provide AI debate judging, AI fact checking, voice input, and multiple AI judges.

Therefore, DO NOT claim that the following are unique:

- AI judges
- AI fact checking
- speech-to-text
- voice input
- multiple AI judges
- debate scoring
- AI feedback by itself

Instead, emphasize the combination of:

**live spoken human-to-human debate + English learning + real-time transcription + language feedback + argument analysis + evidence analysis + personalized learning feedback.**

The live room is important.

The intended interaction is:

User A joins room
+
User B joins room
+
both speak naturally through microphones
+
conversation happens in real time
+
speech is transcribed continuously
+
AI analyzes the conversation
+
post-debate learning report is generated.

This should feel closer to:

**Google Meet + English speaking practice + debate coach**

than:

**typed debate + AI judge.**

---

# IMPORTANT EXISTING-PRODUCT AWARENESS

The documentation should acknowledge that similar products exist.

Known categories/examples include:

- ArguFight — AI-judged debates, voice input, fact checking, multiple AI judges.
- DebateGuard — real-time speech transcription and fact checking.
- Khaos Live — live debates, transcription, AI scoring.
- Who's Right? — two-person spoken argument/debate with AI verdict and fact checking.
- Debate Judge AI / Dikast — AI-assisted debate judging and analysis.
- Various English-speaking/debate-learning applications.

Do not falsely claim the proposed system is completely novel.

Instead, formulate differentiation honestly.

A useful comparison is:

ArguFight:
structured competitive debate + AI judges

Proposed system:
live spoken conversation + English learning + debate practice + personalized language/argument feedback.

Also distinguish the proposed product from generic English conversation tutors:

Generic English tutor:
conversation → language correction

Proposed system:
conversation → debate → spontaneous rebuttal → evidence → argumentation → language feedback → personalized improvement.

---

# COURSE CONTEXT

This is a Software Engineering course project.

The documentation should therefore prioritize:

- requirements
- actors
- functional groups
- system architecture
- web application design
- AI integration
- database
- real-time communication
- testing
- project management
- sprint planning
- acceptance criteria
- risks
- implementation roadmap

Do not turn this into an academic machine-learning research project.

The team should NOT train a speech recognition model, LLM, pronunciation model, or fact-checking model.

Use existing APIs/libraries/services.

The interesting engineering work is the integration and orchestration of the components into a coherent web application.

---

# COURSE REQUIREMENT CONSTRAINTS

The project must be designed as a:

**Web application or mobile application.**

Do NOT make it a desktop-only application or CLI.

It should contain approximately:

**8–10 meaningful functional groups.**

It must have at least:

**2 actor/user types.**

Suggested actors:

1. Debater / Learner
2. Moderator / Admin

Do not create artificial functional groups merely to reach 8–10.

Each functional group should represent a meaningful cluster of related use cases.

The system must include a meaningful AI feature.

AI must provide actual practical value rather than being a decorative chatbot.

---

# CORE FUNCTIONAL GROUPS

Use approximately these 10 functional groups unless you identify a better decomposition:

1. User Account & Profile Management
2. Debate Topic & Difficulty Management
3. Debate Room / Live Session Management
4. Real-Time Audio Communication
5. Speech-to-Text & Speaker Diarization
6. English Language Analysis
7. Argument & Debate Analysis
8. AI Fact Checking & Evidence Analysis
9. Multi-Agent Evaluation / Consensus
10. Learning History & Personalized Reports

You may refine the names and boundaries, but preserve the intent.

For example, English Language Analysis should cover things such as:

- grammar
- vocabulary
- fluency
- filler words
- speaking pace
- sentence structure
- clarity

Where technically feasible, pronunciation can be included through an external speech/pronunciation API.

Do NOT promise highly accurate pronunciation scoring if the selected technology cannot support it.

Argument analysis can cover:

- claim identification
- relevance
- evidence usage
- reasoning
- rebuttal quality
- counterargument handling
- logical fallacies
- clarity of position

Fact checking should be described as:

speech → claim extraction → evidence/search retrieval → AI evidence evaluation

rather than:

LLM simply decides whether something is true.

---

# MULTI-AGENT DESIGN

Use multiple specialized AI roles where this genuinely improves the product.

Possible agents:

### Language Coach Agent
Analyzes:
- grammar
- vocabulary
- fluency
- clarity
- filler words
- speaking patterns

### Argument Coach Agent
Analyzes:
- argument structure
- reasoning
- relevance
- rebuttals
- counterarguments
- fallacies

### Fact Investigator Agent
Identifies factual claims and retrieves relevant evidence.

### Evidence/Skeptic Agent
Critically examines whether the retrieved evidence actually supports the claim.

### Debate Judge Agent(s)
Produces an overall debate-performance evaluation.

### Learning Coach Agent
Converts all findings into actionable English-learning recommendations.

If multiple judge models are used, DO NOT claim this alone is the unique feature.

Instead, explain that independent evaluations can expose disagreement and uncertainty.

Example:

Judge A:
Claim sufficiently supported — 85%

Judge B:
Partially supported — 70%

Judge C:
Insufficient evidence — 80%

System:

"Contested claim — judges disagree; evidence is insufficient for a confident conclusion."

This is preferable to blindly presenting one model's answer as fact.

---

# REAL-TIME ROOM

The live room is a core feature.

Conceptually:

```text
User A ─────┐
            │
            ▼
      ┌─────────────┐
      │ Debate Room │
      │  WebRTC     │
      └──────┬──────┘
             │
      ┌──────▼──────┐
      │ Audio Stream│
      └──────┬──────┘
             │
      ┌──────▼────────────┐
      │ Speech Recognition│
      │     + Diarization │
      └──────┬────────────┘
             │
          Transcript
             │
     ┌───────┼────────┐
     ▼       ▼        ▼
 Language  Argument  Fact
 Agent     Agent     Agent
     │       │        │
     └───────┼────────┘
             ▼
      Consensus / Judge
             │
             ▼
       Learning Report
```

Possible technologies:

Frontend:
- React / Next.js

Backend:
- FastAPI or Node.js

Database:
- PostgreSQL

Real-time communication:
- WebRTC
- or LiveKit if that substantially simplifies implementation

Real-time signaling:
- WebSocket

Speech-to-text:
- Whisper / faster-whisper / Whisper-compatible service
- or an appropriate hosted speech API

TTS:
- browser SpeechSynthesis API or an external TTS service

LLM:
- configurable LLM APIs

Evidence retrieval:
- web/search API

Do not over-engineer the first version.

If LiveKit provides a substantially easier and more reliable implementation of the room, prefer it over manually implementing a complete WebRTC infrastructure.

---

# ENGLISH-LEARNING DESIGN

The system should have a CEFR-aware learning dimension.

Possible levels:

A2
B1
B2
C1

Users can select their approximate level.

The AI should adapt:

- debate topic difficulty
- vocabulary expectations
- feedback complexity
- suggested vocabulary
- grammar feedback
- speaking goals

Example:

A B1 learner says:

"I think government should make people use public transport because it reduce pollution."

Feedback:

Grammar:
"it reduce" → "it reduces"

Vocabulary:
"make people use" → "encourage people to use"

Argument:
Clear claim, but supporting evidence is weak.

Suggested improvement:

"Governments should encourage people to use public transport because it can reduce urban air pollution."

Do not make the feedback excessively academic or difficult for the learner.

---

# PERSONALIZED REPORT

The report is one of the most important product features.

Example structure:

## Debate Summary

Topic:
"Should university education be free?"

Duration:
12:34

## English Performance

Grammar:
82/100

Vocabulary:
74/100

Fluency:
78/100

Clarity:
85/100

## Debate Performance

Argument Quality:
81/100

Evidence:
63/100

Rebuttal:
76/100

Counterarguments:
70/100

## Important Issues

1. Frequent article errors.
2. Repeated use of "I think".
3. Several long pauses before rebuttals.
4. One factual claim had weak evidence.
5. Strong main position but limited supporting examples.

## Recommended Practice

- Practice articles with academic topics.
- Learn 10 alternative expressions for giving opinions.
- Practice 30-second rebuttals.
- Review evidence quality.

This report should be actionable rather than just a leaderboard score.

---

# FILES TO CREATE

Create EXACTLY these three Markdown files:

1. `DEBATESPEAK_SPEC.md`
2. `PROJECT_OVERVIEW.md`
3. `ROADMAP_AND_EXECUTION.md`

Do not modify the three original AI-Combine files.

The new files should be self-contained and internally consistent.

---

# FILE 1 — DEBATESPEAK_SPEC.md

This should be the detailed software requirements and architecture specification.

Use `AI_COMBINE_SPEC.md` as the structural reference.

It should contain approximately these sections:

1. Executive Summary & Problem Formulation
2. Product Goals and Non-Goals
3. Target Users and Actors
4. Functional Requirements
5. Non-Functional Requirements
6. System Architecture
7. Live Debate Room Architecture
8. Speech-to-Text Pipeline
9. AI Agent Architecture
10. Fact Checking & Evidence Pipeline
11. English Learning Analysis
12. Debate Analysis
13. Multi-Agent Evaluation / Consensus
14. Data Models & Schemas
15. API Design
16. Security & Privacy
17. AI Safety / Hallucination Handling
18. External Services / Libraries
19. Evaluation Metrics
20. Definition of Done

For each functional requirement provide:

- ID
- Requirement
- Priority
- Description where useful

Example:

FR-01:
Users can register and authenticate.

FR-02:
Users can create or join a debate room.

FR-03:
A debate room supports two participants with real-time audio.

FR-04:
The system produces a near-real-time transcript.

FR-05:
The system identifies which participant produced each utterance.

FR-06:
The system analyzes English performance.

FR-07:
The system identifies and evaluates arguments.

FR-08:
The system fact-checks selected factual claims using retrieved evidence.

FR-09:
Independent AI evaluators assess debate performance.

FR-10:
The system produces a personalized learning report.

Continue until all meaningful functionality is represented.

NFR categories should include:

- performance
- latency
- availability
- privacy
- security
- scalability
- usability
- browser compatibility
- AI response latency
- transcript accuracy
- reliability

Do not invent unrealistic numerical targets without explaining that they are project targets.

---

# DATA MODELS

Design reasonable entities such as:

User
UserProfile
DebateTopic
DebateRoom
DebateParticipant
DebateSession
TranscriptSegment
DetectedClaim
EvidenceSource
LanguageFeedback
ArgumentFeedback
JudgeEvaluation
ConsensusResult
LearningReport

Include useful fields and relationships.

Use PostgreSQL as the proposed database unless there is a strong reason to choose something else.

---

# API DESIGN

Include representative endpoints such as:

POST /auth/register
POST /auth/login

GET /topics
POST /topics

POST /debates/rooms
POST /debates/rooms/{id}/join
POST /debates/rooms/{id}/start
POST /debates/rooms/{id}/end

WebSocket /debates/{room_id}/audio
WebSocket /debates/{room_id}/transcript

GET /debates/{id}/transcript
GET /debates/{id}/analysis
GET /debates/{id}/report

Do not pretend these endpoints already exist.

Mark them as proposed API design.

---

# AI PIPELINE

Clearly separate deterministic software from AI.

Example:

```text
Audio
 ↓
Speech Recognition
 ↓
Speaker Diarization
 ↓
Transcript Segmentation
 ↓
Claim Detection
 ↓
Evidence Retrieval
 ↓
Evidence Evaluation
 ↓
Language Analysis
 ↓
Argument Analysis
 ↓
Independent Judges
 ↓
Consensus
 ↓
Learning Report
```

Explain which components can operate asynchronously.

Do not send the entire transcript to every agent if unnecessary.

Use targeted segments where possible to reduce cost and latency.

---

# FACT CHECKING

Make this technically realistic.

The system should:

1. Detect potentially factual claims.
2. Decide whether a claim requires verification.
3. Search/retrieve relevant sources.
4. Present retrieved evidence to the evaluation agent.
5. Evaluate whether the evidence supports, contradicts, or does not establish the claim.
6. Display sources.
7. Represent uncertainty.

Possible verdicts:

- Supported
- Partially supported
- Contradicted
- Insufficient evidence
- Not verifiable

Avoid "true/false" as the only possible outcome.

---

# SECURITY AND PRIVACY

This is a voice application.

Discuss:

- microphone permissions
- user consent
- audio storage
- transcript storage
- deletion
- authentication
- authorization
- API key protection
- rate limiting
- WebSocket authentication
- prompt injection from spoken content
- malicious speech attempting to manipulate the AI
- external search content potentially containing prompt injection
- not treating retrieved webpages as trusted instructions

The system should treat user speech and external retrieved content as DATA, not system instructions.

---

# FILE 2 — PROJECT_OVERVIEW.md

Use the original `PROJECT_OVERVIEW.md` as the structural reference.

Keep it concise compared with the specification.

Include:

## Project Overview

A table:

| Project name | Description | Similar existing Apps/Systems |

Explain the project in approximately one strong paragraph.

## Elevator Pitch

Give a short pitch suitable for presenting to the professor.

Something conceptually similar to:

> DebateSpeak is a live spoken-debate platform for English learners. Two users debate a topic in a real-time audio room while AI agents transcribe, analyze English usage, evaluate arguments, investigate factual claims, and produce personalized feedback for improving both spoken English and debate skills.

Improve the wording if needed.

## Core Product Concept

Explain:

Live room
→ speech
→ transcript
→ AI analysis
→ evidence
→ learning feedback.

## Actors

At minimum:

- Learner/Debater
- Moderator/Admin

## Functional Groups

List the 8–10 functional groups.

## Existing Apps / Systems

Include honest comparisons.

At minimum discuss:

- ArguFight
- DebateGuard
- Khaos Live
- one English-learning / speaking platform

Do NOT claim the proposed project has no competitors.

Instead explain what the proposed product combines or emphasizes differently.

Use a comparison table:

| Existing System | Main Focus | Relevant Features | Proposed Difference |

## Differentiation

Emphasize:

1. Live human-to-human spoken debate room.
2. English-learning-first objective.
3. Debate as the learning activity.
4. Combined language + argument + evidence analysis.
5. Personalized post-debate improvement.
6. Optional multi-agent independent evaluation and uncertainty reporting.

Be careful not to claim any of these are individually unprecedented.

---

# FILE 3 — ROADMAP_AND_EXECUTION.md

Use the original `ROADMAP_AND_EXECUTION.md` as the structural and detail-level reference.

However, adapt the roadmap to a WEB APPLICATION rather than CLI/gateway software.

Use an approximately 8-week academic sprint.

Suggested structure:

```text
Week 1–2: Foundation & Authentication
Week 3–4: Live Debate Room
Week 5–6: AI Analysis Pipeline
Week 7: Learning Dashboard & Reports
Week 8: Testing, Integration & Demo
```

You may improve this breakdown.

---

# SPRINT 1 — FOUNDATION

Goal:

Working web application with:

- authentication
- user profiles
- database
- topic selection
- basic dashboard
- room creation/joining

Deliverables.

Acceptance criteria.

Milestone.

---

# SPRINT 2 — LIVE DEBATE ROOM

Goal:

Two users can enter the same room and communicate using microphones.

Implement:

- WebRTC or LiveKit
- signaling
- room state
- participant state
- microphone controls
- mute/unmute
- connection status
- debate timer
- start/end debate

Acceptance criteria should be testable.

Example:

"Two authenticated users can join the same room from separate browser windows and exchange audio."

---

# SPRINT 3 — TRANSCRIPTION + AI ANALYSIS

Implement:

- speech-to-text
- speaker identification
- transcript streaming
- transcript persistence
- claim detection
- language analysis
- argument analysis
- fact-checking pipeline

Do not make every AI analysis synchronous.

Explain where asynchronous processing is preferable.

---

# SPRINT 4 — LEARNING REPORT + FINALIZATION

Implement:

- debate summary
- English score
- argument score
- evidence feedback
- personalized recommendations
- history
- progress tracking
- UI polish
- testing
- deployment
- final presentation/demo

---

# TESTING PLAN

Include:

## Unit Testing

Examples:

- authentication validation
- scoring calculations
- transcript segmentation
- claim extraction parsing
- database operations

## Integration Testing

Examples:

- room creation → join → debate → end
- transcript → AI analysis
- claim → search → evidence evaluation
- analysis → report

## Real-Time Testing

Test:

- two users
- reconnect
- microphone permission denied
- network interruption
- one participant leaves
- duplicate WebSocket messages
- delayed transcription

## AI Testing

Evaluate:

- grammar feedback usefulness
- claim detection precision
- evidence relevance
- judge consistency
- hallucination handling

## User Testing

Potential participants:

- English learners
- students

Measure:

- ease of joining a debate
- usefulness of feedback
- report clarity
- perceived speaking improvement
- willingness to use again

Do not invent results. Define experiments and metrics only.

---

# ACCEPTANCE CRITERIA

Every major sprint must contain measurable acceptance criteria.

Examples:

AC-1:
Two users can create and join a debate room.

AC-2:
Audio is transmitted between both participants.

AC-3:
Transcript segments identify the correct speaker.

AC-4:
The system generates language feedback from the transcript.

AC-5:
At least one factual claim is linked to retrieved evidence.

AC-6:
The final report combines language and debate analysis.

AC-7:
A user can review previous debates.

---

# RISK REGISTER

Include risks such as:

| Risk | Likelihood | Impact | Mitigation |

Potential risks:

- WebRTC complexity
- speech recognition latency
- poor transcript accuracy
- speaker diarization errors
- LLM hallucination
- fact-checking search quality
- API cost
- API rate limits
- AI response latency
- privacy concerns with voice recordings
- browser microphone permissions
- unstable network
- scope becoming too large
- team unfamiliarity with real-time systems

Be realistic.

For a student project, explicitly identify which features are MVP and which are stretch goals.

---

# MVP BOUNDARY

This is VERY IMPORTANT.

Do not design an impossible semester project.

The MVP should be:

1. Login
2. Topic selection
3. Create/join room
4. Two-person live audio
5. Speech-to-text
6. Transcript
7. English analysis
8. Argument analysis
9. Basic fact checking
10. Final learning report

Stretch goals:

- live video
- advanced pronunciation scoring
- multiple simultaneous AI judges
- tournaments
- rankings/ELO
- audience mode
- advanced real-time fact-check overlays
- teacher dashboard
- sophisticated CEFR progression model

Clearly label these as stretch goals.

---

# IMPLEMENTATION GUIDANCE

The documentation should recommend using existing libraries/services rather than implementing difficult infrastructure from scratch.

Potential technologies:

Frontend:
- Next.js / React
- TypeScript
- Tailwind CSS

Backend:
- FastAPI or Node.js

Database:
- PostgreSQL

Realtime:
- WebRTC
- LiveKit as a possible managed/open-source WebRTC layer

Speech:
- Whisper / faster-whisper / appropriate hosted speech API

AI:
- OpenAI-compatible LLM APIs or another configurable provider

TTS:
- browser SpeechSynthesis or external TTS API

Do not lock the entire project to one vendor unnecessarily.

Use adapter interfaces where practical.

---

# DOCUMENT STYLE

The three new files should resemble the supplied AI-Combine documents in:

- technical depth
- structured headings
- tables
- IDs
- acceptance criteria
- architecture diagrams
- data models
- implementation details
- testing methodology
- roadmap
- risk analysis

The old files are detailed engineering documents, not short project proposals. Preserve that level of seriousness.

However:

**Do not blindly copy AI-Combine's content.**

Replace concepts such as:

- Red Agent
- Blue Agent
- Sandbox Oracle
- AST probing
- adversarial testing
- CLI
- code hardening
- provider gateway
- token savings

with appropriate concepts for DebateSpeak.

The new equivalent architecture should be centered around:

- Live Debate Room
- Audio/Realtime Layer
- Speech Recognition
- Transcript Processor
- Language Coach
- Argument Coach
- Fact Investigator
- Evidence Evaluator
- Independent Judges
- Consensus Engine
- Learning Report Generator

---

# ARCHITECTURE DIAGRAM

Include at least one clear ASCII architecture diagram similar in detail to the original AI-Combine specification.

For example:

```text
                 ┌───────────────────────┐
                 │   Learner A           │
                 │   Browser + Mic       │
                 └───────────┬───────────┘
                             │
                             │ WebRTC
                             │
                 ┌───────────▼───────────┐
                 │     Debate Room       │
                 │ WebRTC / LiveKit      │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Speech Recognition    │
                 │ + Speaker Diarization│
                 └───────────┬───────────┘
                             │
                         Transcript
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ Language   │ │ Argument   │ │ Fact       │
       │ Coach      │ │ Coach      │ │ Investigator│
       └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                   ┌────────────────┐
                   │ AI Judges /    │
                   │ Consensus      │
                   └───────┬────────┘
                           ▼
                   ┌────────────────┐
                   │ Learning Report│
                   └────────────────┘
```

Improve it where appropriate.

---

# OUTPUT REQUIREMENTS

Create the following files in the project workspace:

`DEBATESPEAK_SPEC.md`

`PROJECT_OVERVIEW.md`

`ROADMAP_AND_EXECUTION.md`

Do not create unnecessary additional documentation files.

After creating them:

1. Read each file back.
2. Check that the three files agree with each other.
3. Check that functional requirements match the roadmap.
4. Check that actors match the functional groups.
5. Check that the architecture supports the requirements.
6. Check that MVP scope is realistic for a student team.
7. Check that no unsupported "unique" or "first-ever" claims remain.
8. Check that the competitor comparison is honest.
9. Check that the project is clearly a web application.
10. Check that the AI component has meaningful practical value.
11. Check that the live room is clearly distinguished from simple voice-input-to-text debate systems.
12. Check for contradictions or leftover AI-Combine terminology.

If you find contradictions, fix them before finishing.

Do not implement the actual application yet.

The task is ONLY to produce these three high-quality Markdown planning/specification documents.

At the end, provide a concise summary of:

- files created
- proposed tech stack
- MVP scope
- main differentiator
- biggest technical risk
- biggest scope risk