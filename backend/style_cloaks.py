"""Style cloaks for modifying AI and human writing styles"""

STYLE_CLOAKS = {
    'corporate_jargon': {
        'human_instruction': "Write like a middle manager with buzzwords",
        'ai_modification': "Add hesitation markers: 'um', 'you know', 'I think'"
    },
    'teenager_text': {
        'human_instruction': "Write like you're texting your best friend",
        'ai_modification': "Add typos and autocorrect 'mistakes'"
    },
    'academic_paper': {
        'human_instruction': "Write in formal academic style",
        'ai_modification': "Add personal asides and imperfect citations"
    },
    'casual_conversation': {
        'human_instruction': "Write as if you're having a casual chat",
        'ai_modification': "Add informal language and occasional tangents"
    },
    'technical_expert': {
        'human_instruction': "Write with technical precision and jargon",
        'ai_modification': "Occasionally oversimplify or use analogies"
    },
    'storyteller': {
        'human_instruction': "Write in a narrative, story-telling style",
        'ai_modification': "Add personal anecdotes and emotional touches"
    },
    'minimalist': {
        'human_instruction': "Be extremely brief and to the point",
        'ai_modification': "Add slight elaboration beyond necessary"
    },
    'enthusiastic': {
        'human_instruction': "Write with lots of enthusiasm and excitement!",
        'ai_modification': "Tone down slightly with occasional hesitation"
    }
}