import boto3
import uuid
from config import REGION
from db import prompts_table


# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=REGION)


SEED_PROMPTS = [
    # Ice Breakers
    {"level": "ice", "text": "Are you more of a morning person or a night owl?"},
    {"level": "ice", "text": "What's one app on your phone you can't live without?"},
    {"level": "ice", "text": "What's the last movie or TV show you really enjoyed?"},
    {"level": "ice", "text": "What's your favorite season and why?"},
    {"level": "ice", "text": "Would you rather explore space or the deep ocean?"},
    {"level": "ice", "text": "Do you like working in teams or independently?"},
    {"level": "ice", "text": "What's your ideal way to spend a day off?"},
    {"level": "ice", "text": "What's a small thing that made you smile recently?"},
    {"level": "ice", "text": "What's a nostalgic food from your childhood?"},
    {"level": "ice", "text": "What's a skill you've always wanted to learn?"},
    {"level": "ice", "text": "What's a childhood tradition you still enjoy?"},
    {"level": "ice", "text": "What's a fun fact most people don't know about you?"},
    {"level": "ice", "text": "If you could visit anywhere in the world, where would you go and why?"},
    {"level": "ice", "text": "If your life were a movie genre, what would it be and why?"},
    {"level": "ice", "text": "What's the most spontaneous thing you've ever done?"},

    # Confessions
    {"level": "confess", "text": "What's a hobby you could talk about for hours?"},
    {"level": "confess", "text": "What do you wish others understood about you?"},
    {"level": "confess", "text": "What's a part of your past you've forgiven yourself for?"},
    {"level": "confess", "text": "What's something you wish you could apologize for?"},
    {"level": "confess", "text": "What's a lie you've told that still weighs on you?"},
    {"level": "confess", "text": "What's the hardest truth you've had to accept about yourself?"},
    {"level": "confess", "text": "What's something you're still healing from?"},
    {"level": "confess", "text": "What's your biggest regret so far?"},
    {"level": "confess", "text": "What relationship in your life do you wish had turned out differently?"},
    {"level": "confess", "text": "What part of yourself are you most afraid to show others?"},
    {"level": "confess", "text": "When have you felt the most alone, and what helped you through it?"},
    {"level": "confess", "text": "Have you ever lost someone you loved deeply? What did that teach you?"},
    {"level": "confess", "text": "When was the last time you cried and why?"},
    {"level": "confess", "text": "What's something you've never told anyone before?"},

    # Deep Questions
    {"level": "deep", "text": "How do you define success in your life?"},
    {"level": "deep", "text": "If you had to describe your personal growth in one word, what would it be?"},
    {"level": "deep", "text": "What values are most important to you?"},
    {"level": "deep", "text": "How do you define meaningful relationships?"},
    {"level": "deep", "text": "How do you recharge when you're mentally or emotionally drained?"},
    {"level": "deep", "text": "When do you feel most at peace?"},
    {"level": "deep", "text": "How do you handle disappointment?"},
    {"level": "deep", "text": "What does forgiveness mean to you?"},
    {"level": "deep", "text": "What lesson took you the longest to learn?"},
    {"level": "deep", "text": "What motivates you to keep going during tough times?"},
    {"level": "deep", "text": "What's a fear you've managed to overcome?"},
    {"level": "deep", "text": "Who has had the biggest impact on your life and why?"},
    {"level": "deep", "text": "What does home mean to you?"},
    {"level": "deep", "text": "If you could talk to your past self, what would you say?"},
    {"level": "deep", "text": "What's a moment in life you wish you could relive?"},
    {"level": "deep", "text": "What kind of legacy do you want to leave behind?"},
]


def seed_prompts_data():
    SYSTEM_USER_ID = "ADMIN"
    for prompt in SEED_PROMPTS:
        prompts_table.put_item(Item={
            "prompt_id": str(uuid.uuid4()),
            "text": prompt["text"],
            "level": prompt["level"],
            "user_id": SYSTEM_USER_ID,
            "public": True
        })

    print(f"Seeded {len(SEED_PROMPTS)} prompts to DynamoDB.")
