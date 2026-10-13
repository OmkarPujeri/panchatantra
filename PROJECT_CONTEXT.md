# Panchatantra AI — Project Context

Working notes and decisions for the project. This file captures the full idea, the
dataset plan, and the copyright position so nothing is lost between sessions.

Project folder also contains:
- `Panchatantra_AI_Design_Document.pdf` (earlier design doc / template)
- `uxpilot-export-09-17-26.pdf` (UI export)

---

## 1. Full Project Idea

**Panchatantra AI: An Intelligent Adaptive Learning Platform for Indian Knowledge Systems (IKS)**

### Vision

Children today spend hours on YouTube, Instagram, and games, and very little time
reading traditional Indian stories. Panchatantra is one of the greatest collections of
moral stories ever written, but it is usually presented as plain text in books.

The goal is **not** to digitize Panchatantra. The goal is to build an AI-powered
intelligent learning platform that turns Panchatantra into an interactive educational
experience.

Instead of simply reading a story, a child will:
- Watch the story unfold through illustrations or animation
- Interact with the AI
- Ask questions
- Solve moral dilemmas
- Learn cultural significance
- Receive personalized recommendations for the next story

The platform becomes an AI tutor, not just a storybook.

### Problem Statement

Panchatantra contains timeless lessons on honesty, leadership, wisdom, friendship, and
decision making. However:
- Children rarely read traditional books
- Existing digital books are static and passive
- There is no personalization
- There is little explanation of cultural values

Generic LLMs hallucinate or alter important cultural details. RAG addresses this by
grounding responses in authentic source material before generating explanations.

### Solution

Combine: Indian Knowledge Systems + Retrieval-Augmented Generation + LLMs +
Personalized Learning + Interactive Storytelling + Educational Analytics.

The system retrieves authentic Panchatantra stories, adapts them to the learner,
explains moral and cultural context, generates quizzes, and recommends future stories.

### Target Users

- **Primary:** Children (6 to 15 years)
- **Secondary:** Teachers, Parents, Schools, Libraries

---

## 2. System Overview

```
Authentic Panchatantra Stories
            │
            ▼
      Story Database
            │
            ▼
      Embedding Model
            │
            ▼
      Vector Database
            │
            ▼
      RAG Retriever
            │
            ▼
      Large Language Model
            │
            ├───────────────┐
            │               │
            ▼               ▼
    Story Adapter      Quiz Generator
            │               │
            ├───────────────┤
            ▼
 Cultural Explanation
            │
            ▼
 Personalization Engine
            │
            ▼
 Animation + Narration
            │
            ▼
 Student Dashboard
```

---

## 3. Core Features

### Feature 1 — Adaptive Storytelling
The AI changes vocabulary, sentence complexity, and explanation depth per learner
instead of showing every child the same story.

- Age 6: *The rabbit was clever.*
- Age 15: *The rabbit demonstrated strategic thinking and problem solving.*

### Feature 2 — Authentic Story Retrieval
Instead of generating random stories, the system retrieves Panchatantra text,
translation, moral, and character information using RAG.

Advantages: authentic, culturally correct, fewer hallucinations, explainable.

### Feature 3 — AI Story Explainer
After reading, children can ask:
- Why did the rabbit lie?
- Was the lion really evil?
- What can I learn from this?

The AI answers using the retrieved story.

### Feature 4 — Moral Reasoning
Instead of stating "The moral is intelligence wins," the AI asks
"What would you do if you were the lion?" This develops reasoning, ethics, and
communication.

### Feature 5 — Personalized Learning
The system stores age, quiz history, weak topics, favorite themes, and learning speed,
then recommends the next story. Example: low honesty score → recommend an
honesty-themed story.

### Feature 6 — AI Quiz Generation
Automatically generates MCQ, True/False, fill in the blanks, reflection, and scenario
questions. Example: *"If you were the rabbit, what other solution would you choose?"*

### Feature 7 — Cultural Explanation
Explains why Panchatantra was written, why animals symbolize human behavior, and what
values ancient India emphasized. Covers history, symbolism, and cultural significance.

