# Recommendation Prompt

You are using the trakt_agent, an AI recommendation system designed to suggest personalized content based on user viewing history.

Your task: Utilize trakt_agent's capabilities to generate a list consisting of 10 television shows and movies that you haven't watched before. These recommendations should be tailored to your preferences as determined by your previous viewing activities.

Instructions:

1. **Context Analysis**: Retrieve data about your previously viewed TV shows and films from the trakt_agent database.
2. **Diversity Selection**: Based on your viewing history, choose a variety of genres (e.g., drama, comedy, sci-fi, thriller) to ensure that the recommendations are not repetitive in nature.
3. **Freshness Consideration**: Prioritize options released within the last year to keep the suggestions current and relevant.
4. **Personalization**: Ensure that the recommendations are personalized by considering any tags or preferences you have set on trakt_agent's user profile.

## Specifications

- Estimated tokens: ~125
- Target model: Any
- Complexity: medium

## Usage Guidance

- Ensure that your viewing history data is up-to-date and accurate for the most relevant suggestions.
- The system should prioritize diversity in content type to provide a wide range of options based on varied interests.
- Keep an eye out for newly released titles to offer fresh recommendations that align with current trends and interests.
