import os
import dotenv
dotenv.load_dotenv()
import copy
import json
from typing import Union
from cerebras.cloud.sdk import Cerebras
from cerebras.cloud.sdk.types import chat as cerebras_types

client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY"),  # This is the default and can be omitted
)

prompt_bases = [
    """
    You will generate a script for a scene of a play about the given topic in the given language in the given world in markdown.\n
    Your generated content should be ORIGINAL (DIFFERENT from previous plots), but in the same world
    Use ### Heading 3 for the names of scenes\n
    Use **bolding** for the names of characters the FIRST (and only the first) time they appear\n
    Use ALL CAPS for character names EVERY time they appear\n
    Use ALL CAPS for a character name followed by a colon and then their dialogue for character dialogue\n
    Use _italics_ for stage directions.\n
    Each line of dialogue and each stage direction should be on its own line\n
    Example Snippet of a play (you will generate a full play in the given language, which may not be english, and on a different topic, this is just an example of formatting):\n
    ### Scene 1: The Call to Adventure\n
    _(A small village. **ALICE** is sitting by a fire.)_\n
    ALICE: I wish something exciting would happen.\n
    _(Suddenly, a mysterious figure, **THE STRANGER**, enters.)_\n
    THE STRANGER: Greetings, Alice. Your adventure awaits!\n
    ALICE: Who are you? What adventure?\n
    ...(scene continues, this is just a snippet)\n
    Respond with ONLY the scene that continues the current play (the CURRENT play consists of the text IN "Current Content") in the format described above, do not include any other text. Include AT LEAST 20 lines of dialogue and stage directions.\n
    START your response by first adding a summary of the play, focusing on what you plan to write about in the current scene (including characterization and plot) and potential directions for the story after this scene, enclosed in <info></info> tags (each of the opening and closing info tags should receive their own line).\n
    IF there are currently no scenes IN "Current Content", please begin the play with the title of the play (in # heading 1)\n
    THEN, add ONE scene that continues the current play.\n
    NEXT, please write a brief summary enclosed in <summary></summary> tags (each of the opening and closing summary tags should receive their own line) of the scene you just wrote\n
    FINALLY, IF you reach a conclusion to the ENTIRE play after this scene, end it with a line saying ### THE END. (in the language given). Then, in a new line, write <end>\n
    OTHERWISE, end the scene with a NEWLINE after the last line of dialogue or stage directions of the CURRENT scene.\n
    DO NOT include the name of the next scene. Note that a good play should have around 5 scenes.\n
    """,
    """
    You will generate a short story about the given topic in the given language in markdown.\n
    Your generated content should be ORIGINAL (DIFFERENT from previous plots), but in the same world
    Use # Heading 1 for the name of the story\n
    Respond with ONLY the story, do not include any other text. An example of a story in terms of length, plot complexity, and characterization is The Gift of the Magi.\n
    (Note: Do NOT use this as a style or plot reference unless it would fit the topic; use this example as a reference for how complex your plot and characters should be).\n
    Please BEGIN by first adding a summary of the story, focusing on what you plan to write about (separate into Exposition, Inciting Incident, Rising Action, Climax, Falling Action, Resolution) (including characterization and plot) and potential directions for the story, enclosed in <info></info> tags (each of the opening and closing info tags should receive their own line)\n
    THEN, write the story, based on the given guidelines.\n
    AFTER you finish writing the story, please write a brief summary enclosed in <summary></summary> tags (each of the opening and closing summary tags should receive their own line) of the story you just wrote\n
    END the story with a final line saying ### THE END. (in the language given). Then, in a new line, write <end>\n
    Note that good stories should have highly descriptive language (including literary and rhetorical devices), and be AT LEAST 1000 words long.\n
    """
]

def get_full_prompt(prompt_base, topic, language, world, current_content):
    return prompt_base + f"Topic: {topic}\nLanguage: {language}\nWorld: {world}\nCurrent Content:\n" + current_content + "\nTo repeat for clarity:\n" +prompt_base

def get_response(prompt):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="qwen-3-235b-a22b-instruct-2507",
    )
    return response

def get_text(content):
    lines = content.split("\n")
    in_info = False
    in_summary = False
    filtered_lines = []
    for line in lines:
        if line.startswith("<info>"):
            in_info = True
        elif line.startswith("</info>"):
            in_info = False
        elif line.startswith("<summary>"):
            in_summary = True
        elif line.startswith("</summary>"):
            in_summary = False
        elif line.startswith("<end>"):
            break
        elif not in_info and not in_summary:
            filtered_lines.append(line)
    return "\n".join(filtered_lines).strip()

def get_info(content):
    lines = content.split("\n")
    in_info = False
    info_lines = []
    for line in lines:
        if line.startswith("<info>"):
            in_info = True
        elif line.startswith("</info>"):
            in_info = False
        elif in_info:
            info_lines.append(line)
    return "\n".join(info_lines).strip()

def get_summary(content):
    lines = content.split("\n")
    in_summary = False
    summary_lines = []
    for line in lines:
        if line.startswith("<summary>"):
            in_summary = True
        elif line.startswith("</summary>"):
            in_summary = False
        elif in_summary:
            summary_lines.append(line)
    return "\n".join(summary_lines).strip()

def generate_content(prompt_base, topic, language, world_file, current_content_idx: Union[int, str] = "new"):
    with open(world_file, "r") as f:
        world = json.load(f)
    if current_content_idx == "new":
        world["backstory"].append("")
        current_content_idx = len(world["backstory"]) - 1

    concise_world = copy.deepcopy(world)
    for i in range(len(world["backstory"])):
        concise_world["backstory"][i] = get_summary(world["backstory"][i])
    concise_world["backstory"][current_content_idx] = ""

    response = get_response(
        get_full_prompt(
            prompt_base, topic, language,
            '{"Description":' + json.dumps(concise_world["description"]) + ', "Previous Plots/Stories":' + json.dumps(concise_world["backstory"]) + '}',
            world["backstory"][current_content_idx] if world["backstory"][current_content_idx] != "" else "<empty>"))
    print(response.usage.total_tokens) # type: ignore
    completion = "\n" + response.choices[0].message.content # type: ignore

    world["backstory"][current_content_idx] += completion
    with open(world_file, "w") as f:
        json.dump(world, f)
    return get_text(completion), completion.endswith("<end>")

def create_new_world(name, description):
    world = {
        "description": description,
        "backstory": [""]
    }
    with open(f"data/{name}.json", "w") as f:
        json.dump(world, f)
    return

def clear_world(name):
    with open(f"data/{name}.json", "r") as f:
        world = json.load(f)
    world["backstory"] = []
    with open(f"data/{name}.json", "w") as f:
        json.dump(world, f)
    return

if __name__ == "__main__":
  completion = ""
  ended = False
  clear_world("world0")
  while True:
    completion, ended = generate_content(prompt_bases[0], "discovering mars", "English", "data/world0.json", "new" if completion == "" else -1)
    with open("output.md", "w") as f:
        f.write(get_text(completion))
    if ended:
        completion = ""