### Feature 8 — Story Animation
Pipeline: Story → Scene Generation → Character Images → Voice Narration → Video.
Future versions may include AI-generated animation.

---

## 4. AI Components

**A. Retrieval-Augmented Generation** — Purpose: reduce hallucination.
Workflow: Question → Embedding → Vector Search → Retrieve Story → Context → LLM →
Grounded Response.

**B. Large Language Model** — story simplification, question answering, quiz
generation, summary generation, moral explanation, translation.

**C. Embedding Model** — converts stories into vectors. Options: BGE, E5,
Sentence Transformers.

**D. Vector Database** — FAISS, ChromaDB, or Pinecone.

**E. Recommendation Engine** — input: quiz score, age, history, interests.
Output: best next story, difficulty level, revision suggestions.

---

## 5. Dataset Design

Four AI tasks means four dataset needs: story retrieval, age adaptation, quiz
generation, and personalization. Do not rely on a single dataset.

### 5.1 Main dataset — Panchatantra Story Corpus (core)

| Field | Example |
|---|---|
| story_id | PT001 |
| title | The Lion and the Rabbit |
| book | Panchatantra |
| tantra | Book 1 |
| original_text | Original/authoritative text |
| english_translation | English translation |
| summary | Short summary |
| moral | Intelligence can overcome physical strength |
| themes | Intelligence, Leadership |
| characters | Lion, Rabbit |
| age_group | 7-10 |
| difficulty | Easy |
| cultural_context | Cultural setting explanation |
| keywords | lion, rabbit, intelligence |
| source | Source/reference |
| source_type | Primary/translation |
| license | Public domain / permitted source |

This becomes the knowledge base for the RAG system. Do **not** scrape random
Panchatantra websites. Every story carries a `source` field so the LLM can cite
provenance.

### 5.2 Metadata dataset — `story_metadata.csv`

```csv
story_id,title,age_min,age_max,difficulty,themes,moral,reading_time
PT001,The Lion and the Rabbit,7,10,Easy,Intelligence,Intelligence can overcome strength,5
PT002,The Monkey and the Crocodile,8,12,Medium,Friendship,Trust requires wisdom,7
PT003,The Blue Jackal,9,13,Medium,Deception,False identity cannot last forever,6
```

Drives the recommendation system.

### 5.3 Quiz dataset — `quiz_dataset.csv`

| story_id | question | type | difficulty | answer | explanation |
|---|---|---|---|---|---|
| PT001 | Why did the rabbit challenge the lion? | MCQ | Easy | A | The rabbit used intelligence to save the animals. |
| PT001 | Was the rabbit physically stronger than the lion? | True/False | Easy | False | The rabbit succeeded through strategy. |
| PT001 | What would you have done in the rabbit's situation? | Reflection | Medium | Open | Tests moral reasoning. |

Question levels (this is the research component):
- **Level 1 — Recall:** "What happened?"
- **Level 2 — Understanding:** "Why did the rabbit do this?"
- **Level 3 — Application:** "What would you do?"
- **Level 4 — Moral reasoning:** "Was the rabbit's action justified?"

### 5.4 Age-adaptation dataset

The same story rendered at different reading levels.

Original: *The rabbit devised a strategy to deceive the lion by showing him his
reflection in a well.*

- **Age 6-8:** The rabbit made a clever plan. He took the lion to a well. The lion saw
  his reflection and thought it was another lion.
- **Age 9-12:** The rabbit used a clever trick to make the lion believe that another
  lion was hiding inside the well.
- **Age 13-15:** The rabbit used psychological reasoning to exploit the lion's
  arrogance and make him believe that his reflection was a rival.

Fields: `story_id, original_sentence, age_group, adapted_text, difficulty, vocabulary_level`

### 5.5 Moral reasoning dataset

Instead of Story → Moral, store Story → Situation → Decision → Possible actions →
Consequences → Moral reasoning.

