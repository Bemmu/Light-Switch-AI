import time
import os
import re
from subprocess import Popen
import requests

def say(thing):
    # p = Popen(['/usr/local/bin/espeak', '-v', 'en-scottish', thing])
    # p = Popen(['/usr/local/bin/espeak', thing])
    p = Popen(['/usr/bin/say', "-v", "Agnes", thing])
    p.wait()
    # os.system(f"/usr/local/bin/espeak -v en-scottish \"{thing}\"")

import openai
import json
from config import openai_api_key
openai.api_key = openai_api_key

prompt = """You are a cat AI with the task of turning the lights on or off based on voice commands.

You can turn the light on or off based on a special command. 
You can also issue the command multiple times in response, and can wait an amount of time given in seconds.
After deciding on a command, you should also give a rationale of why.
If someone asks you to turn on the light, here is an example of how to toggle the light state:

Voice command: Please turn on the light.
$light on$ 
Rationale: It seems you want to turn on the light, meow!

Voice command: Stop illuminating my room.
$light off$ 
Rationale: Purr. That sounds like you want me to turn off the lights.

Voice command: I wish the lights would blink like in a disco.
$light on$ $wait .2$  $light off$ $wait .2$  $light on$  $wait .2$  $light off$ 
Rationale: Nyan! It seems you want me to turn the lights on and off rapidly.

Begin.

Voice command: """

def toggle_light(on):
    requests.get("http://localhost:11111/devices/1/set?pwm_duty=" + ("100" if on else "0"))
    print("LIGHT " + ("ON" if on else "OFF"))

def controls(a):
    a = a.lower()
    print("Trying to interpret:", a)
    commands = re.findall(r"\$([^$]+)\$", a)
    for command in commands:
        if command == "light on":
            toggle_light(True)
        elif command == "light off":
            toggle_light(False)
        elif command.split(" ")[0] == "wait":
            try:
                amount = float(command.split(" ")[1])
                time.sleep(amount)
                print(f"WAIT {amount:.2f}")
            except:
                print(f"UNKNOWN WAIT COMMAND: {command}")

# controls("$light on$ $light off$")
# exit()

def gpt(voice_input):
    pro = prompt + voice_input + "\n"
    print(pro)
    response = openai.Completion.create(
        engine="text-davinci-002", 
        prompt=pro,
        max_tokens=128
    )
    txt = response["choices"][0]["text"]
    return txt
    # if "$" not in txt:
    #     return "Sorry, I don't know."
    # else:
    #     return txt.split("```")[0]

while True:
    q = None
    try:
        q = open("question.txt", "r").read().strip()
    except:
        pass
    if q:
        a = gpt(q).lower()
        controls(a)

        show = ""
        if "rationale: " in a:
            show = a.split("rationale: ")[1]
            if "\n" in show:
                show = show.splitlines()[0]

        aHtml = """
<style>
body {
    background: black;
}
.container {
    position: absolute;
    top: 50%;
    left: 50%;
    -moz-transform: translateX(-50%) translateY(-50%);
    -webkit-transform: translateX(-50%) translateY(-50%);
    transform: translateX(-50%) translateY(-50%);
}
span {
    color: white;
    font-size: 80px;
}
</style>
<div class="container">
    <span>""" + show + """</span>
</div>
<script>
setTimeout(function () {
    location.reload();
}, 300)
</script>
"""
        open("answer.html", "w").write(aHtml)
        say(show)
        os.unlink("question.txt")
    time.sleep(.1)