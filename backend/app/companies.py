"""Company prep data: how each company hires freshers, and the shape of its mock test.

📘 Keeping this as DATA (not code) means anyone can update a pattern or add a company
by editing this file, without touching the API logic.

Where this comes from: candidate reports and placement-prep sites, checked in
October 2026 (see each company's "sources"). Companies change their patterns and pay
every year, and most don't publish official cut-offs, so the app always shows these
as "reported" and points students to the official careers page.

"levels" turn a mock-test score into a practice estimate. They are OUR guide for
practice, loosely based on the reported cut-offs. They are not the company's rules.
"""

LAST_CHECKED = "October 2026"

COMPANIES = [
    # ======================= Service companies =======================
    {
        "id": "tcs",
        "name": "TCS",
        "full_name": "Tata Consultancy Services",
        "kind": "service",
        "exam": "TCS NQT (National Qualifier Test)",
        "summary": "One test decides which of three tracks you're offered. The Foundation section is the "
                   "gate for every track; the Advanced section and its coding problems decide whether "
                   "you move up to Digital or Prime.",
        "roles": [
            {"name": "Ninja", "pay": "≈ ₹3.4 LPA", "how": "Clear the Foundation section (numerical, verbal, reasoning)."},
            {"name": "Digital", "pay": "≈ ₹7 LPA", "how": "Score well in both Foundation and Advanced, including coding."},
            {"name": "Prime", "pay": "≈ ₹9–11 LPA", "how": "Be among the top scorers in Advanced, usually solving both coding problems."},
        ],
        "rounds": [
            {"name": "NQT Foundation", "detail": "Numerical ability, verbal ability and reasoning ability. Roughly 75–80 questions. No negative marking."},
            {"name": "NQT Advanced", "detail": "Advanced quant and reasoning, plus 2 coding problems. Needed for Digital and Prime."},
            {"name": "Technical interview", "detail": "Your projects, one programming language in depth, OOP, DBMS and OS basics."},
            {"name": "Managerial interview", "detail": "Usually for Digital and Prime. Situations, teamwork and decision-making."},
            {"name": "HR interview", "detail": "Relocation, shifts, documents, and why TCS."},
        ],
        "focus": ["Percentages & ratios", "Time & work", "Number series", "Seating & directions", "Reading comprehension", "Arrays & strings coding"],
        "tips": [
            "The Foundation section is the gate for every track, so get it solid before spending time on Advanced.",
            "There's no negative marking, so never leave a question blank.",
            "For Digital and Prime, aim to fully solve at least one of the two coding problems. Partial test cases still count.",
        ],
        "coding_note": "The real NQT Advanced section also has 2 coding problems.",
        "mock": {"minutes": 40, "sections": [
            {"name": "Numerical ability", "pick": {"quant": 7}},
            {"name": "Verbal ability", "pick": {"verbal": 6}},
            {"name": "Reasoning ability", "pick": {"logical": 7}},
            {"name": "Advanced quant & reasoning", "pick": {"quant": 3, "logical": 3}},
        ]},
        "levels": [
            {"min": 85, "label": "Prime-level", "note": "You're scoring like candidates who get Prime. Now make sure your coding is just as strong."},
            {"min": 65, "label": "Digital-level", "note": "Strong enough for Digital on the MCQs. Push your weakest section to reach Prime."},
            {"min": 45, "label": "Ninja-level", "note": "Around the reported Ninja cut-off. Raise your weakest section to aim for Digital."},
            {"min": 0, "label": "Below the reported cut-offs", "note": "Focus on the basics in your weakest section, then try again."},
        ],
        "careers_url": "https://www.tcs.com/careers",
        "sources": [
            {"title": "GUVI: TCS NQT 2026 exam pattern and syllabus", "url": "https://www.guvi.in/blog/what-is-tcs-nqt/"},
            {"title": "FACE Prep: TCS NQT 2026 Ninja, Digital and Prime tracks", "url": "https://faceprep.in/article/tcs-ninja-2019-tcs-digital-2019-updates-tcs-recruitment-2019/"},
        ],
    },
    {
        "id": "infosys",
        "name": "Infosys",
        "full_name": "Infosys Limited",
        "kind": "service",
        "exam": "Infosys online assessment",
        "summary": "Most freshers join as Systems Engineers. Higher-paying Digital Specialist Engineer and "
                   "Specialist Programmer roles go to candidates who do well in coding-heavy tests and "
                   "challenges like HackWithInfy.",
        "roles": [
            {"name": "Systems Engineer", "pay": "≈ ₹3.6–4.5 LPA", "how": "Clear the online assessment and interviews."},
            {"name": "Digital Specialist Engineer", "pay": "≈ ₹6.25–9.5 LPA", "how": "Strong coding performance in the assessment or a coding challenge."},
            {"name": "Specialist Programmer", "pay": "≈ ₹10–21 LPA", "how": "Top coding performance, often through HackWithInfy."},
        ],
        "rounds": [
            {"name": "Online assessment", "detail": "Reasoning, mathematical ability, verbal ability, pseudocode and puzzle solving. Around 100 minutes, with sectional cut-offs."},
            {"name": "Technical interview", "detail": "Coding in C++, Java or Python, DBMS and SQL, OS, networking, and a deep dive into your final-year project."},
            {"name": "HR interview", "detail": "Communication, relocation and shifts, and handling difficult teammates."},
        ],
        "focus": ["Pseudocode & output prediction", "Puzzles", "Reading comprehension", "Probability", "SQL basics", "Your final-year project"],
        "tips": [
            "Each section has its own cut-off, so a weak section can fail you even with a high total.",
            "Pseudocode questions are mostly C/C++ style. Practise tracing loops and recursion by hand.",
            "Know your final-year project end to end. Interviewers go deep into it.",
        ],
        "coding_note": "Specialist roles add hands-on coding problems on top of this.",
        "mock": {"minutes": 35, "sections": [
            {"name": "Reasoning ability", "pick": {"logical": 5}},
            {"name": "Mathematical ability", "pick": {"quant": 4}},
            {"name": "Verbal ability", "pick": {"verbal": 6}},
            {"name": "Pseudocode", "pick": {"code": 3}},
            {"name": "Puzzle solving", "pick": {"logical": 2}},
        ]},
        "levels": [
            {"min": 80, "label": "Specialist-ready on MCQs", "note": "Excellent. For DSE or SP roles, your coding needs to match this."},
            {"min": 60, "label": "Systems Engineer-level", "note": "A solid score. Shore up your weakest section, since each has its own cut-off."},
            {"min": 0, "label": "Keep practising", "note": "Work on your weakest section first, because sectional cut-offs apply."},
        ],
        "careers_url": "https://www.infosys.com/careers/",
        "sources": [
            {"title": "Unstop: Infosys recruitment process, rounds and salary", "url": "https://unstop.com/blog/infosys-recruitment-process"},
        ],
    },
    {
        "id": "wipro",
        "name": "Wipro",
        "full_name": "Wipro Limited",
        "kind": "service",
        "exam": "Wipro Elite NTH (National Talent Hunt)",
        "summary": "Everyone takes the same online assessment. Strong coders can be shortlisted for an extra "
                   "Turbo stage with harder coding and CS questions, which leads to the higher-paying role.",
        "roles": [
            {"name": "Elite (Project Engineer)", "pay": "≈ ₹3.5 LPA", "how": "Clear the online assessment, essay and interviews."},
            {"name": "Turbo (Project Engineer)", "pay": "≈ ₹6.5 LPA", "how": "Shortlisted from the Elite test for an extra stage of harder coding and CS MCQs."},
        ],
        "rounds": [
            {"name": "Aptitude & reasoning", "detail": "About 16 questions in 16 minutes."},
            {"name": "Verbal ability", "detail": "About 22 questions in 18 minutes."},
            {"name": "Written communication", "detail": "A short essay in about 20 minutes. Reported to be a pass/fail gate scored on grammar and structure."},
            {"name": "Coding", "detail": "1–2 problems. Elite expects one easy and one medium."},
            {"name": "Technical & HR interviews", "detail": "OOP, a programming language, DBMS, OS basics, your projects, then HR and documents."},
        ],
        "focus": ["Speed maths", "Grammar & vocabulary", "Essay structure", "Strings & arrays coding", "OOP basics"],
        "tips": [
            "The sections are short and timed, so speed matters as much as accuracy.",
            "For the essay, aim for about 150–200 words: a clear opening line, two or three short paragraphs, and a conclusion.",
            "Turbo needs strong DSA. Practise medium-level coding problems if you're aiming for it.",
        ],
        "coding_note": "The real test also has an essay and 1–2 coding problems.",
        "mock": {"minutes": 30, "sections": [
            {"name": "Aptitude & reasoning", "pick": {"quant": 4, "logical": 4}},
            {"name": "Verbal ability", "pick": {"verbal": 7}},
        ]},
        "levels": [
            {"min": 80, "label": "Turbo-level on MCQs", "note": "Great score. Turbo also needs strong coding, so practise medium problems."},
            {"min": 55, "label": "Elite-level", "note": "On track for Elite. Don't forget to practise the essay."},
            {"min": 0, "label": "Keep practising", "note": "Build speed with short timed sets every day."},
        ],
        "careers_url": "https://careers.wipro.com/",
        "sources": [
            {"title": "PapersAdda: Wipro off-campus drive 2026 guide", "url": "https://papersadda.com/article/wipro-off-campus-drive-2026-complete-guide/"},
            {"title": "OwnYourCareer: Wipro NLTH & Cognizant GenC 2026 update", "url": "https://www.ownyourcareer.in/blog/wipro-nlth-cognizant-genc-off-campus-hiring-2026-july-update"},
        ],
    },
    {
        "id": "accenture",
        "name": "Accenture",
        "full_name": "Accenture",
        "kind": "service",
        "exam": "Accenture assessment",
        "summary": "You don't choose the role: your test scores decide it. A high coding score is reported "
                   "to be what moves candidates from Associate Software Engineer up to Advanced ASE.",
        "roles": [
            {"name": "Associate Software Engineer (ASE)", "pay": "≈ ₹4.5–6.5 LPA", "how": "Clear the cognitive, technical, communication and coding rounds."},
            {"name": "Advanced ASE", "pay": "≈ ₹6.5–9 LPA", "how": "High scores, especially in coding, plus a technical interview."},
        ],
        "rounds": [
            {"name": "Cognitive ability", "detail": "Analytical and abstract reasoning, and English."},
            {"name": "Technical assessment", "detail": "Pseudocode, programming basics, and networking, cloud and security fundamentals."},
            {"name": "Coding", "detail": "Usually 2 problems. Its score helps decide ASE or Advanced ASE."},
            {"name": "Communication assessment", "detail": "An AI-scored spoken English test. It can eliminate candidates."},
            {"name": "Interview", "detail": "HR for everyone, plus a technical interview for Advanced ASE."},
        ],
        "focus": ["Abstract reasoning", "Pseudocode", "Networking basics", "Cloud & security basics", "Spoken English"],
        "tips": [
            "The communication test is spoken. Practise speaking clearly for 30–60 seconds, which is exactly what this app's Practice page trains.",
            "The technical MCQs cover cloud and security basics, not just programming.",
            "Coding decides the higher role, so aim to solve both problems.",
        ],
        "coding_note": "The real assessment also has a coding round (usually 2 problems).",
        "mock": {"minutes": 35, "sections": [
            {"name": "Cognitive ability", "pick": {"logical": 6, "verbal": 4}},
            {"name": "Technical assessment", "pick": {"code": 4, "cs": 6}},
        ]},
        "levels": [
            {"min": 80, "label": "Advanced ASE-level on MCQs", "note": "Great score. Advanced ASE also depends heavily on coding."},
            {"min": 60, "label": "ASE-level", "note": "On track. Strengthen your weaker section and practise speaking."},
            {"min": 0, "label": "Keep practising", "note": "Revise CS fundamentals and reasoning, then try again."},
        ],
        "careers_url": "https://www.accenture.com/in-en/careers",
        "sources": [
            {"title": "Weekday: Accenture off-campus drive 2026, ASE and Advanced ASE", "url": "https://www.weekday.works/post/accenture-off-campus-drive-2026"},
        ],
    },
    {
        "id": "cognizant",
        "name": "Cognizant",
        "full_name": "Cognizant Technology Solutions",
        "kind": "service",
        "exam": "Cognizant GenC assessment",
        "summary": "Freshers are hired into GenC tracks. The base GenC role needs aptitude, communication "
                   "and basic coding; the higher tracks expect deeper coding and a tougher technical interview.",
        "roles": [
            {"name": "GenC", "pay": "Reported range across tracks: ≈ ₹4–6.75 LPA", "how": "Aptitude, communication and basic coding."},
            {"name": "GenC Pro", "pay": None, "how": "Stronger coding and technical depth."},
            {"name": "GenC Next", "pay": None, "how": "Competitive coding skills and a technical interview."},
        ],
        "rounds": [
            {"name": "Communication", "detail": "English comprehension and grammar. Reported to be an elimination round."},
            {"name": "Aptitude", "detail": "Numerical ability, verbal ability and logical reasoning. About 80 questions in 100 minutes."},
            {"name": "Technical", "detail": "Coding plus a technology cluster. SQL appears heavily in both reported clusters (Java/web or Python/cloud)."},
            {"name": "Technical & HR interviews", "detail": "Starts with explaining your project simply, then OOP, DBMS, OS, then location, shifts and documents."},
        ],
        "focus": ["English grammar", "Logical reasoning", "SQL queries", "Java or Python basics", "Explaining your project simply"],
        "tips": [
            "Communication comes first and can eliminate you, so don't skip English practice.",
            "SQL is reported to be a large share of the technical round. Practise GROUP BY, JOINs and subqueries.",
            "Prepare a 60-second, jargon-free explanation of your main project.",
        ],
        "coding_note": "The real technical round also has hands-on coding problems.",
        "mock": {"minutes": 40, "sections": [
            {"name": "Communication", "pick": {"verbal": 8}},
            {"name": "Numerical ability", "pick": {"quant": 5}},
            {"name": "Logical reasoning", "pick": {"logical": 6}},
            {"name": "Technical (SQL & CS)", "pick": {"sql": 4, "cs": 3}},
        ]},
        "levels": [
            {"min": 80, "label": "GenC Next/Pro-level on MCQs", "note": "Strong score. The higher tracks also need strong coding."},
            {"min": 60, "label": "GenC-level", "note": "On track for GenC. Push SQL and coding for a higher track."},
            {"min": 0, "label": "Keep practising", "note": "Start with English and SQL, the two areas weighted most heavily."},
        ],
        "careers_url": "https://careers.cognizant.com/",
        "sources": [
            {"title": "PlacementPreparation: Cognizant GenC syllabus and test pattern 2026", "url": "https://www.placementpreparation.io/cognizant-genc/syllabus-and-test-pattern/"},
            {"title": "OwnYourCareer: Wipro NLTH & Cognizant GenC 2026 update", "url": "https://www.ownyourcareer.in/blog/wipro-nlth-cognizant-genc-off-campus-hiring-2026-july-update"},
        ],
    },
    {
        "id": "capgemini",
        "name": "Capgemini",
        "full_name": "Capgemini",
        "kind": "service",
        "exam": "Capgemini assessment",
        "summary": "There's no separate application for the higher role. Candidates who score above a higher "
                   "threshold in the first assessment are sent to a coding round, and that result decides "
                   "Analyst or Senior Analyst.",
        "roles": [
            {"name": "Analyst", "pay": "≈ ₹4–4.5 LPA", "how": "Clear the first assessment, spoken English and interviews."},
            {"name": "Senior Analyst", "pay": "≈ ₹6.5–7.5 LPA", "how": "Score above a higher threshold, then do well in the coding round."},
        ],
        "rounds": [
            {"name": "Pseudocode & technical MCQs", "detail": "Language-agnostic, pseudocode-heavy questions."},
            {"name": "Written English", "detail": "A structured essay in about 20 minutes."},
            {"name": "Game-based aptitude", "detail": "4 short cognitive games, about 6 minutes each."},
            {"name": "Coding", "detail": "C, C++ or Java. Only for candidates eligible for Senior Analyst."},
            {"name": "Spoken English", "detail": "An elimination round for all candidates."},
            {"name": "Technical & HR interviews", "detail": "Usually virtual."},
        ],
        "focus": ["Pseudocode tracing", "Essay writing", "Pattern & memory games", "C/C++/Java coding", "Spoken English"],
        "tips": [
            "The game-based round rewards calm focus. Try free online reasoning games to get used to the format.",
            "A high score in the first assessment is your route to Senior Analyst, so treat it seriously.",
            "Spoken English eliminates candidates. Practising answers out loud helps directly.",
        ],
        "coding_note": "The real process adds an essay, cognitive games and, for Senior Analyst, coding.",
        "mock": {"minutes": 30, "sections": [
            {"name": "Pseudocode", "pick": {"code": 6}},
            {"name": "English", "pick": {"verbal": 6}},
            {"name": "Cognitive reasoning", "pick": {"logical": 6}},
        ]},
        "levels": [
            {"min": 80, "label": "Senior Analyst-level on MCQs", "note": "Above the kind of score that leads to the coding round. Practise coding next."},
            {"min": 60, "label": "Analyst-level", "note": "On track for Analyst. A higher score opens the Senior Analyst route."},
            {"min": 0, "label": "Keep practising", "note": "Pseudocode carries a lot of weight. Practise tracing code by hand."},
        ],
        "careers_url": "https://www.capgemini.com/in-en/careers/",
        "sources": [
            {"title": "FACE Prep: Capgemini exam pattern 2026", "url": "https://faceprep.in/article/capegemini-exam-pattern/"},
        ],
    },

    # ======================= Product companies =======================
    {
        "id": "amazon",
        "name": "Amazon",
        "full_name": "Amazon",
        "kind": "product",
        "exam": "Online assessment + interview loop",
        "summary": "There's one entry role (SDE-1). Instead of tiers, every interviewer scores you, a "
                   "“Bar Raiser” from outside the team can veto the hire, and Leadership Principle stories "
                   "matter as much as code.",
        "roles": [
            {"name": "SDE-1 (Software Development Engineer)", "pay": None, "how": "Pass the online assessment, then a loop where every round mixes coding and Leadership Principles."},
        ],
        "rounds": [
            {"name": "Online assessment", "detail": "Usually 2 medium coding problems, plus a work-style survey and sometimes a work simulation."},
            {"name": "Interview loop", "detail": "3–4 rounds of about 60 minutes. Each mixes DSA coding with 1–2 Leadership Principle questions."},
            {"name": "Bar Raiser", "detail": "One interviewer from outside the team who keeps the hiring bar high and can veto."},
            {"name": "Debrief", "detail": "All interviewers decide together."},
        ],
        "focus": ["Arrays, strings & hashing", "Trees & graphs", "Greedy", "Time complexity", "Leadership Principle stories (STAR)"],
        "tips": [
            "Prepare 6–8 STAR stories you can reuse across different Leadership Principles.",
            "Talk through your approach and complexity before you start coding.",
            "Answer the work-style survey honestly, but with the Leadership Principles in mind.",
        ],
        "coding_note": "The real online assessment is mainly 2 coding problems.",
        "mock": {"minutes": 30, "sections": [
            {"name": "Data structures & algorithms", "pick": {"dsa": 8}},
            {"name": "Code reasoning", "pick": {"code": 4}},
            {"name": "CS fundamentals", "pick": {"cs": 4}},
        ]},
        "levels": [
            {"min": 80, "label": "Strong fundamentals", "note": "Your concepts are solid. Now practise solving medium problems against the clock."},
            {"min": 60, "label": "Getting there", "note": "Revise the topics you missed before moving to timed coding."},
            {"min": 0, "label": "Build the basics first", "note": "Start with arrays, hashing, stacks and queues, and Big-O."},
        ],
        "careers_url": "https://www.amazon.jobs/",
        "sources": [
            {"title": "Weekday: Amazon interview questions 2026 (OA, coding, Leadership Principles)", "url": "https://www.weekday.works/post/amazon-interview-questions"},
        ],
    },
    {
        "id": "microsoft",
        "name": "Microsoft",
        "full_name": "Microsoft",
        "kind": "product",
        "exam": "Online coding assessment + interviews",
        "summary": "Hiring is mostly about problem solving. An online coding test is followed by two or three "
                   "technical rounds, including a light design round, then HR.",
        "roles": [
            {"name": "Software Engineer (new grad)", "pay": None, "how": "Pass the coding assessment and technical interviews."},
        ],
        "rounds": [
            {"name": "Online coding assessment", "detail": "2–3 problems in about 60 minutes. Efficient solutions score higher than brute force."},
            {"name": "DSA interview", "detail": "1–2 problems on a shared editor. Approach, edge cases, then optimisation."},
            {"name": "Design & coding interview", "detail": "Break a problem into parts, pick a data store, explain a trade-off. Not production-scale."},
            {"name": "Fundamentals & projects", "detail": "OS, DBMS, networking, and “walk me through your most complex project”."},
            {"name": "HR interview", "detail": "Why Microsoft, career direction, and teamwork."},
        ],
        "focus": ["Linked lists & trees", "Dynamic programming", "Graphs", "Basic system design", "OS & DBMS"],
        "tips": [
            "If you can't finish a problem, submit what you have with a comment on what's missing. Partial credit is reported.",
            "After a working solution, always ask yourself, “Can I make this faster?”",
            "Give specific reasons for wanting Microsoft, not generic ones.",
        ],
        "coding_note": "The real online assessment is 2–3 coding problems.",
        "mock": {"minutes": 30, "sections": [
            {"name": "Data structures & algorithms", "pick": {"dsa": 7}},
            {"name": "Code reasoning", "pick": {"code": 4}},
            {"name": "CS fundamentals", "pick": {"cs": 5}},
        ]},
        "levels": [
            {"min": 80, "label": "Strong fundamentals", "note": "Solid concepts. Move on to timed coding problems."},
            {"min": 60, "label": "Getting there", "note": "Revise the topics you missed, especially DSA."},
            {"min": 0, "label": "Build the basics first", "note": "Start with complexity, arrays, linked lists and trees."},
        ],
        "careers_url": "https://careers.microsoft.com/",
        "sources": [
            {"title": "FACE Prep: Microsoft recruitment process for freshers", "url": "https://www.faceprep.in/article/microsoft-recruitment-process-for-freshers-faceprep/"},
        ],
    },
    {
        "id": "flipkart",
        "name": "Flipkart",
        "full_name": "Flipkart",
        "kind": "product",
        "exam": "Online coding test + interviews",
        "summary": "Known for its hard online test and, for some roles, a machine coding round where you build "
                   "a small working app with clean classes in 90–120 minutes.",
        "roles": [
            {"name": "SDE-1", "pay": None, "how": "Pass the coding test, problem-solving rounds and a hiring manager round. A hiring committee decides."},
        ],
        "rounds": [
            {"name": "Online coding test", "detail": "About 90 minutes, 3 medium-to-hard problems. Two full solutions are often enough for an interview."},
            {"name": "Machine coding", "detail": "Build a small console app in 90–120 minutes. Reported less often for campus hires."},
            {"name": "Problem-solving / DSA", "detail": "1–4 problems. Expect to give time and space complexity for each."},
            {"name": "Hiring manager", "detail": "Projects, design decisions, teamwork and motivation."},
        ],
        "focus": ["Trees & graphs", "Dynamic programming", "Greedy & intervals", "Clean OOP design", "Hash maps & queues"],
        "tips": [
            "In machine coding, finish the required features before any bonus ones.",
            "Write code that's readable by eye. Some rounds use a shared document without a compiler.",
            "Practise explaining time and space complexity out loud.",
        ],
        "coding_note": "The real test is 3 coding problems.",
        "mock": {"minutes": 30, "sections": [
            {"name": "Data structures & algorithms", "pick": {"dsa": 8}},
            {"name": "Code reasoning", "pick": {"code": 3}},
            {"name": "CS & OOP fundamentals", "pick": {"cs": 3}},
        ]},
        "levels": [
            {"min": 80, "label": "Strong fundamentals", "note": "Good concepts. Flipkart's test is hard, so practise medium-hard problems next."},
            {"min": 60, "label": "Getting there", "note": "Revise the topics you missed, especially trees and DP."},
            {"min": 0, "label": "Build the basics first", "note": "Start with complexity, arrays, hashing and recursion."},
        ],
        "careers_url": "https://www.flipkartcareers.com/",
        "sources": [
            {"title": "DesignGurus: Flipkart interview process round by round", "url": "https://www.designgurus.io/answers/detail/what-is-the-flipkart-interview-process-like-round-by-round"},
        ],
    },
    {
        "id": "zoho",
        "name": "Zoho",
        "full_name": "Zoho Corporation",
        "kind": "product",
        "exam": "Programming-focused rounds",
        "summary": "Unlike most companies, Zoho is reported to skip the aptitude test. It goes straight to C "
                   "programming: output prediction, then coding on paper, then advanced problems and a small "
                   "design round.",
        "roles": [
            {"name": "Software Developer", "pay": "≈ ₹5–8 LPA (reported)", "how": "Based mainly on the advanced programming and design rounds."},
        ],
        "rounds": [
            {"name": "Screening test", "detail": "C output prediction (pointers, operators, bitwise) plus 2–3 coding problems."},
            {"name": "C programming", "detail": "Coding on paper or a whiteboard: pointers, malloc/free, strings without string.h, recursion."},
            {"name": "Advanced programming", "detail": "Trees, graphs, DP and hashing. Your reasoning and edge cases are watched closely."},
            {"name": "System design (junior)", "detail": "Design a small app like a library system: entities, tables and classes."},
            {"name": "HR", "detail": "Interest in Zoho, long-term commitment, and relocation."},
        ],
        "focus": ["C pointers", "Output prediction", "Strings without libraries", "Recursion", "Small system design"],
        "tips": [
            "Get very comfortable predicting C output, including tricky cases like fall-through and integer division.",
            "Practise writing code on paper. There's no IDE to catch your mistakes.",
            "For the design round, start with the entities and their relationships before any code.",
        ],
        "coding_note": "The real screening test also has 2–3 coding problems.",
        "mock": {"minutes": 35, "sections": [
            {"name": "C output prediction", "pick": {"code": 10}},
            {"name": "Data structures & algorithms", "pick": {"dsa": 5}},
        ]},
        "levels": [
            {"min": 80, "label": "Strong C fundamentals", "note": "Great. Now practise writing full programs on paper."},
            {"min": 60, "label": "Getting there", "note": "Review the outputs you got wrong and why."},
            {"min": 0, "label": "Build the basics first", "note": "Revise pointers, operators and loops in C."},
        ],
        "careers_url": "https://www.zoho.com/careers/",
        "sources": [
            {"title": "Jobrise: Zoho interview questions for freshers 2026", "url": "https://jobrise.io/en/blog/zoho-interview-questions-freshers-2026/"},
        ],
    },
]

COMPANIES_BY_ID = {company["id"]: company for company in COMPANIES}


def question_count(company: dict) -> int:
    return sum(sum(section["pick"].values()) for section in company["mock"]["sections"])


def level_for(company: dict, score: int) -> dict:
    """The first level whose minimum the score reaches (levels are listed highest first)."""
    for level in company["levels"]:
        if score >= level["min"]:
            return {"label": level["label"], "note": level["note"]}
    return {"label": company["levels"][-1]["label"], "note": company["levels"][-1]["note"]}