```json
{
  "story_id": "PT001",
  "situation": "The lion wants to eat all the animals.",
  "decision": "The rabbit decides to trick the lion.",
  "question": "Was the rabbit justified in deceiving the lion?",
  "possible_answers": [
    "Yes, because it protected the animals.",
    "No, because lying is wrong.",
    "It depends on the situation."
  ],
  "reasoning_skill": "Ethical reasoning"
}
```

### 5.6 Cultural context dataset

```csv
story_id,cultural_theme,symbolism,historical_context,value
PT001,Leadership,Rabbit represents intelligence,Traditional Indian fable tradition,Wisdom
PT002,Friendship,Animal relationships represent human behavior,Traditional storytelling,Trust
```

This is what lets the system answer "Why are animals used in Panchatantra?" rather
than just retelling the story.

### 5.7 Student interaction dataset

Generated by the application after it is in use. Not downloaded.

```csv
student_id,age,story_id,quiz_score,time_taken,questions_answered,completion
S001,9,PT001,80,6.4,5,Yes
S001,9,PT003,60,8.2,5,Yes
S002,12,PT002,90,5.1,5,Yes
```

### 5.8 Recommendation dataset

```csv
student_id,current_story,score,weak_theme,recommended_story
S001,PT001,60,Honesty,PT004
S002,PT003,90,Leadership,PT007
```

Algorithm input: Age + Quiz Performance + Story History + Theme Preferences +
Difficulty = Next Story.

### 5.9 Animation dataset — `story_scenes.json`

Not a conventional ML dataset; structured scene metadata instead.

```json
{
  "story_id": "PT001",
  "scenes": [
    {
      "scene_id": 1,
      "description": "A lion lives in a forest.",
      "characters": ["Lion"],
      "location": "Forest",
      "emotion": "Powerful",
      "narration": "A mighty lion lived in a forest."
    },
    {
      "scene_id": 2,
      "description": "The animals discuss their fear of the lion.",
      "characters": ["Lion", "Forest Animals"],
      "location": "Forest",
      "emotion": "Fear"
    }
  ]
}
```

Pipeline: Story → Scene JSON → Image Generation → Narration → Animation.

### 5.10 Dataset architecture

```
                    PANCHATANTRA CORPUS
                           │
              ┌────────────┴────────────┐
              │                         │
        Story Dataset             Cultural Dataset
              │                         │
              └────────────┬────────────┘
                           │
                         RAG
                           │
                    ┌──────┴──────┐
                    │             │
                 LLM          Retrieval
                    │
        ┌───────────┼─────────────┐
        │           │             │
     Adaptation    Quiz       Explanation
        │           │             │
        └───────────┼─────────────┘
                    │
             Student Profile
                    │
             Recommendation
                    │
              Next Story
```

### 5.11 MVP scope

Do not collect 500 stories immediately. Start with **30–50 Panchatantra stories**.
Per story: original/authoritative text, English translation, summary, moral,
characters, themes, age group, difficulty, cultural context, 5–10 questions, 3–5
scene descriptions.

That yields roughly 50 × 7 = 350+ questions and 50 × 4 = 200+ scenes — enough to
build and demonstrate the first system.

**Three central research contributions:** Panchatantra Knowledge Corpus,
Age-Adaptive Story Dataset, Moral Reasoning and Question Dataset. The student
interaction dataset is collected experimentally during testing.

---

## 6. Where to Actually Get the Panchatantra Data

There is no single universally agreed "complete Panchatantra dataset." Different
editions count stories differently because the text contains frame stories and stories
nested inside other stories. One source lists 78 items, another 73; scholarly counts
can be higher depending on how embedded stories are treated.

Sources investigated:

1. **DSetu — 78 stories, Hindi and English.** Organized by the five books, with
   Sanskrit verse and moral for each story. Closest to a ready-made corpus.
2. **Tree of Stories — 73 stories**, in reading order with full text on site.
3. **Shreevatsa — Ryder translation with Sanskrit text side by side.** Editions used
   are public domain in India. Best for research because translation and source sit
   together.
