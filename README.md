# Duolingo 2.0

Duolingo but you actually learn the language

## Inspiration 
Duolingo isn't a language learning app. (Has anyone ever said, "I learned fluent French from duolingo!"?)
Conventional language learning, like memorization, is a pain and doesn't lead to fluency.

One of our developers, with her love for language learning, found an amazing way to learn languages in a FUN way, that improved her skills, made her more confident than she thought she could be.

## What it does
Duolingo 2.0 is how you learn language like a baby. 
It uses the 80%-20% rule (80% familiar + context, 20% new) in fictional novels/stories in a play/movie like script in the target language. 
Depending on the proficiency level of the user, the user can highlight 1 word or a phrase to translate into English!

But that's not all -- 
If the user is super invested in "world" or story setting (ex: Harry Potter, or a forest with talking animals), they can continue reading stories in that world!
Users can pick the genre. They are also able to work with Felix the fox (duo's rival, it eats birds), to come up with their own storyline and watch their plot come to life!

## How we built it
Front end -- Prisha
Backend -- Winston

Website using html & css
backend connected through python --
used Cerebras AI to generate the stories, stored the world building information in a json file.

cursor AI, Chat GPT, Github copilot, and ourselves to code

## Challenges we ran into

Integration --> for a while, we didn't realize that we were outputting a string instead of a json file, and had to dig through the code to find that. 
Design --> The design that was first generated was very tacky. Definitely not inspiring enough to def(eat) Duolingo with Felix the Fox. 
Prompting --> Sometimes the output came in different formats, and we had to be super specific. 
AI coding --> AI does things in very inefficient ways, like copying 40 lines of code just because two lines were different. It was harder to find different sections in our code as well, since we did not technically code all of it. 

## Accomplishments that we're proud of

Integration! This being our first hackathon, none of us have actually coded a fully functioning website before. We also used cursor AI to generate a lot of our code, so it was like debugging a code written by someone else.
Getting the "new story" and "continue" buttons to work! There was error in parsing, since we were converting back and forth between json and string files. 

## What we learned
* AI isn't perfect. We knew this already, but we hoped we were wrong.
* python integration in websites
* prompt engineering (being very, very specific)

## What's next for Duolingo 2.0
Later, they will be able to work with Felix the Fox to change the story IN the middle. Maybe even rewrite scenes they don't like! 
The quiz at the beginning will provide a better test of proficiency level.
It may also include a more interactive section, where users are asked to FORM their OWN sentences using new vocab and grammar -- and there isn't just one correct answer to it.
