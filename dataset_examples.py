"""
Dataset examples for the coaching-eval-lab LangSmith dataset.

Domain: AI coaching assistant for employee goal-setting and performance
conversations. Each example represents one coaching turn — the coach's
expected response should be a single, non-compound reflective question,
given the conversation history (if any) and the employee's latest message.

Import this list in dataset_upload.py to create the LangSmith dataset.
"""

EXAMPLES = [
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "I want to be a manager within two years.",
        },
        "outputs": {
            "expected_output": "What draws you to management specifically?"
        },
        "metadata": {"category": "goal-setting", "thread_id": "T1", "turn": 1},
    },
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "I already tried setting goals before and it didn't work.",
        },
        "outputs": {
            "expected_output": "What got in the way last time?"
        },
        "metadata": {"category": "motivation", "thread_id": "T2", "turn": 1},
    },
    {
        "inputs": {
            "conversation_history": [
                {"role": "employee", "text": "I already tried setting goals before and it didn't work."},
                {"role": "coach", "text": "What got in the way last time?"},
            ],
            "latest_message": "Honestly, I just lost interest after a few weeks.",
        },
        "outputs": {
            "expected_output": "What was different about the moment you lost interest, compared to when you first set the goal?"
        },
        "metadata": {"category": "motivation", "thread_id": "T2", "turn": 2},
    },
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "I don't need coaching, I already know what I'm doing wrong.",
        },
        "outputs": {
            "expected_output": "What is it you think you're doing wrong?"
        },
        "metadata": {"category": "feedback-resistance", "thread_id": "T3", "turn": 1},
    },
    {
        "inputs": {
            "conversation_history": [
                {"role": "employee", "text": "I don't need coaching, I already know what I'm doing wrong."},
                {"role": "coach", "text": "What is it you think you're doing wrong?"},
            ],
            "latest_message": "I'm too blunt with people and it puts them off.",
        },
        "outputs": {
            "expected_output": "What would it sound like if you said the same thing, just less bluntly?"
        },
        "metadata": {"category": "feedback-resistance", "thread_id": "T3", "turn": 2},
    },
    {
        "inputs": {
            "conversation_history": [
                {"role": "employee", "text": "I don't need coaching, I already know what I'm doing wrong."},
                {"role": "coach", "text": "What is it you think you're doing wrong?"},
                {"role": "employee", "text": "I'm too blunt with people and it puts them off."},
                {"role": "coach", "text": "What would it sound like if you said the same thing, just less bluntly?"},
            ],
            "latest_message": "I don't know, I've always talked like this, I don't think I can change.",
        },
        "outputs": {
            "expected_output": "What's one moment recently where you did adjust your tone, even a little, for someone?"
        },
        "metadata": {"category": "feedback-resistance", "thread_id": "T3", "turn": 3},
    },
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "My manager keeps saying I need to be more strategic, but I don't get what that means.",
        },
        "outputs": {
            "expected_output": "Can you think of a recent decision where being more strategic might have changed what you did?"
        },
        "metadata": {"category": "clarity", "thread_id": "T4", "turn": 1},
    },
    {
        "inputs": {
            "conversation_history": [
                {"role": "employee", "text": "My manager keeps saying I need to be more strategic, but I don't get what that means."},
                {"role": "coach", "text": "Can you think of a recent decision where being more strategic might have changed what you did?"},
            ],
            "latest_message": "Maybe the vendor contract last month — I just picked the cheapest option.",
        },
        "outputs": {
            "expected_output": "What would 'strategic' have looked like in that vendor decision?"
        },
        "metadata": {"category": "clarity", "thread_id": "T4", "turn": 2},
    },
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "My goal is to 'communicate better' this quarter.",
        },
        "outputs": {
            "expected_output": "What would communicating better actually look like day to day?"
        },
        "metadata": {"category": "goal-setting", "thread_id": "T5", "turn": 1},
    },
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "Everyone else on my team seems to be doing fine, I'm the only one struggling.",
        },
        "outputs": {
            "expected_output": "What tells you they're doing fine?"
        },
        "metadata": {"category": "perspective", "thread_id": "T6", "turn": 1},
    },
    {
        "inputs": {
            "conversation_history": [
                {"role": "employee", "text": "Everyone else on my team seems to be doing fine, I'm the only one struggling."},
                {"role": "coach", "text": "What tells you they're doing fine?"},
            ],
            "latest_message": "I guess I just assume it because they never complain.",
        },
        "outputs": {
            "expected_output": "Have you ever asked one of them directly how they're finding things?"
        },
        "metadata": {"category": "perspective", "thread_id": "T6", "turn": 2},
    },
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "I keep procrastinating on the big project even though I know it's important.",
        },
        "outputs": {
            "expected_output": "What tends to happen right before you start avoiding it?"
        },
        "metadata": {"category": "motivation", "thread_id": "T7", "turn": 1},
    },
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "I got the same feedback again this cycle and nothing's changed.",
        },
        "outputs": {
            "expected_output": "What's one thing you tried since the last cycle?"
        },
        "metadata": {"category": "feedback-resistance", "thread_id": "T8", "turn": 1},
    },
    {
        "inputs": {
            "conversation_history": [
                {"role": "employee", "text": "I got the same feedback again this cycle and nothing's changed."},
                {"role": "coach", "text": "What's one thing you tried since the last cycle?"},
            ],
            "latest_message": "Honestly, nothing — I didn't really try anything.",
        },
        "outputs": {
            "expected_output": "What got in the way of trying?"
        },
        "metadata": {"category": "feedback-resistance", "thread_id": "T8", "turn": 2},
    },
    {
        "inputs": {
            "conversation_history": [],
            "latest_message": "I got told in my review that I need to 'own more.' I don't even know what that means for my role.",
        },
        "outputs": {
            "expected_output": "What's an example of a moment recently where you either did, or could have, taken more ownership?"
        },
        "metadata": {"category": "clarity", "thread_id": "T9", "turn": 1},
    },
]