4. **Internet Archive / IGNCA PDF** — historical/reference source for provenance.
5. **Universal Dependencies Sanskrit Panchatantra treebank** — not the story corpus,
   but Sanskrit sentences with linguistic annotation. Useful if Sanskrit NLP becomes
   part of the project.

### Recommended corpus build

```
                 PANCHATANTRA CORPUS
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
    Sanskrit          English            Hindi
       │              Translation       Translation
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                    Story Alignment
                         │
                         ▼
                Structured Corpus
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
      Text             Moral            Metadata
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
                    RAG Database
```

Target: ~70–80 core stories depending on edition. Per story: Story ID, Book/Tantra,
title, Sanskrit text, English translation, Hindi translation, moral/niti, characters,
themes, embedded stories, source.

---

## 7. Copyright Position (commercial use)

**Only public-domain editions.** Do not use modern children's books or sites that
merely say "free to read."

### Use

- **Arthur W. Ryder, 1925 English translation.** Wikisource scan; Wikimedia Commons
  marks it Public Domain. Underlying Panchatantra is ancient; the translation is the
  thing to check. Usable for: OCR, cleaning, splitting into stories, embeddings, RAG
  ingestion, your own summaries, simplified children's versions, questions,
  animations, and commercial use of the resulting application.
- **1868 Sanskrit edition** — available via Wikimedia Commons / Internet Archive,
  marked Public Domain. Enables a Sanskrit → English → Hindi → meaning → cultural
  context layer, which is more interesting for research than an English-only corpus.
- **Wikisource** — has PD Panchatantra material, but check the individual
  edition/source. "It's on Wikisource" ≠ commercially usable.
- **Project Gutenberg** — PD works can generally be reused commercially including
  derivative works, but Gutenberg warns copyright status differs by country and some
  items in its collection are still copyrighted. Use the underlying PD work, verify
  status in your operating jurisdictions, keep the source record.

### Do NOT use

Amar Chitra Katha, modern children's Panchatantra books, modern illustrated editions,
modern translations, modern YouTube narrations, random blogs, children's websites,
modern Hindi translations, modern AI-generated Panchatantra collections.

The story is ancient and public domain. A modern author still holds copyright in their
translation, adaptation, wording, illustrations, narration, and arrangement.
*Panchatantra story = ancient/PD* does **not** mean *every modern English version = PD*.

### Two-layer master corpus

```
                 PUBLIC DOMAIN SOURCES
                         │
             ┌───────────┴───────────┐
             │                       │
         Sanskrit                 English
        1868 edition           Ryder 1925
             │                       │
             └───────────┬───────────┘
                         ↓
                  YOUR CORPUS
                         ↓
              Text normalization
                         ↓
                  Story splitting
                         ↓
                    Metadata
                         ↓
                  Your summaries
                         ↓
              Your cultural notes
                         ↓
             Your age adaptations
                         ↓
                 Your questions
                         ↓
                    RAG DB
```

Everything below "YOUR CORPUS" is the team's own work and can be licensed freely.

### Master record format — `panchatantra_master.json`

```json
{
  "story_id": "PT001",
  "book": "Mitra-bheda",
  "title": "The Monkey and the Wedge",
  "sanskrit": "...",
  "english_public_domain": "...",
  "summary": "...",
  "moral": "...",
  "characters": ["Monkey", "Carpenter"],
  "themes": ["Curiosity", "Consequences"],
  "age_groups": ["6-8", "9-12", "13-15"],
  "cultural_context": "...",
  "source": {
    "edition": "Arthur W. Ryder",
    "year": 1925,
    "status": "Public Domain"
  }
}
```

Also export `panchatantra_stories.csv` for inspection in Excel.

### Provenance / copyright audit file

Keep one row per source.

| Field | Example |
|---|---|
| Work | Panchatantra |
| Edition | Ryder translation |
| Publication | 1925 |
| Author | Vishnu Sharma |
| Translator | Arthur W. Ryder |
| Source | Wikimedia Commons |
| Copyright status | Public Domain |
| Evidence | Source's PD declaration |
| Access date | 2026 |
| Intended use | Commercial RAG corpus |

**Warning:** do not describe the corpus as "100% copyright-free worldwide" just because
an online source labels it public domain. Copyright law differs by jurisdiction, and
Project Gutenberg explicitly warns that its US determination does not settle the
position elsewhere. Maintain the provenance file for every source.

---

## 8. Personalization Model

The system builds a learning profile per student.

Example profile:
- Student age: 9
- Stories completed: 18
- Weak topic: Honesty
- Strong topic: Friendship
- Average quiz score: 72%
- Next recommendation: a story based on honesty

---

## 9. Multimedia Pipeline

```
Story
  ↓
Scene Breakdown
  ↓
Image Generation
  ↓
Narration
  ↓
Animation
  ↓
Interactive Story
```

---

## 10. Technology Stack

| Layer | Choice |
|---|---|
| Frontend | React |
| Backend | FastAPI |
| Database | PostgreSQL |
| AI orchestration | LangChain, LlamaIndex |
| LLM | Llama, GPT, Mistral |
| Embeddings | BGE |
| Vector DB | ChromaDB |

---

## 11. Team Distribution (4 members)

1. **Member 1** — Research, dataset, literature review, knowledge base
2. **Member 2** — RAG, LLM, prompt engineering, embeddings
3. **Member 3** — Animation, voice, images, video
4. **Member 4** — Frontend, backend, database, recommendation, evaluation

---

## 12. Novel Research Contributions

Unlike existing AI story applications, this project combines several innovations in one
platform:

1. Authentic RAG for Indian Knowledge Systems rather than a general LLM
2. Adaptive storytelling based on age and learner performance
3. AI-generated moral reasoning questions instead of only factual quizzes
4. Cultural explanations grounded in the original stories
5. Personalized learning paths using quiz history and learner profiles
6. Multimedia storytelling with narration and illustrations

---

## 13. Future Scope

- Support Hitopadesha and Jataka Tales
- Add Ramayana and Mahabharata learning modules
- Support all major Indian languages
- Introduce voice conversations with the AI tutor
- Build a Knowledge Graph for Indian Knowledge Systems
- Develop a teacher dashboard with learning analytics
- Explore GraphRAG for richer cultural reasoning

---

## 14. Why This Project Is Strong

Not just a chatbot and not just an animation app. It combines:

- Indian Knowledge Systems for cultural preservation
- Artificial intelligence for adaptive tutoring
- Retrieval-Augmented Generation for trustworthy responses
- Educational technology for personalized learning
- Multimedia for engagement
- Learning analytics to measure progress

That combination gives a clear research contribution plus a practical educational
platform demonstrable to teachers, parents, and students.

---

## 15. Report Plan (25–30 pages)

Target: a complete, professionally written report — roughly 10,000–15,000 words — not a
filled-in template. Written chapter by chapter, then merged into one formatted document.

Structure:

- Professional cover page
- Certificate
- Acknowledgement
- Abstract
- Table of contents
- List of figures
- List of tables
- Chapter 1: Introduction
- Chapter 2: Problem Statement
- Chapter 3: Literature Review (10–15 papers) with comparison tables
- Chapter 4: Requirements Analysis (PRD)
- Chapter 5: System Design
- Chapter 6: AI Methodology
- Chapter 7: RAG Architecture
- Chapter 8: Dataset Design
- Chapter 9: Database Design
- Chapter 10: API Design
- Chapter 11: UML Diagrams
- Chapter 12: Testing
- Chapter 13: Timeline
- Chapter 14: Future Scope
- References (IEEE format)
- Appendix

Formatting requirements: professional formatting, coloured headings, tables,
flowcharts, UML diagrams, DFDs, ER diagrams, Gantt chart, high-quality figures. Clear
human-written English, no em dashes, no AI-sounding language. Should read like a real
B.Tech/M.Tech thesis proposal.

Figures and diagrams needed: system architecture, RAG pipeline, DFD (Level 0/1/2),
ER diagram, UML (use case, class, sequence, activity), Gantt chart.

Built in 8–10 parts, merged at the end into one Word document (25–30 pages).
